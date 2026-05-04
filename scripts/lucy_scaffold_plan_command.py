#!/usr/bin/env python3
"""Deterministic read-only technical scaffold plan for LucyClaw."""

from __future__ import annotations

import json
import re
import sys

from lucy_planning_readonly import (
    build_acceptance,
    build_blocked_actions,
    build_rollback,
    build_tests,
    classify_risk,
    normalize_request,
    redact_request,
    summarize_permissions,
)


STAGE = "R55"


def extract_slug(text: str) -> str:
    """Extract a reasonable command name slug from the request text."""
    lowered = text.lower()
    match = re.search(r"(?:command|comando)\s+([a-z0-9_-]+(?:\s+[a-z0-9_-]+){0,2})", lowered)
    if match:
        words = match.group(1).split()
        # Remove filler words
        filtered = [w for w in words if w not in ("para", "read-only", "que", "de", "un")]
        if filtered:
            return "_".join(filtered)
    # Fallback
    words = re.findall(r"[a-z0-9]+", lowered)
    filtered = [w for w in words if w not in ("comando", "command", "agregar", "crear", "hacer", "un", "para", "read", "only")]
    if filtered:
        return "_".join(filtered[:2])
    return "custom"


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def build_payload(raw_request: str) -> tuple[dict, int]:
    request_text = normalize_request(raw_request)
    risk = classify_risk(request_text)
    permissions = summarize_permissions(request_text, risk["level"])
    
    slug = extract_slug(request_text)
    plugin_dir = f"openclaw_plugins/lucy-{slug.replace('_', '-')}-command"
    
    return {
        "ok": True,
        "command": "scaffold_plan",
        "stage": STAGE,
        "decision": "PLAN_ONLY",
        "request_summary": redact_request(request_text),
        "suggested_command": f"/{slug}",
        "suggested_stage": "RXX",
        "risk": risk["level"],
        "scaffold": {
            "wrapper": f"scripts/lucy_{slug}_command.py",
            "plugin_dir": plugin_dir + "/",
            "docs": f"docs/LUCYCLAW_{slug.upper()}_RXX.md"
        },
        "files_to_create": [
            f"scripts/lucy_{slug}_command.py",
            f"{plugin_dir}/package.json",
            f"{plugin_dir}/openclaw.plugin.json",
            f"{plugin_dir}/index.js",
            f"docs/LUCYCLAW_{slug.upper()}_RXX.md"
        ] if risk["level"] != "RED" else [],
        "files_to_modify": [
            "scripts/lucy_planning_readonly.py",
            "scripts/lucy_capabilities_command.py",
            "scripts/lucy_repo_map_command.py",
            "scripts/verify_lucyclaw_green_commands.py",
            "scripts/verify_lucyclaw_security_policy.py",
            "docs/LUCYCLAW_CURRENT_STATE.md"
        ] if risk["level"] != "RED" else [],
        "permissions_needed": permissions,
        "tests": build_tests(request_text, risk["level"]),
        "acceptance_criteria": build_acceptance(request_text, risk["level"]),
        "rollback": build_rollback(risk["level"]),
        "blocked_actions": build_blocked_actions(risk["level"]),
    }, 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return emit(
            {
                "ok": False,
                "command": "scaffold_plan",
                "stage": STAGE,
                "error": "usage: /scaffold_plan <request>",
            },
            2,
        )
    try:
        payload, code = build_payload(argv[1])
    except ValueError as exc:
        return emit(
            {
                "ok": False,
                "command": "scaffold_plan",
                "stage": STAGE,
                "error": str(exc),
            },
            2,
        )
    return emit(payload, code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))