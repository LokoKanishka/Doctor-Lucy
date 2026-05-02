#!/usr/bin/env python3
"""Compact read-only repo map for LucyClaw/OpenClaw navigation."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_LABEL = "doctora-lucy"
STAGE = "R49"
MAX_TOP_LEVEL = 8

TOP_LEVEL_CANDIDATES = (
    "docs",
    "scripts",
    "openclaw_plugins",
    "data",
    "diagnostics",
    "systemd",
    "memoria",
    "skills",
)
KEY_FILE_CANDIDATES = {
    "ssot": [
        "docs/LUCYCLAW_CURRENT_STATE.md",
    ],
    "qa": [
        "scripts/verify_lucyclaw_green_commands.py",
        "scripts/verify_lucyclaw_security_policy.py",
    ],
    "commands": [
        "scripts/lucy_capabilities_command.py",
        "scripts/lucy_next_step_command.py",
        "scripts/lucy_fs_search_command.py",
        "scripts/lucy_repo_map_command.py",
    ],
    "plugins": [
        "openclaw_plugins/lucy-fs-readonly-command/",
        "openclaw_plugins/lucy-fs-search-command/",
        "openclaw_plugins/lucy-next-step-command/",
        "openclaw_plugins/lucy-repo-map-command/",
    ],
    "docs": [
        "docs/LUCYCLAW_REPO_MAP_R49.md",
        "docs/LUCYCLAW_NEXT_STEP_R48.md",
        "docs/LUCYCLAW_FS_SEARCH_R47.md",
    ],
}
SENSITIVE_SEGMENTS = tuple(
    "".join(parts)
    for parts in (
        (".", "env"),
        (".", "git"),
        (".", "agents"),
        ("n8n_", "data"),
        ("n8n_", "backups"),
        ("work", "flows"),
        ("cred", "entials"),
        ("database", ".sqlite"),
        ("token", "s"),
    )
)


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def is_sensitive(path_text: str) -> bool:
    lowered = path_text.lower()
    return any(segment.lower() in lowered for segment in SENSITIVE_SEGMENTS)


def existing_top_level() -> list[str]:
    results: list[str] = []
    for name in TOP_LEVEL_CANDIDATES:
        candidate = ROOT / name
        if candidate.exists() and not is_sensitive(name):
            suffix = "/" if candidate.is_dir() else ""
            results.append(f"{name}{suffix}")
    return results[:MAX_TOP_LEVEL]


def filter_existing(paths: list[str]) -> list[str]:
    results: list[str] = []
    for path_text in paths:
        normalized = path_text.rstrip("/")
        if is_sensitive(normalized):
            continue
        if (ROOT / normalized).exists():
            results.append(path_text)
    return results


def build_payload(argv: list[str]) -> tuple[dict, int]:
    if len(argv) != 1:
        return {
            "ok": False,
            "command": "repo_map",
            "stage": STAGE,
            "error": "arguments are not supported",
        }, 2

    key_files = {section: filter_existing(paths) for section, paths in KEY_FILE_CANDIDATES.items()}

    return {
        "ok": True,
        "command": "repo_map",
        "stage": STAGE,
        "root": ROOT_LABEL,
        "status": {
            "mode": "read-only",
            "bounded": True,
            "sensitive_paths_excluded": True,
        },
        "summary": {
            "purpose": "Mapa compacto del repo para navegación segura.",
            "recommended_next": "Usar /fs_find, /fs_grep y /fs_read para profundizar.",
        },
        "top_level": existing_top_level(),
        "lucy_commands": {
            "read": ["/fs_read", "/fs_find", "/fs_grep"],
            "health": ["/health_brief", "/health_report", "/openclaw_health"],
            "machine": ["/sys_status", "/gpu_status", "/disk_status", "/process_status"],
            "services": ["/docker_status", "/ollama_status", "/n8n_health", "/service_status", "/log_tail"],
            "policy": ["/lucy_capabilities", "/lucy_next_step", "/repo_map"],
        },
        "key_files": key_files,
        "safe_navigation": [
            "/fs_find <nombre>",
            "/fs_grep <texto> [scope]",
            "/fs_read <archivo> <linea_inicio> <linea_fin>",
        ],
        "excluded": [
            "env files",
            "git metadata",
            "agent internals",
            "n8n runtime data",
            "n8n backups",
            "auth material",
            "automation internals",
            "sqlite/db internals",
            "logs pesados",
        ],
        "next": "Usar /repo_map para orientación general; usar /fs_find y /fs_grep para búsqueda puntual.",
    }, 0


def main(argv: list[str]) -> int:
    payload, code = build_payload(argv)
    return emit(payload, code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
