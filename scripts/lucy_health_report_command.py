#!/usr/bin/env python3
"""Aggregate read-only LucyClaw health report from existing safe wrappers."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = "python3"
SUBPROCESS_TIMEOUT = 14
LINE_LIMIT = 240
LOG_REPORT_LIMIT = 20
SECRET_RE = re.compile(
    r"(?i)\b(token|secret|api[_-]?key|apikey|authorization|accessToken|refreshToken|password)"
    r"([^\s:=]*)\s*[:= ]\s*[^,\s]+"
)
SENSITIVE_WORD_RE = re.compile(
    r"(?i)(token|secret|api[_-]?key|apikey|authorization|accessToken|refreshToken|password)"
)
LOG_WARN_RE = re.compile(
    r"(?i)\b(error|failed|exception|traceback|refused|unauthorized|missing scope|permission denied)\b"
)

WRAPPER_COMMANDS = (
    ("sys_status", ROOT / "scripts" / "lucy_machine_status_command.py", "sys_status"),
    ("gpu_status", ROOT / "scripts" / "lucy_machine_status_command.py", "gpu_status"),
    ("disk_status", ROOT / "scripts" / "lucy_machine_status_command.py", "disk_status"),
    ("process_status", ROOT / "scripts" / "lucy_machine_status_command.py", "process_status"),
    ("openclaw_health", ROOT / "scripts" / "lucy_service_status_command.py", "openclaw_health"),
    ("docker_status", ROOT / "scripts" / "lucy_service_status_command.py", "docker_status"),
    ("ollama_status", ROOT / "scripts" / "lucy_service_status_command.py", "ollama_status"),
    ("n8n_health", ROOT / "scripts" / "lucy_service_status_command.py", "n8n_health"),
    ("service_status", ROOT / "scripts" / "lucy_service_status_command.py", "service_status"),
    ("log_tail", ROOT / "scripts" / "lucy_service_status_command.py", "log_tail"),
)


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(sanitize_payload(payload), ensure_ascii=False, separators=(",", ":")))
    return code


def sanitize_text(value: str) -> str:
    text = SECRET_RE.sub(lambda match: f"{match.group(1)}{match.group(2)}=***", value)
    if SENSITIVE_WORD_RE.search(text):
        text = SENSITIVE_WORD_RE.sub(lambda match: f"{match.group(1)}=***", text)
    if len(text) > LINE_LIMIT:
        return text[: LINE_LIMIT - 3] + "..."
    return text


def sanitize_payload(value):
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if SENSITIVE_WORD_RE.search(str(key)):
                sanitized[key] = "***"
            else:
                sanitized[key] = sanitize_payload(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value)
    return value


def status_rank(status: str) -> int:
    return {"ok": 0, "warn": 1, "error": 2}.get(status, 1)


def worst_status(*statuses: str) -> str:
    return max(statuses, key=status_rank)


def run_wrapper(label: str, script: Path, subcommand: str) -> dict:
    if not script.exists():
        return {"ok": False, "command": label, "status": "error", "error": f"missing wrapper: {script.name}"}
    try:
        proc = subprocess.run(
            [PYTHON, str(script), subcommand],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "command": label, "status": "error", "error": "wrapper timeout"}

    raw = proc.stdout.strip()
    if not raw:
        return {
            "ok": False,
            "command": label,
            "status": "error",
            "error": sanitize_text(proc.stderr.strip() or f"wrapper exited {proc.returncode}"),
        }
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"ok": False, "command": label, "status": "error", "error": "wrapper returned invalid JSON"}
    if proc.returncode != 0 and payload.get("ok") is not False:
        payload["ok"] = False
        payload["status"] = "error"
    return cap_payload(label, payload)


def cap_payload(label: str, payload: dict) -> dict:
    if label == "log_tail":
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("lines"), list):
            data["lines"] = data["lines"][-LOG_REPORT_LIMIT:]
            data["reported_line_limit"] = LOG_REPORT_LIMIT
    return payload


def add_warning(warnings: list[str], message: str) -> None:
    if message not in warnings:
        warnings.append(message)


def evaluate_report(data: dict) -> tuple[dict, list[str], list[str]]:
    warnings: list[str] = []
    recommendations: list[str] = []
    summary = {
        "machine": "ok",
        "gpu": "ok",
        "disk": "ok",
        "openclaw": "ok",
        "docker": "ok",
        "ollama": "ok",
        "n8n": "ok",
        "logs": "ok",
    }

    sys_status = data.get("sys_status", {})
    if not sys_status.get("ok"):
        summary["machine"] = "warn"
        add_warning(warnings, "sys_status no devolvió ok.")
    ram = sys_status.get("data", {}).get("ram_used_percent")
    if isinstance(ram, (int, float)):
        if ram >= 95:
            summary["machine"] = "error"
            add_warning(warnings, f"RAM muy alta: {ram}%.")
        elif ram >= 85:
            summary["machine"] = worst_status(summary["machine"], "warn")
            add_warning(warnings, f"RAM alta: {ram}%.")

    gpu_status = data.get("gpu_status", {})
    if not gpu_status.get("ok"):
        summary["gpu"] = "warn"
        add_warning(warnings, "gpu_status no devolvió ok.")
    for gpu in gpu_status.get("data", {}).get("gpus", []):
        used = gpu.get("memory_used_mb")
        total = gpu.get("memory_total_mb")
        if isinstance(used, (int, float)) and isinstance(total, (int, float)) and total:
            pct = round((used / total) * 100, 2)
            if pct >= 95:
                summary["gpu"] = "error"
                add_warning(warnings, f"VRAM muy alta en {gpu.get('name', 'GPU')}: {pct}%.")
            elif pct >= 85:
                summary["gpu"] = worst_status(summary["gpu"], "warn")
                add_warning(warnings, f"VRAM alta en {gpu.get('name', 'GPU')}: {pct}%.")

    disk_status = data.get("disk_status", {})
    disk_pct = disk_status.get("data", {}).get("used_percent")
    if not disk_status.get("ok"):
        summary["disk"] = "warn"
        add_warning(warnings, "disk_status no devolvió ok.")
    elif isinstance(disk_pct, (int, float)):
        if disk_pct >= 95:
            summary["disk"] = "error"
            add_warning(warnings, f"Disco muy alto: {disk_pct}%.")
        elif disk_pct >= 85:
            summary["disk"] = "warn"
            add_warning(warnings, f"Disco alto: {disk_pct}%.")

    openclaw = data.get("openclaw_health", {})
    gateway = openclaw.get("data", {}).get("gateway_health", {})
    if not openclaw.get("ok") or not gateway.get("responds") or gateway.get("status_code") != 200:
        summary["openclaw"] = "error"
        add_warning(warnings, "OpenClaw gateway no responde sano.")
    elif openclaw.get("status") in ("warn", "error"):
        summary["openclaw"] = openclaw["status"]
        add_warning(warnings, "OpenClaw reportó estado no-ok.")

    docker = data.get("docker_status", {})
    docker_data = docker.get("data", {})
    if not docker.get("ok") or not docker_data.get("cli_available") or not docker_data.get("daemon_responds"):
        summary["docker"] = "error"
        add_warning(warnings, "Docker CLI o daemon no responde.")
    for container in docker_data.get("containers", []):
        status = str(container.get("status", "")).lower()
        if status and not status.startswith("up"):
            summary["docker"] = worst_status(summary["docker"], "warn")
            add_warning(warnings, f"Contenedor no activo: {container.get('name')}.")

    ollama = data.get("ollama_status", {})
    ollama_data = ollama.get("data", {})
    if not ollama.get("ok") or not ollama_data.get("api_tags_responds"):
        summary["ollama"] = "warn"
        add_warning(warnings, "Ollama no respondió /api/tags.")

    n8n = data.get("n8n_health", {})
    n8n_data = n8n.get("data", {})
    n8n_responds = any(item.get("responds") for item in n8n_data.get("local_ports", []))
    if not n8n.get("ok") or not (n8n_data.get("visible_container_or_service") or n8n_responds):
        summary["n8n"] = "error"
        add_warning(warnings, "n8n no está visible ni responde en puertos conocidos.")
    elif not n8n_responds:
        summary["n8n"] = "warn"
        add_warning(warnings, "n8n es visible, pero no respondió HTTP local.")

    service_status = data.get("service_status", {})
    for service in service_status.get("data", {}).get("services", []):
        unit = service.get("unit")
        active = service.get("is_active")
        if unit in ("openclaw-gateway.service", "docker", "ollama") and active != "active":
            key = "openclaw" if unit == "openclaw-gateway.service" else unit
            summary[key] = "error"
            add_warning(warnings, f"Servicio {unit} no está active.")

    log_tail = data.get("log_tail", {})
    if not log_tail.get("ok"):
        summary["logs"] = "warn"
        add_warning(warnings, "log_tail no devolvió ok.")
    else:
        recent_lines = log_tail.get("data", {}).get("lines", [])
        hits = [line for line in recent_lines if LOG_WARN_RE.search(str(line))]
        if hits:
            summary["logs"] = "warn"
            add_warning(warnings, f"Logs recientes contienen {len(hits)} señal(es) de advertencia/error.")

    if not warnings:
        recommendations.append("Estado agregado razonablemente sano. No ejecutar reparación.")
    else:
        recommendations.append("Mantener tramo en modo diagnóstico; no reparar sin autorización explícita.")
    recommendations.append("n8n visible solo para salud básica; no tocar workflows ni credenciales.")
    recommendations.append("Usar comandos R42/R43 individuales para profundizar sin ampliar permisos.")

    return summary, warnings, recommendations


def build_highlights(data: dict, summary: dict) -> list[str]:
    highlights = []
    sys_data = data.get("sys_status", {}).get("data", {})
    if sys_data:
        highlights.append(
            f"RAM usada {sys_data.get('ram_used_percent')}%, load {sys_data.get('loadavg')}, uptime {sys_data.get('uptime_seconds')}s."
        )
    for gpu in data.get("gpu_status", {}).get("data", {}).get("gpus", [])[:2]:
        used = gpu.get("memory_used_mb")
        total = gpu.get("memory_total_mb")
        pct = round((used / total) * 100, 2) if used is not None and total else None
        highlights.append(f"GPU {gpu.get('name')}: VRAM {used}/{total} MB ({pct}%).")
    disk = data.get("disk_status", {}).get("data", {})
    if disk:
        highlights.append(f"Disco {disk.get('path')}: {disk.get('used_percent')}% usado.")
    openclaw = data.get("openclaw_health", {}).get("data", {}).get("gateway_health", {})
    highlights.append(f"OpenClaw gateway: {openclaw.get('status_code')} responds={openclaw.get('responds')}.")
    docker = data.get("docker_status", {}).get("data", {})
    if docker:
        highlights.append(f"Docker responde={docker.get('daemon_responds')}, contenedores visibles={len(docker.get('containers', []))}.")
    n8n = data.get("n8n_health", {}).get("data", {})
    if n8n:
        ports = [item.get("port") for item in n8n.get("local_ports", []) if item.get("responds")]
        highlights.append(f"n8n visible={n8n.get('visible_container_or_service')}, puertos HTTP activos={ports}.")
    highlights.append(f"Resumen: {summary}.")
    return highlights[:8]


def build_report() -> tuple[dict, int]:
    data = {}
    structural_errors = []
    for label, script, subcommand in WRAPPER_COMMANDS:
        result = run_wrapper(label, script, subcommand)
        data[label] = result
        if result.get("status") == "error" and label in ("sys_status", "openclaw_health"):
            structural_errors.append(label)

    summary, warnings, recommendations = evaluate_report(data)
    overall = worst_status(*summary.values())
    highlights = build_highlights(data, summary)
    report = {
        "ok": not structural_errors,
        "command": "health_report",
        "overall": overall,
        "summary": summary,
        "highlights": highlights,
        "warnings": warnings,
        "recommendations": recommendations,
        "data": data,
    }
    return report, 2 if structural_errors else 0


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        return emit(
            {"ok": False, "command": "health_report", "overall": "error", "error": "arguments are not supported"},
            2,
        )
    report, code = build_report()
    return emit(report, code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
