#!/usr/bin/env python3
"""Deterministic read-only filesystem search wrappers for LucyClaw."""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
HELPER = SCRIPT_DIR / "lucy_fs_readonly.py"
SUBPROCESS_TIMEOUT = 15
MAX_RESULTS = 50
MAX_TEXT_LENGTH = 240
FORBIDDEN_RESULT_SEGMENTS = (
    ".agents/",
    ".git/",
    "n8n_data/",
    "n8n_backups/",
    "node_modules/",
    "__pycache__/",
)
SENSITIVE_QUERY_RE = re.compile(
    r"(?i)(?:^|[^a-z])(?:token|secret|api[_-]?key|apikey|authorization|access[_-]?token|refresh[_-]?token|password|\.env)(?:[^a-z]|$)"
)
SECRET_RE = re.compile(
    r"(?i)\b(token|secret|api[_-]?key|apikey|authorization|accessToken|refreshToken|password)"
    r"([^\s:=]*)\s*[:= ]\s*[^,\s]+"
)
SENSITIVE_WORD_RE = re.compile(
    r"(?i)(token|secret|api[_-]?key|apikey|authorization|accessToken|refreshToken|password)"
)


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def parse_tokens(argv: list[str]) -> list[str]:
    if len(argv) == 1:
        return shlex.split(argv[0])
    return argv


def reject_sensitive_query(query: str) -> None:
    if SENSITIVE_QUERY_RE.search(query):
        raise ValueError("query contains blocked sensitive terms")


def sanitize_text(value: str) -> str:
    text = SECRET_RE.sub(lambda match: f"{match.group(1)}{match.group(2)}=***", value)
    if SENSITIVE_WORD_RE.search(text):
        text = SENSITIVE_WORD_RE.sub(lambda match: f"{match.group(1)}=***", text)
    text = text.rstrip("\n")
    if len(text) > MAX_TEXT_LENGTH:
        return text[: MAX_TEXT_LENGTH - 3] + "..."
    return text


def is_allowed_result_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return not any(segment in normalized for segment in FORBIDDEN_RESULT_SEGMENTS)


def run_helper(args: list[str]) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, str(HELPER), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "search timeout"}

    raw = proc.stdout.strip()
    if not raw:
        return {"ok": False, "error": proc.stderr.strip() or "helper returned no output"}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"ok": False, "error": "helper returned invalid JSON"}

    if proc.returncode != 0 or not payload.get("ok"):
        return {"ok": False, "error": payload.get("error") or f"helper exited {proc.returncode}"}
    return payload


def build_find(argv: list[str]) -> tuple[dict, int]:
    tokens = parse_tokens(argv)
    query = " ".join(tokens).strip()
    if not query:
        return {"ok": False, "command": "fs_find", "error": "usage: lucy_fs_search_command.py find <query>"}, 2
    reject_sensitive_query(query)

    payload = run_helper(["find_files", "--query", query, "--max-results", str(MAX_RESULTS)])
    if not payload.get("ok"):
        return {"ok": False, "command": "fs_find", "query": query, "error": payload.get("error", "find failed")}, 2

    raw_results = payload.get("results", [])
    results = [path for path in raw_results if isinstance(path, str) and is_allowed_result_path(path)]
    return {
        "ok": True,
        "command": "fs_find",
        "query": query,
        "count": len(results),
        "results": results,
        "truncated": len(raw_results) >= MAX_RESULTS,
    }, 0


def build_grep(argv: list[str]) -> tuple[dict, int]:
    tokens = parse_tokens(argv)
    if not tokens:
        return {"ok": False, "command": "fs_grep", "error": "usage: lucy_fs_search_command.py grep <query> [scope]"}, 2

    if len(tokens) == 1:
        query = tokens[0]
        scope = "."
    else:
        scope = tokens[-1]
        query = " ".join(tokens[:-1]).strip()

    if not query:
        return {"ok": False, "command": "fs_grep", "error": "query must not be empty"}, 2
    reject_sensitive_query(query)

    payload = run_helper(["grep_text", "--query", query, "--path", scope, "--max-results", str(MAX_RESULTS)])
    if not payload.get("ok"):
        return {
            "ok": False,
            "command": "fs_grep",
            "query": query,
            "scope": scope,
            "error": payload.get("error", "grep failed"),
        }, 2

    raw_results = payload.get("results", [])
    results = []
    for row in raw_results:
        if not isinstance(row, dict):
            continue
        path = row.get("path")
        if not isinstance(path, str) or not is_allowed_result_path(path):
            continue
        results.append(
            {
                "path": path,
                "line": row.get("line"),
                "text": sanitize_text(str(row.get("text", ""))),
            }
        )

    return {
        "ok": True,
        "command": "fs_grep",
        "query": query,
        "scope": scope,
        "count": len(results),
        "results": results,
        "truncated": len(raw_results) >= MAX_RESULTS,
    }, 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return emit({"ok": False, "error": "usage: lucy_fs_search_command.py <find|grep> <query> [scope]"}, 2)

    mode = argv[1]
    tail = argv[2:]
    try:
        if mode == "find":
            payload, code = build_find(tail)
            return emit(payload, code)
        if mode == "grep":
            payload, code = build_grep(tail)
            return emit(payload, code)
        return emit({"ok": False, "error": "unsupported mode"}, 2)
    except ValueError as exc:
        command = "fs_find" if mode == "find" else "fs_grep" if mode == "grep" else "unknown"
        return emit({"ok": False, "command": command, "error": str(exc)}, 2)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
