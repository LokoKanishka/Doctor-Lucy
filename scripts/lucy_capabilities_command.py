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
            "/plan_brief",
            "/risk_check",
            "/permission_brief",
            "/change_plan",
            "/scaffold_plan",
            "/lucy_help",
            "/commands_brief",
            "/lucy_capabilities",
            "/run_registry",
            "/rollback_plan",
            "/yellow_preflight",
            "/daemon_brief",
            "/lucy_next_step",
            "/repo_map",
            "/machine_downloads",
            "/machine_ls",
            "/machine_stat",
            "/machine_status",
            "/machine_processes",
            "/machine_ram",
            "/machine_disk",
            "/machine_gpu",
            "/machine_read",
            "/machine_doc_brief"
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
    "next": "Usar /repo_map y /doc_brief para orientación; luego /plan_brief, /risk_check, /permission_brief y /change_plan antes de cualquier tramo amarillo.",
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
