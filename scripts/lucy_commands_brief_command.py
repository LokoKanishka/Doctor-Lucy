#!/usr/bin/env python3
"""Deterministic read-only compact commands index for LucyClaw."""

from __future__ import annotations

import json
import sys


PAYLOAD = {
    "ok": True,
    "command": "commands_brief",
    "stage": "R57",
    "title": "LucyClaw comandos",
    "groups": {
        "estado": [
            "/health_brief",
            "/health_report",
            "/openclaw_health",
        ],
        "lectura": [
            "/fs_read",
            "/fs_find",
            "/fs_grep",
            "/doc_brief",
            "/repo_map",
        ],
        "planificacion": [
            "/plan_brief",
            "/risk_check",
            "/permission_brief",
            "/change_plan",
            "/scaffold_plan",
        ],
        "seguridad": [
            "/lucy_next_step",
            "/lucy_capabilities",
            "/lucy_help",
            "/commands_brief",
        ],
        "maquina_servicios": [
            "/sys_status",
            "/gpu_status",
            "/disk_status",
            "/process_status",
            "/docker_status",
            "/ollama_status",
            "/n8n_health",
            "/service_status",
            "/log_tail",
        ],
    },
    "recommended_flow": [
        "/health_brief",
        "/commands_brief",
        "/repo_map",
        "/lucy_next_step",
    ],
    "blocked": [
        "no .env",
        "no tokens",
        "no memoria",
        "no n8n workflows",
        "no bóveda",
        "no personalidad",
        "no sudo",
    ],
    "next": "Usar /lucy_help para explicación o /lucy_next_step antes de avanzar.",
}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(
            json.dumps(
                {
                    "ok": False,
                    "command": "commands_brief",
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
