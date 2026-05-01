#!/usr/bin/env python3
"""Deterministic safe advance gate for LucyClaw."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = "python3"
TIMEOUT = 40
SUGGESTED_NEXT = "R49 /repo_map"


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def run_json(args: list[str], *, extra_env: dict[str, str] | None = None) -> tuple[dict, int]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        args,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
        env=env,
    )
    raw = proc.stdout.strip()
    if not raw:
        return {"ok": False, "error": proc.stderr.strip() or "command returned no stdout"}, proc.returncode or 2
    try:
        return json.loads(raw), proc.returncode
    except json.JSONDecodeError:
        return {"ok": False, "error": "command returned invalid JSON"}, 2


def git_state() -> str:
    proc = subprocess.run(
        ["git", "status", "--short", "--branch"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10,
        shell=False,
        cwd=ROOT,
    )
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if proc.returncode != 0:
        return "error"
    if len(lines) <= 1:
        return "clean"
    return "dirty"


def build_payload(argv: list[str]) -> tuple[dict, int]:
    if len(argv) != 1:
        return {
            "ok": False,
            "command": "lucy_next_step",
            "stage": "R48",
            "error": "arguments are not supported",
        }, 2

    basis = {"git": git_state()}
    qa_payload, qa_code = run_json(
        [PYTHON, "scripts/verify_lucyclaw_green_commands.py"],
        extra_env={"LUCY_SKIP_NEXT_STEP": "1"},
    )
    sec_payload, sec_code = run_json([PYTHON, "scripts/verify_lucyclaw_security_policy.py"])
    health_payload, health_code = run_json([PYTHON, "scripts/lucy_health_brief_command.py"])
    caps_payload, _ = run_json([PYTHON, "scripts/lucy_capabilities_command.py"])

    basis["qa1"] = "ok" if qa_code == 0 and qa_payload.get("ok") else "failed"
    basis["sec1"] = "ok" if sec_code == 0 and sec_payload.get("ok") and not sec_payload.get("violations") else "failed"
    health_overall = health_payload.get("overall") if isinstance(health_payload, dict) else None
    if health_code == 0 and health_payload.get("ok") and health_overall in {"ok", "warn"}:
        basis["health"] = "ok_or_warn" if health_overall == "ok" else "warn"
    elif health_payload.get("ok") and health_overall == "error":
        basis["health"] = "error"
    else:
        basis["health"] = "error"
    basis["capabilities"] = "green layer available" if caps_payload.get("ok") else "unknown"

    if basis["git"] != "clean" or basis["qa1"] != "ok" or basis["sec1"] != "ok" or basis["health"] == "error":
        return {
            "ok": True,
            "command": "lucy_next_step",
            "stage": "R48",
            "decision": "BLOCK",
            "basis": basis,
            "recommendation": {
                "type": "hold",
                "next": "No avanzar a nueva capacidad.",
            },
            "safe_steps": [
                "corregir git status",
                "correr QA1",
                "correr SEC1",
                "revisar /health_report",
                "pedir autorización antes de tocar runtime",
            ],
        }, 0

    if basis["health"] == "warn":
        return {
            "ok": True,
            "command": "lucy_next_step",
            "stage": "R48",
            "decision": "WARN",
            "basis": basis,
            "recommendation": {
                "type": "diagnose_first",
                "next": "Revisar /health_report antes de nueva capacidad si el warn no es conocido.",
            },
            "safe_steps": [
                "usar /health_brief",
                "usar /health_report",
                "usar /log_tail acotado",
                "no reparar sin autorización",
            ],
        }, 0

    return {
        "ok": True,
        "command": "lucy_next_step",
        "stage": "R48",
        "decision": "READY",
        "basis": basis,
        "recommendation": {
            "type": "proceed",
            "next": "Preparar próximo tramo read-only o bounded.",
            "suggested": SUGGESTED_NEXT,
        },
        "allowed_next_actions": [
            "preparar ticket",
            "leer repo con /fs_find, /fs_grep y /fs_read",
            "generar plan read-only",
            "crear scaffold con TPL1 en tramo futuro",
        ],
        "blocked_actions": [
            "reparar sin autorización",
            "reiniciar sin autorización",
            "tocar n8n workflows",
            "leer .env",
            "usar sudo",
            "commitear cambios no revisados",
        ],
        "next": "Si Diego autoriza, preparar R49.",
    }, 0


def main(argv: list[str]) -> int:
    payload, code = build_payload(argv)
    return emit(payload, code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
