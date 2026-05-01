#!/usr/bin/env python3
"""Deterministic read-only service and log status helpers for LucyClaw."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request


ALLOWED_COMMANDS = {
    "openclaw_health",
    "docker_status",
    "ollama_status",
    "n8n_health",
    "service_status",
    "log_tail",
}
SUBPROCESS_TIMEOUT = 10
HTTP_TIMEOUT = 5
LOG_LIMIT = 80
LINE_LIMIT = 240
SERVICE_ALLOWLIST = (
    ("openclaw-gateway.service", "user"),
    ("docker", "system"),
    ("ollama", "system"),
    ("n8n", "system"),
)
SECRET_RE = re.compile(
    r"(?i)\b(token|secret|api[_-]?key|apikey|authorization|accessToken|refreshToken|password)"
    r"([^\s:=]*)\s*[:= ]\s*[^,\s]+"
)
SENSITIVE_WORD_RE = re.compile(
    r"(?i)(token|secret|api[_-]?key|apikey|authorization|accessToken|refreshToken|password)"
)
PORT_MAP_RE = re.compile(r"127\.0\.0\.1:(\d+)->5678/tcp")


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(sanitize_payload(payload), ensure_ascii=False, separators=(",", ":")))
    return code


def emit_error(command: str, message: str, code: int = 2) -> int:
    return emit({"ok": False, "command": command, "error": sanitize_text(message)}, code)


def sanitize_text(value: str) -> str:
    text = SECRET_RE.sub(lambda match: f"{match.group(1)}{match.group(2)}=***", value)
    if SENSITIVE_WORD_RE.search(text):
        text = SENSITIVE_WORD_RE.sub(lambda match: f"{match.group(1)}=***", text)
    text = " ".join(text.split()) if "\n" not in text else text
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


def run_command(args: list[str], timeout: int = SUBPROCESS_TIMEOUT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        shell=False,
    )


def safe_model_snapshot() -> dict | None:
    if shutil.which("openclaw") is None:
        return None

    proc = run_command(["openclaw", "models", "status", "--json"])
    if proc.returncode != 0:
        return {
            "available": False,
            "error": sanitize_text(proc.stderr.strip() or "openclaw models status failed"),
        }

    try:
        model_body = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"available": False, "error": "openclaw models status returned invalid JSON"}

    default_model = model_body.get("default") or model_body.get("defaultModel")
    resolved_default = model_body.get("resolvedDefault")
    current_model = model_body.get("current") or model_body.get("model")

    safe = {
        "available": True,
        "current": current_model,
        "default": default_model,
        "resolved_default": resolved_default,
        "current_available": current_model is not None,
        "default_available": (default_model is not None or resolved_default is not None),
    }
    model_name = current_model or resolved_default or default_model
    if isinstance(model_name, str) and "/" in model_name:
        provider, model = model_name.split("/", 1)
        safe["provider"] = provider
        safe["model"] = model
    return safe


def http_json(url: str) -> dict:
    try:
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            raw = response.read(65536).decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = raw[:200]
            return {"responds": True, "status_code": response.status, "body": body}
    except urllib.error.HTTPError as exc:
        return {"responds": True, "status_code": exc.code, "error": str(exc)}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"responds": False, "error": str(exc)}


def systemctl_status(unit: str, scope: str) -> dict:
    if shutil.which("systemctl") is None:
        return {"unit": unit, "scope": scope, "available": False, "error": "systemctl not available"}

    base = ["systemctl"]
    if scope == "user":
        base.append("--user")

    proc = run_command([*base, "is-active", unit])
    active = proc.stdout.strip() if proc.stdout.strip() else "unknown"
    enabled_proc = run_command([*base, "is-enabled", unit])
    enabled = enabled_proc.stdout.strip() if enabled_proc.stdout.strip() else "unknown"
    show_proc = run_command([*base, "show", unit, "--property=LoadState,ActiveState,SubState,UnitFileState", "--no-pager"])

    props = {}
    if show_proc.returncode == 0:
        for line in show_proc.stdout.splitlines():
            if "=" in line:
                key, val = line.split("=", 1)
                props[key] = sanitize_text(val)

    return {
        "unit": unit,
        "scope": scope,
        "available": proc.returncode in (0, 3) or bool(props),
        "is_active": active,
        "is_enabled": enabled,
        "properties": props,
    }


def docker_containers() -> tuple[list[dict], str | None]:
    if shutil.which("docker") is None:
        return [], "docker CLI not available"
    proc = run_command(
        [
            "docker",
            "ps",
            "--format",
            "{{json .}}",
        ]
    )
    if proc.returncode != 0:
        return [], proc.stderr.strip() or "docker ps failed"

    containers = []
    for line in proc.stdout.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        containers.append(
            {
                "name": row.get("Names", ""),
                "status": row.get("Status", ""),
                "image": row.get("Image", ""),
                "ports": row.get("Ports", ""),
            }
        )
    return containers[:20], None


def docker_daemon_responds() -> bool:
    if shutil.which("docker") is None:
        return False
    proc = run_command(["docker", "info", "--format", "{{json .ServerVersion}}"])
    return proc.returncode == 0


def build_openclaw_health() -> dict:
    health = http_json("http://127.0.0.1:18789/health")
    service = systemctl_status("openclaw-gateway.service", "user")
    model = safe_model_snapshot()
    status = "ok" if health.get("responds") and health.get("status_code") == 200 else "warn"
    if service.get("is_active") not in ("active", "unknown"):
        status = "warn"
    return {
        "ok": True,
        "command": "openclaw_health",
        "status": status,
        "data": {"gateway_health": health, "systemd_user": service, "model": model},
    }


def build_docker_status() -> dict:
    cli_available = shutil.which("docker") is not None
    daemon = docker_daemon_responds()
    containers, error = docker_containers()
    status = "ok" if cli_available and daemon else "warn"
    data = {
        "cli_available": cli_available,
        "daemon_responds": daemon,
        "containers": containers,
    }
    if error:
        data["error"] = error
    return {"ok": True, "command": "docker_status", "status": status, "data": data}


def build_ollama_status() -> dict:
    base = "http://127.0.0.1:11434"
    root = http_json(base)
    tags = http_json(f"{base}/api/tags")
    models = []
    if tags.get("responds") and isinstance(tags.get("body"), dict):
        raw_models = tags["body"].get("models", [])
        if isinstance(raw_models, list):
            for item in raw_models[:10]:
                if isinstance(item, dict) and item.get("name"):
                    models.append(item["name"])
    status = "ok" if tags.get("responds") and tags.get("status_code") == 200 else "warn"
    return {
        "ok": True,
        "command": "ollama_status",
        "status": status,
        "data": {
            "port_11434_responds": root.get("responds"),
            "api_tags_responds": tags.get("responds"),
            "models": models,
        },
    }


def build_n8n_health() -> dict:
    containers, docker_error = docker_containers()
    n8n_containers = [
        item for item in containers if "n8n" in item.get("name", "").lower() or "n8n" in item.get("image", "").lower()
    ]
    detected_ports = []
    for item in n8n_containers:
        for match in PORT_MAP_RE.finditer(item.get("ports", "")):
            detected_ports.append(int(match.group(1)))
    local_ports = []
    for port in sorted(set([5678, 5679, *detected_ports])):
        url = f"http://127.0.0.1:{port}/"
        result = http_json(url)
        local_ports.append({"port": port, "responds": result.get("responds"), "status_code": result.get("status_code")})
    responds = any(item.get("responds") for item in local_ports)
    visible = bool(n8n_containers)
    status = "ok" if visible or responds else "warn"
    data = {
        "visible_container_or_service": visible,
        "containers": n8n_containers[:10],
        "local_ports": local_ports,
    }
    if docker_error:
        data["docker_note"] = docker_error
    return {"ok": True, "command": "n8n_health", "status": status, "data": data}


def build_service_status() -> dict:
    services = [systemctl_status(unit, scope) for unit, scope in SERVICE_ALLOWLIST]
    return {"ok": True, "command": "service_status", "status": "ok", "data": {"services": services}}


def build_log_tail() -> tuple[dict, int]:
    if shutil.which("journalctl") is None:
        return {"ok": False, "command": "log_tail", "error": "journalctl not available"}, 2
    proc = run_command(
        [
            "journalctl",
            "--user",
            "-u",
            "openclaw-gateway.service",
            "-n",
            str(LOG_LIMIT),
            "--no-pager",
        ]
    )
    if proc.returncode != 0:
        return {"ok": False, "command": "log_tail", "error": proc.stderr.strip() or "journalctl failed"}, 2
    lines = [sanitize_text(line) for line in proc.stdout.splitlines()[-LOG_LIMIT:]]
    return {
        "ok": True,
        "command": "log_tail",
        "status": "ok",
        "data": {"unit": "openclaw-gateway.service", "line_limit": LOG_LIMIT, "lines": lines},
    }, 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return emit_error("unknown", "usage: lucy_service_status_command.py <subcommand>")

    command = argv[1]
    if command not in ALLOWED_COMMANDS:
        return emit_error(command, "unsupported command")

    try:
        if command == "openclaw_health":
            return emit(build_openclaw_health())
        if command == "docker_status":
            return emit(build_docker_status())
        if command == "ollama_status":
            return emit(build_ollama_status())
        if command == "n8n_health":
            return emit(build_n8n_health())
        if command == "service_status":
            return emit(build_service_status())
        payload, code = build_log_tail()
        return emit(payload, code)
    except subprocess.TimeoutExpired:
        return emit_error(command, "command timeout")
    except Exception as exc:  # pragma: no cover - final JSON guardrail
        return emit_error(command, f"unexpected error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
