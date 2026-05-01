#!/usr/bin/env python3
"""Compact read-only health summary for Telegram built from lucy_health_report."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_SCRIPT = ROOT / "scripts" / "lucy_health_report_command.py"
SUBPROCESS_TIMEOUT = 20
LINE_LIMIT = 240
WARNING_LIMIT = 3
SECRET_RE = re.compile(
    r"(?i)\b(token|secret|api[_-]?key|apikey|authorization|accessToken|refreshToken|password)"
    r"([^\s:=]*)\s*[:= ]\s*[^,\s]+"
)
SENSITIVE_WORD_RE = re.compile(
    r"(?i)(token|secret|api[_-]?key|apikey|authorization|accessToken|refreshToken|password)"
)

STATUS_LABELS = {
    "machine": "máquina",
    "gpu": "GPU",
    "disk": "disco",
    "openclaw": "OpenClaw",
    "docker": "Docker",
    "ollama": "Ollama",
    "n8n": "n8n",
    "logs": "logs",
}


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


def run_health_report() -> dict:
    if not REPORT_SCRIPT.exists():
        return {"ok": False, "error": f"missing wrapper: {REPORT_SCRIPT.name}"}
    try:
        proc = subprocess.run(
            ["python3", str(REPORT_SCRIPT)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "health_report timeout"}

    raw = proc.stdout.strip()
    if not raw:
        return {"ok": False, "error": sanitize_text(proc.stderr.strip() or f"health_report exited {proc.returncode}")}

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"ok": False, "error": "health_report returned invalid JSON"}

    if proc.returncode != 0 and payload.get("ok") is not False:
        payload["ok"] = False
        payload["error"] = "health_report failed"
    return payload


def summarize_components(summary: dict) -> tuple[list[str], list[str]]:
    ok_items: list[str] = []
    problem_items: list[str] = []
    for key in ("machine", "gpu", "disk", "openclaw", "docker", "ollama", "n8n", "logs"):
        label = STATUS_LABELS[key]
        status = summary.get(key)
        if status == "ok":
            ok_items.append(label)
        elif status in ("warn", "error"):
            problem_items.append(label)
    return ok_items, problem_items


def join_labels(labels: list[str]) -> str:
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} y {labels[1]}"
    return f"{', '.join(labels[:-1])} y {labels[-1]}"


def build_brief(report: dict) -> dict:
    if not report.get("ok"):
        return {
            "ok": False,
            "command": "health_brief",
            "overall": "error",
            "error": sanitize_text(report.get("error") or "health_report failed"),
        }

    overall = report.get("overall", "warn")
    summary = report.get("summary", {})
    warnings = [sanitize_text(str(item)) for item in report.get("warnings", [])[:WARNING_LIMIT]]
    ok_items, problem_items = summarize_components(summary)

    if overall == "ok":
        brief = f"OK: {join_labels(ok_items)} sanos."
        next_step = "No reparar. Usar /health_report para detalle."
    elif overall == "warn":
        if problem_items:
            brief = f"WARN: sistema operativo, pero hay señales en {join_labels(problem_items)}."
        else:
            brief = "WARN: sistema operativo, pero hay señales de advertencia."
        next_step = "Revisar /health_report o comandos individuales antes de reparar."
    else:
        if problem_items:
            brief = f"ERROR: revisar {join_labels(problem_items)}."
        else:
            brief = "ERROR: revisar /health_report para detalle."
        next_step = "No reparar automáticamente. Revisar /health_report antes de actuar."

    return {
        "ok": True,
        "command": "health_brief",
        "overall": overall,
        "brief": brief,
        "warnings": warnings,
        "next": next_step,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        return emit({"ok": False, "command": "health_brief", "overall": "error", "error": "arguments are not supported"}, 2)
    report = run_health_report()
    brief = build_brief(report)
    return emit(brief, 0 if brief.get("ok") else 2)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
