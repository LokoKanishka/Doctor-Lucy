#!/usr/bin/env python3
"""Open a safe URL in the host Firefox browser for LucyClaw."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from urllib.parse import urlparse


ALLOWED_SCHEMES = {"http", "https"}


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return code


def firefox_path() -> str | None:
    return shutil.which("firefox")


def is_safe_url(raw_url: str) -> tuple[bool, str]:
    url = raw_url.strip()
    if not url:
        return False, "missing url"
    if any(char in url for char in ("\n", "\r", "\t", "\x00")):
        return False, "url contains control characters"
    if url == "about:blank":
        return True, ""

    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, "only http, https or about:blank URLs are allowed"
    if not parsed.netloc:
        return False, "url must include a host"
    return True, ""


def firefox_status() -> int:
    path = firefox_path()
    pids: list[int] = []
    try:
        proc = subprocess.run(
            ["pgrep", "-x", "firefox"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
            shell=False,
        )
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.isdigit():
                pids.append(int(line))
    except (OSError, subprocess.SubprocessError):
        pids = []

    return emit(
        {
            "ok": path is not None,
            "command": "firefox_status",
            "browser": "firefox",
            "firefox_path": path,
            "running": bool(pids),
            "pids": pids[:20],
            "mutation_allowed": False,
            "shell_used": False,
            "sudo_used": False,
        }
    )


def firefox_open(raw_url: str, mode: str = "tab") -> int:
    path = firefox_path()
    if path is None:
        return emit(
            {
                "ok": False,
                "controlled_failure": True,
                "command": "firefox_open",
                "browser": "firefox",
                "error": "Firefox executable not found",
                "mutation_allowed": True,
                "shell_used": False,
                "sudo_used": False,
            },
            2,
        )

    url = raw_url.strip()
    safe, reason = is_safe_url(url)
    if not safe:
        return emit(
            {
                "ok": False,
                "controlled_failure": True,
                "command": "firefox_open",
                "browser": "firefox",
                "error": "URL rejected",
                "reason": reason,
                "mutation_allowed": False,
                "shell_used": False,
                "sudo_used": False,
            },
            2,
        )

    normalized_mode = mode if mode in {"tab", "window"} else "tab"
    flag = "--new-window" if normalized_mode == "window" else "--new-tab"
    try:
        proc = subprocess.Popen(
            [path, flag, url],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True,
        )
        time.sleep(0.5)
    except OSError as exc:
        return emit(
            {
                "ok": False,
                "controlled_failure": True,
                "command": "firefox_open",
                "browser": "firefox",
                "error": "Firefox launch failed",
                "details": str(exc),
                "mutation_allowed": True,
                "shell_used": False,
                "sudo_used": False,
            },
            2,
        )

    return emit(
        {
            "ok": True,
            "command": "firefox_open",
            "browser": "firefox",
            "url": url,
            "mode": normalized_mode,
            "pid": proc.pid,
            "mutation_allowed": True,
            "shell_used": False,
            "sudo_used": False,
            "evidence": "Firefox launch command accepted by host process.",
            "limit": "This opens visible Firefox; DOM reading/click/playback evidence still requires an automation-capable browser tool.",
        }
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return emit(
            {
                "ok": False,
                "controlled_failure": True,
                "command": "firefox",
                "error": "Usage: lucy_firefox_command.py status|open <url> [tab|window]",
            },
            2,
        )

    command = argv[1]
    if command == "status":
        return firefox_status()
    if command == "open":
        if len(argv) < 3:
            return emit(
                {
                    "ok": False,
                    "controlled_failure": True,
                    "command": "firefox_open",
                    "error": "Missing url",
                },
                2,
            )
        return firefox_open(argv[2], argv[3] if len(argv) > 3 else "tab")

    return emit(
        {
            "ok": False,
            "controlled_failure": True,
            "command": "firefox",
            "error": "Unknown command",
        },
        2,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
