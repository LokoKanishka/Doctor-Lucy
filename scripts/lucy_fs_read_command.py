#!/usr/bin/env python3
"""Deterministic read-lines command wrapper for OpenClaw slash skills."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
HELPER = SCRIPT_DIR / "lucy_fs_readonly.py"


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def parse_int(raw: str, name: str) -> int:
    try:
        value = int(raw, 10)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    return value


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        return emit(
            {
                "ok": False,
                "error": "usage: lucy_fs_read_command.py <relative-path> <start> <end>",
            },
            2,
        )

    path, start_raw, end_raw = argv[1:]
    try:
        start = parse_int(start_raw, "start")
        end = parse_int(end_raw, "end")
    except ValueError as exc:
        return emit({"ok": False, "error": str(exc)}, 2)

    cmd = [
        sys.executable,
        str(HELPER),
        "read_lines",
        "--path",
        path,
        "--start",
        str(start),
        "--end",
        str(end),
    ]
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return emit({"ok": False, "error": "read timeout"}, 2)

    stdout = proc.stdout.strip()
    if not stdout:
        return emit({"ok": False, "error": "helper returned no output"}, 2)

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return emit({"ok": False, "error": "helper returned invalid JSON"}, 2)

    if proc.returncode != 0 or not payload.get("ok"):
        return emit(
            {
                "ok": False,
                "path": path,
                "start": start,
                "end": end,
                "error": payload.get("error") or f"helper exited {proc.returncode}",
            },
            2,
        )

    return emit(
        {
            "ok": True,
            "path": payload.get("path"),
            "start": payload.get("start"),
            "end": payload.get("end"),
            "lines": payload.get("lines", []),
        }
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
