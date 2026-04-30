#!/usr/bin/env python3
"""Deterministic read-only machine status helpers for LucyClaw."""

from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path


ALLOWED_COMMANDS = {"sys_status", "gpu_status", "disk_status", "process_status"}
PROCESS_LIMIT = 8
SUBPROCESS_TIMEOUT = 10
SENSITIVE_MARKERS = (
    "token",
    "secret",
    "password",
    "api_key",
    "apikey",
    "authorization",
    "access_token",
    "refresh_token",
)


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def emit_error(command: str, message: str, code: int = 2) -> int:
    return emit({"ok": False, "command": command, "error": message}, code)


def round_mb(value_bytes: int) -> float:
    return round(value_bytes / (1024 * 1024), 2)


def round_gb(value_bytes: int) -> float:
    return round(value_bytes / (1024 * 1024 * 1024), 2)


def percent(used: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((used / total) * 100, 2)


def read_proc_uptime() -> float | None:
    try:
        raw = Path("/proc/uptime").read_text(encoding="utf-8").split()[0]
        return round(float(raw), 2)
    except (FileNotFoundError, IndexError, OSError, ValueError):
        return None


def read_loadavg() -> list[float] | None:
    try:
        values = os.getloadavg()
    except OSError:
        return None
    return [round(value, 2) for value in values]


def read_meminfo() -> dict[str, int]:
    info: dict[str, int] = {}
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            parts = raw_value.strip().split()
            if not parts:
                continue
            info[key] = int(parts[0]) * 1024
    except (FileNotFoundError, OSError, ValueError):
        return {}
    return info


def run_command(args: list[str], timeout: int = SUBPROCESS_TIMEOUT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        shell=False,
    )


def scrub_text(value: str) -> str:
    compact = " ".join(value.split())
    lowered = compact.lower()
    for marker in SENSITIVE_MARKERS:
        if marker in lowered:
            return "[redacted-command]"
    return compact[:100]


def build_sys_status() -> dict:
    meminfo = read_meminfo()
    total = meminfo.get("MemTotal", 0)
    available = meminfo.get("MemAvailable", 0)
    used = max(total - available, 0)
    data = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "uptime_seconds": read_proc_uptime(),
        "loadavg": read_loadavg(),
        "ram_total_mb": round_mb(total),
        "ram_available_mb": round_mb(available),
        "ram_used_mb": round_mb(used),
        "ram_used_percent": percent(used, total),
    }
    return {"ok": True, "command": "sys_status", "data": data}


def build_gpu_status() -> tuple[dict, int]:
    if shutil.which("nvidia-smi") is None:
        return {"ok": False, "command": "gpu_status", "error": "nvidia-smi not available"}, 2

    query = ",".join(
        [
            "name",
            "memory.used",
            "memory.total",
            "utilization.gpu",
            "temperature.gpu",
        ]
    )
    proc = run_command(
        [
            "nvidia-smi",
            f"--query-gpu={query}",
            "--format=csv,noheader,nounits",
        ]
    )
    if proc.returncode != 0:
        message = proc.stderr.strip() or "nvidia-smi failed"
        return {"ok": False, "command": "gpu_status", "error": message}, 2

    gpus = []
    for line in proc.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 5:
            continue
        name, mem_used, mem_total, util_gpu, temp_gpu = parts
        try:
            gpu = {
                "name": name,
                "memory_used_mb": int(mem_used),
                "memory_total_mb": int(mem_total),
                "gpu_utilization_percent": int(util_gpu),
                "temperature_c": int(temp_gpu),
            }
        except ValueError:
            continue
        gpus.append(gpu)

    return {"ok": True, "command": "gpu_status", "data": {"gpus": gpus}}, 0


def build_disk_status() -> dict:
    target = str(Path.home())
    usage = shutil.disk_usage(target)
    used = usage.total - usage.free
    data = {
        "path": target,
        "total_gb": round_gb(usage.total),
        "used_gb": round_gb(used),
        "free_gb": round_gb(usage.free),
        "used_percent": percent(used, usage.total),
    }
    return {"ok": True, "command": "disk_status", "data": data}


def build_process_status() -> tuple[dict, int]:
    proc = run_command(
        [
            "ps",
            "-eo",
            "pid=,user=,%cpu=,%mem=,args=",
            "--sort=-%mem",
        ]
    )
    if proc.returncode != 0:
        message = proc.stderr.strip() or "ps failed"
        return {"ok": False, "command": "process_status", "error": message}, 2

    processes = []
    for line in proc.stdout.splitlines():
        parts = line.strip().split(None, 4)
        if len(parts) < 5:
            continue
        pid_raw, user, cpu_raw, mem_raw, command = parts
        try:
            row = {
                "pid": int(pid_raw),
                "user": user,
                "cpu_percent": round(float(cpu_raw), 2),
                "mem_percent": round(float(mem_raw), 2),
                "command": scrub_text(command),
            }
        except ValueError:
            continue
        processes.append(row)
        if len(processes) >= PROCESS_LIMIT:
            break

    return {"ok": True, "command": "process_status", "data": {"top_processes": processes}}, 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return emit_error("unknown", "usage: lucy_machine_status_command.py <sys_status|gpu_status|disk_status|process_status>")

    command = argv[1]
    if command not in ALLOWED_COMMANDS:
        return emit_error(command, "unsupported command")

    try:
        if command == "sys_status":
            return emit(build_sys_status())
        if command == "gpu_status":
            payload, code = build_gpu_status()
            return emit(payload, code)
        if command == "disk_status":
            return emit(build_disk_status())
        payload, code = build_process_status()
        return emit(payload, code)
    except subprocess.TimeoutExpired:
        return emit_error(command, "command timeout")
    except Exception as exc:  # pragma: no cover - defensive guardrail
        return emit_error(command, f"unexpected error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
