#!/usr/bin/env python3
"""Deterministic read-only risk classifier for LucyClaw requests."""

from __future__ import annotations

import json
import sys

from lucy_planning_readonly import (
    build_rollback,
    build_risk_checks,
    build_safe_alternatives,
    classify_risk,
    normalize_request,
    redact_request,
)


STAGE = "R52"


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def build_payload(raw_request: str) -> tuple[dict, int]:
    request_text = normalize_request(raw_request)
    risk = classify_risk(request_text)
    level = risk["level"]
    summary = {
        "GREEN": "VERDE: se puede orientar y verificar con capa read-only.",
        "YELLOW": "AMARILLO: requiere autorización explícita antes de tocar código o runtime.",
        "RED": "ROJO: cae en zona prohibida para LucyClaw verde.",
    }[level]
    return {
        "ok": True,
        "command": "risk_check",
        "stage": STAGE,
        "request_summary": redact_request(request_text),
        "risk": level,
        "approval": risk["authorization"],
        "summary": summary,
        "reasons": risk["reasons"],
        "checks_previos": build_risk_checks(request_text, level),
        "rollback": build_rollback(level),
        "safe_alternatives": build_safe_alternatives(request_text, level),
    }, 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return emit(
            {
                "ok": False,
                "command": "risk_check",
                "stage": STAGE,
                "error": "usage: /risk_check <request>",
            },
            2,
        )
    try:
        payload, code = build_payload(argv[1])
    except ValueError as exc:
        return emit(
            {
                "ok": False,
                "command": "risk_check",
                "stage": STAGE,
                "error": str(exc),
            },
            2,
        )
    return emit(payload, code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
