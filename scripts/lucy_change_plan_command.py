#!/usr/bin/env python3
"""Deterministic read-only technical change plan for LucyClaw."""

from __future__ import annotations

import json
import sys

from lucy_planning_readonly import (
    build_acceptance,
    build_blocked_actions,
    build_rollback,
    build_safe_next,
    build_tests,
    classify_change_type,
    classify_risk,
    collect_change_files,
    normalize_request,
    redact_request,
    summarize_permissions,
)


STAGE = "R54"


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def build_payload(raw_request: str) -> tuple[dict, int]:
    request_text = normalize_request(raw_request)
    risk = classify_risk(request_text)
    permissions = summarize_permissions(request_text, risk["level"])
    files = collect_change_files(request_text, risk["level"])
    return {
        "ok": True,
        "command": "change_plan",
        "stage": STAGE,
        "decision": "PLAN_ONLY",
        "request_summary": redact_request(request_text),
        "risk": risk["level"],
        "change_type": classify_change_type(request_text, risk["level"]),
        "files_to_review": files["review"],
        "files_to_create": files["create"],
        "files_to_modify": files["modify"],
        "permissions_needed": permissions,
        "tests": build_tests(request_text, risk["level"]),
        "acceptance_criteria": build_acceptance(request_text, risk["level"]),
        "rollback": build_rollback(risk["level"]),
        "blocked_actions": build_blocked_actions(risk["level"]),
        "safe_next": build_safe_next(request_text, risk["level"]),
    }, 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return emit(
            {
                "ok": False,
                "command": "change_plan",
                "stage": STAGE,
                "error": "usage: /change_plan <request>",
            },
            2,
        )
    try:
        payload, code = build_payload(argv[1])
    except ValueError as exc:
        return emit(
            {
                "ok": False,
                "command": "change_plan",
                "stage": STAGE,
                "error": str(exc),
            },
            2,
        )
    return emit(payload, code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
