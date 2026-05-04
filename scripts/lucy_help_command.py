#!/usr/bin/env python3
"""Deterministic read-only help guide for LucyClaw."""

from __future__ import annotations

import json
import sys


PAYLOAD = {
    "ok": True,
    "command": "lucy_help",
    "stage": "R56",
    "title": "LucyClaw ayuda rápida",
    "quick_start": [
        "/health_brief — estado rápido",
        "/repo_map — mapa del repo",
        "/doc_brief <path> — resumen seguro de un archivo",
        "/fs_find <texto> — buscar archivos",
        "/fs_grep <texto> [scope] — buscar texto",
        "/lucy_next_step — decidir si avanzar",
        "/plan_brief <pedido> — armar brief",
        "/risk_check <pedido> — clasificar riesgo",
        "/permission_brief <pedido> — permisos necesarios",
        "/change_plan <pedido> — plan técnico",
        "/scaffold_plan <pedido> — plan de scaffold",
    ],
    "safe_flow": [
        "1. /health_brief",
        "2. /repo_map",
        "3. /doc_brief o /fs_find",
        "4. /lucy_next_step",
        "5. /plan_brief / risk_check / permission_brief / change_plan",
    ],
    "blocked": [
        "no .env",
        "no tokens",
        "no memoria",
        "no n8n workflows",
        "no bóveda",
        "no personalidad",
        "no sudo",
        "no reparación automática",
    ],
    "next": "Usar /lucy_next_step antes de avanzar a cualquier tramo.",
}


def main(argv: list[str]) -> int:
    # No arguments accepted
    if len(argv) != 1:
        print(
            json.dumps(
                {
                    "ok": False,
                    "command": "lucy_help",
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
