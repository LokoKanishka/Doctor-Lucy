#!/usr/bin/env python3
"""Deterministic read-only planning brief for LucyClaw."""

from __future__ import annotations

import json
import sys

from lucy_planning_readonly import (
    build_acceptance,
    build_checks,
    build_safe_alternatives,
    build_tests,
    classify_risk,
    collect_review_files,
    grouped_authorization_text,
    normalize_request,
    redact_request,
    summarize_permissions,
)


STAGE = "R51"


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def build_payload(raw_request: str) -> tuple[dict, int]:
    request_text = normalize_request(raw_request)
    risk = classify_risk(request_text)
    permissions = summarize_permissions(request_text, risk["level"])
    return {
        "ok": True,
        "command": "plan_brief",
        "stage": STAGE,
        "decision": "PLAN_ONLY",
        "scope": "read-only",
        "request_summary": redact_request(request_text),
        "target_risk": risk["level"],
        "files_to_review": collect_review_files(request_text),
        "risks": risk["reasons"],
        "permissions_needed": permissions,
        "approval": {
            "mode": risk["authorization"],
            "grouped_recommendation": grouped_authorization_text(permissions, risk["level"]),
        },
        "checks": build_checks(risk["level"]),
        "tests": build_tests(request_text, risk["level"]),
        "acceptance_criteria": build_acceptance(request_text, risk["level"]),
        "safe_alternatives": build_safe_alternatives(request_text, risk["level"]),
        "next": "Usar /risk_check y /permission_brief antes de cualquier tramo amarillo.",
    }, 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return emit(
            {
                "ok": False,
                "command": "plan_brief",
                "stage": STAGE,
                "error": "usage: /plan_brief <request>",
            },
            2,
        )
    try:
        payload, code = build_payload(argv[1])
    except ValueError as exc:
        return emit(
            {
                "ok": False,
                "command": "plan_brief",
                "stage": STAGE,
                "error": str(exc),
            },
            2,
        )
    return emit(payload, code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
