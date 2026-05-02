#!/usr/bin/env python3
"""Deterministic read-only capabilities map for LucyClaw."""

from __future__ import annotations

import json
import sys


PAYLOAD = {
    "ok": True,
    "command": "lucy_capabilities",
    "stage": "R46",
    "green": {
        "description": "Acciones read-only permitidas sin autorización previa.",
        "commands": [
            "/fs_read",
            "/fs_find",
            "/fs_grep",
            "/doc_brief",
            "/lucy_next_step",
            "/repo_map",
            "/sys_status",
            "/gpu_status",
            "/disk_status",
            "/process_status",
            "/openclaw_health",
            "/docker_status",
            "/ollama_status",
            "/n8n_health",
            "/service_status",
            "/log_tail",
            "/health_report",
            "/health_brief",
            "/lucy_capabilities",
        ],
    },
    "yellow": {
        "description": "Acciones que requieren autorización explícita antes de ejecutarse.",
        "examples": [
            "instalar o registrar plugins",
            "reiniciar OpenClaw gateway",
            "editar configuración",
            "aplicar reparaciones",
            "commitear cambios",
            "operar escritorio",
        ],
    },
    "red": {
        "description": "Acciones prohibidas salvo autorización explícita excepcional.",
        "limits": [
            "no sudo",
            "no shell libre",
            "no .env",
            "no tokens",
            "no memoria",
            "no n8n workflows",
            "no bóveda",
            "no personalidad",
            "no borrado",
            "no reparación automática",
        ],
    },
    "next": "Usar /repo_map o /doc_brief para orientación segura antes de profundizar.",
}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(
            json.dumps(
                {
                    "ok": False,
                    "command": "lucy_capabilities",
                    "error": "arguments are not supported",
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 2

    print(json.dumps(PAYLOAD, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
