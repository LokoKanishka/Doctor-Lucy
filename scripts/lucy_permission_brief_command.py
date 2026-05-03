#!/usr/bin/env python3
"""Deterministic read-only permission brief for LucyClaw requests."""

from __future__ import annotations

import json
import sys

from lucy_planning_readonly import (
    build_checks,
    build_safe_alternatives,
    classify_risk,
    grouped_authorization_text,
    normalize_request,
    redact_request,
    summarize_permissions,
)


STAGE = "R53"


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def build_payload(raw_request: str) -> tuple[dict, int]:
    request_text = normalize_request(raw_request)
    risk = classify_risk(request_text)
    permissions = summarize_permissions(request_text, risk["level"])
    return {
        "ok": True,
        "command": "permission_brief",
        "stage": STAGE,
        "scope": "planning",
        "request_summary": redact_request(request_text),
        "target_risk": risk["level"],
        "permissions_needed": permissions,
        "approval_mode": risk["authorization"],
        "grouped_approval_recommended": grouped_authorization_text(permissions, risk["level"]),
        "checks_before_execution": build_checks(risk["level"]),
        "blocked_zones": [
            "env files",
            "auth material",
            "memory/vault/personality",
            "n8n internals",
        ],
        "safe_alternatives": build_safe_alternatives(request_text, risk["level"]),
    }, 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return emit(
            {
                "ok": False,
                "command": "permission_brief",
                "stage": STAGE,
                "error": "usage: /permission_brief <request>",
            },
            2,
        )
    try:
        payload, code = build_payload(argv[1])
    except ValueError as exc:
        return emit(
            {
                "ok": False,
                "command": "permission_brief",
                "stage": STAGE,
                "error": str(exc),
            },
            2,
        )
    return emit(payload, code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
