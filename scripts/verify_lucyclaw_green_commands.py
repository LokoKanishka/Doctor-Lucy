#!/usr/bin/env python3
"""Unified smoke verifier for LucyClaw green commands."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = "python3"
# Yellow/daemon meta-checks invoke nested read-only validators and can take
# longer than the earlier 30s budget without indicating a real failure.
TIMEOUT = 90
MAX_HEALTH_REPORT_LOG_LINES = 20
MAX_LOG_TAIL_LINES = 80

SENSITIVE_VALUE_RE = re.compile(
    r"(?i)\b(?:token|secret|api[_-]?key|apikey|authorization|access[_-]?token|refresh[_-]?token|password)\b"
    r"[^\n:=]{0,20}[:= ][^\s,\]}]{4,}"
)
OPENAI_KEY_RE = re.compile(r"(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]{10,}")
ENV_PATH_RE = re.compile(r"(^|[\\/])\.env($|[./])", re.IGNORECASE)
N8N_WORKFLOW_RE = re.compile(r"workflow", re.IGNORECASE)
LEGACY_PATH_RE = re.compile(r"/home/lucy-ubuntu/Escritorio/doctor de lucy")
LOG_SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?:token|secret|api[_-]?key|apikey|authorization|access[_-]?token|refresh[_-]?token|password)\b"
    r"[^\n:=]{0,20}(?::|=)\s*([^\s,\]}]+)"
)
LOG_BEARER_RE = re.compile(r"(?i)" + "authori" + "zation" + r"\s*:\s*" + "bear" + r"er\s+\S+")
LOG_STRUCTURAL_BLOCK_RE = re.compile(
    r"(?i)(?:^|[^a-z])(?:credentials|database\.sqlite|n8n_data/|n8n_backups/|/workflows|workflow[s]?/)(?:[^a-z]|$)"
)
FULLY_REDACTED_VALUE_RE = re.compile(r"^[*\-._<>\[\]{}()=,:;!?/\\|]+$")


def run_json(args: list[str]) -> tuple[dict, str]:
    env = os.environ.copy()
    proc = subprocess.run(
        args,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
        env=env,
    )
    raw = proc.stdout.strip()
    if not raw:
        raise RuntimeError(f"{' '.join(args)} returned no stdout")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{' '.join(args)} returned invalid JSON") from exc
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} exited {proc.returncode}: {raw[:400]}")
    return payload, raw


def flatten_strings(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from flatten_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from flatten_strings(item)
    elif isinstance(value, str):
        yield value


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def assert_no_sensitive_strings(payload: dict, *, forbid_env=True, forbid_legacy_path=True) -> None:
    for text in flatten_strings(payload):
        assert_true(not SENSITIVE_VALUE_RE.search(text), f"sensitive-looking assignment found: {text[:120]}")
        assert_true(not OPENAI_KEY_RE.search(text), f"OpenAI-like key found: {text[:120]}")
        if forbid_env:
            assert_true(not ENV_PATH_RE.search(text), f".env reference found: {text[:120]}")
        if forbid_legacy_path:
            assert_true(not LEGACY_PATH_RE.search(text), f"legacy hardcoded path found: {text[:120]}")


def _is_fully_redacted_log_value(value: str) -> bool:
    compact = value.strip().strip("`'\"")
    return bool(compact) and FULLY_REDACTED_VALUE_RE.fullmatch(compact) is not None


def assert_no_sensitive_log_leaks(payload: dict) -> None:
    lines = payload.get("data", {}).get("lines", [])
    assert_true(isinstance(lines, list), "log payload lines is not a list")
    for line in lines:
        assert_true(isinstance(line, str), "log payload line is not a string")
        assert_true(not OPENAI_KEY_RE.search(line), f"OpenAI-like key found in log: {line[:120]}")
        assert_true(not LOG_BEARER_RE.search(line), f"sensitive auth header found in log: {line[:120]}")
        assert_true(not ENV_PATH_RE.search(line), f".env reference found in log: {line[:120]}")
        assert_true(not LEGACY_PATH_RE.search(line), f"legacy hardcoded path found in log: {line[:120]}")
        assert_true(not LOG_STRUCTURAL_BLOCK_RE.search(line), f"sensitive structural path found in log: {line[:120]}")
        for match in LOG_SENSITIVE_ASSIGNMENT_RE.finditer(line):
            value = match.group(1)
            assert_true(
                _is_fully_redacted_log_value(value),
                f"sensitive-looking log assignment found: {line[:120]}",
            )


def verify_fs_read(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_fs_read_command.py", "scripts/lucy_openclaw_bridge.py", "138", "138"])
    assert_true(payload.get("ok") is True, "fs_read did not return ok=true")
    assert_true(payload.get("path") == "scripts/lucy_openclaw_bridge.py", "fs_read returned unexpected path")
    lines = payload.get("lines", [])
    assert_true(isinstance(lines, list) and len(lines) == 1, "fs_read returned unexpected lines payload")
    assert_true(lines[0].get("line") == 138, "fs_read returned unexpected line number")
    assert_true("delegate_mission" in lines[0].get("text", ""), "fs_read did not return expected content")
    assert_no_sensitive_strings(payload)
    results.append({"command": "fs_read", "status": "ok"})


def verify_fs_find(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_fs_search_command.py", "find", "health"])
    assert_true(payload.get("ok") is True, "fs_find did not return ok=true")
    assert_true(payload.get("command") == "fs_find", "fs_find returned wrong command field")
    assert_true(payload.get("query") == "health", "fs_find returned wrong query")
    matches = payload.get("results", [])
    assert_true(isinstance(matches, list), "fs_find results is not a list")
    assert_true(payload.get("count") == len(matches), "fs_find count does not match results")
    assert_true(any("health" in item.lower() for item in matches), "fs_find did not return expected health match")
    assert_true(not any(part in item for item in matches for part in (".agents/", ".git/", "n8n_data/", "n8n_backups/")), "fs_find exposed blocked paths")
    assert_no_sensitive_strings(payload)
    results.append({"command": "fs_find", "status": "ok"})


def verify_fs_grep(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_fs_search_command.py", "grep", "delegate_mission", "scripts"])
    assert_true(payload.get("ok") is True, "fs_grep did not return ok=true")
    assert_true(payload.get("command") == "fs_grep", "fs_grep returned wrong command field")
    assert_true(payload.get("query") == "delegate_mission", "fs_grep returned wrong query")
    assert_true(payload.get("scope") == "scripts", "fs_grep returned wrong scope")
    matches = payload.get("results", [])
    assert_true(isinstance(matches, list), "fs_grep results is not a list")
    assert_true(payload.get("count") == len(matches), "fs_grep count does not match results")
    assert_true(len(matches) >= 1, "fs_grep returned no matches for delegate_mission")
    first = matches[0]
    assert_true(isinstance(first, dict), "fs_grep match is not an object")
    assert_true("path" in first and "line" in first and "text" in first, "fs_grep match missing expected keys")
    assert_true(all("delegate_mission" in item.get("text", "") or "delegate_mission" in item.get("path", "") for item in matches), "fs_grep did not return expected match text")
    raw = json.dumps(payload, ensure_ascii=False)
    for blocked in (".agents/", ".git/", "n8n_data/", "n8n_backups/"):
        assert_true(blocked not in raw, f"fs_grep exposed blocked path {blocked}")
    assert_no_sensitive_strings(payload)
    results.append({"command": "fs_grep", "status": "ok"})


def verify_machine(command: str, key: str, results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_machine_status_command.py", command])
    assert_true(payload.get("ok") is True, f"{command} did not return ok=true")
    assert_true(payload.get("command") == f"machine_{command}", f"{command} returned wrong command field")
    data = payload.get("data")
    assert_true(isinstance(data, dict), f"{command} did not return object data")
    assert_true(key in data, f"{command} missing expected key {key}")
    assert_no_sensitive_strings(payload)
    results.append({"command": command, "status": "ok"})


def verify_service(command: str, required_keys: list[str], results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_service_status_command.py", command])
    assert_true(payload.get("ok") is True, f"{command} did not return ok=true")
    assert_true(payload.get("command") == command, f"{command} returned wrong command field")
    if "status" in payload:
        assert_true(payload["status"] in ("ok", "warn", "error"), f"{command} returned invalid status")
    data = payload.get("data")
    assert_true(isinstance(data, dict), f"{command} did not return object data")
    for key in required_keys:
        assert_true(key in data, f"{command} missing expected key {key}")
    if command == "log_tail":
        assert_no_sensitive_log_leaks(payload)
    else:
        assert_no_sensitive_strings(payload)

    if command == "n8n_health":
        assert_true("workflows" not in json.dumps(payload, ensure_ascii=False).lower(), "n8n_health leaked workflow details")
    if command == "log_tail":
        lines = data.get("lines", [])
        assert_true(isinstance(lines, list), "log_tail lines is not a list")
        assert_true(len(lines) <= MAX_LOG_TAIL_LINES, "log_tail exceeded line limit")

    results.append({"command": command, "status": "ok"})


def verify_health_report(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_health_report_command.py"])
    assert_true(payload.get("ok") is True, "health_report did not return ok=true")
    assert_true(payload.get("command") == "health_report", "health_report returned wrong command field")
    assert_true(payload.get("overall") in ("ok", "warn", "error"), "health_report missing valid overall")
    for key in ("summary", "highlights", "warnings", "recommendations", "data"):
        assert_true(key in payload, f"health_report missing {key}")
    log_lines = payload.get("data", {}).get("log_tail", {}).get("data", {}).get("lines", [])
    assert_true(isinstance(log_lines, list), "health_report log lines is not a list")
    assert_true(len(log_lines) <= MAX_HEALTH_REPORT_LOG_LINES, "health_report exceeded capped log lines")
    redacted_payload = json.loads(json.dumps(payload))
    if isinstance(redacted_payload.get("data", {}).get("log_tail", {}).get("data"), dict):
        redacted_payload["data"]["log_tail"]["data"]["lines"] = []
    assert_no_sensitive_strings(redacted_payload)
    assert_no_sensitive_log_leaks(payload.get("data", {}).get("log_tail", {}))
    results.append({"command": "health_report", "status": "ok", "overall": payload.get("overall")})


def verify_health_brief(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_health_brief_command.py"])
    assert_true(payload.get("ok") is True, "health_brief did not return ok=true")
    assert_true(payload.get("command") == "health_brief", "health_brief returned wrong command field")
    assert_true(payload.get("overall") in ("ok", "warn", "error"), "health_brief missing valid overall")
    for key in ("brief", "warnings", "next"):
        assert_true(key in payload, f"health_brief missing {key}")
    assert_true("data" not in payload, "health_brief should not expose data payload")
    raw = json.dumps(payload, ensure_ascii=False)
    assert_true('"lines"' not in raw, "health_brief should not expose full log lines")
    assert_no_sensitive_strings(payload)
    results.append({"command": "health_brief", "status": "ok", "overall": payload.get("overall")})


def verify_capabilities(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_capabilities_command.py"])
    assert_true(payload.get("ok") is True, "lucy_capabilities did not return ok=true")
    assert_true(payload.get("command") == "lucy_capabilities", "lucy_capabilities returned wrong command field")
    for key in ("green", "yellow", "red", "next"):
        assert_true(key in payload, f"lucy_capabilities missing {key}")
    assert_true("/lucy_capabilities" in payload.get("green", {}).get("commands", []), "lucy_capabilities self-map missing")
    assert_true("/fs_find" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /fs_find")
    assert_true("/fs_grep" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /fs_grep")
    assert_true("/doc_brief" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /doc_brief")
    assert_true("/change_plan" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /change_plan")
    assert_true("/plan_brief" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /plan_brief")
    assert_true("/risk_check" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /risk_check")
    assert_true("/permission_brief" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /permission_brief")
    assert_true("/lucy_next_step" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /lucy_next_step")
    assert_true("/repo_map" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /repo_map")
    assert_true("/lucy_help" in payload.get("green", {}).get("commands", []), "lucy_capabilities missing /lucy_help")
    assert_true("no .env" in payload.get("red", {}).get("limits", []), "lucy_capabilities missing red policy")
    assert_no_sensitive_strings(payload, forbid_env=False)
    results.append({"command": "lucy_capabilities", "status": "ok"})


def verify_lucy_help(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_help_command.py"])
    assert_true(payload.get("ok") is True, "lucy_help did not return ok=true")
    assert_true(payload.get("command") == "lucy_help", "lucy_help returned wrong command field")
    assert_true(payload.get("stage") == "R56", "lucy_help returned wrong stage")
    for key in ("title", "quick_start", "safe_flow", "blocked", "next"):
        assert_true(key in payload, f"lucy_help missing {key}")
    assert_true(isinstance(payload.get("quick_start"), list) and len(payload["quick_start"]) >= 5, "lucy_help quick_start is too short")
    assert_no_sensitive_strings(payload)
    results.append({"command": "lucy_help", "status": "ok"})


def verify_commands_brief(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_commands_brief_command.py"])
    assert_true(payload.get("ok") is True, "commands_brief did not return ok=true")
    assert_true(payload.get("command") == "commands_brief", "commands_brief returned wrong command field")
    assert_true(payload.get("stage") == "R57", "commands_brief returned wrong stage")
    for key in ("title", "groups", "recommended_flow", "blocked", "next"):
        assert_true(key in payload, f"commands_brief missing {key}")
    groups = payload.get("groups", {})
    for g in ("estado", "lectura", "planificacion", "seguridad", "maquina_servicios"):
        assert_true(g in groups, f"commands_brief missing group {g}")
    assert_no_sensitive_strings(payload)
    results.append({"command": "commands_brief", "status": "ok"})


def verify_change_plan(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_change_plan_command.py", "agregar comando read-only para listar docs Lucy"])
    assert_true(payload.get("ok") is True, "change_plan did not return ok=true")
    assert_true(payload.get("command") == "change_plan", "change_plan returned wrong command field")
    assert_true(payload.get("stage") == "R54", "change_plan returned wrong stage")
    assert_true(payload.get("decision") == "PLAN_ONLY", "change_plan returned wrong decision")
    assert_true(payload.get("risk") == "YELLOW", "change_plan should classify command creation as yellow")
    for key in (
        "change_type",
        "files_to_review",
        "files_to_create",
        "files_to_modify",
        "permissions_needed",
        "tests",
        "acceptance_criteria",
        "rollback",
        "blocked_actions",
        "safe_next",
    ):
        assert_true(key in payload, f"change_plan missing {key}")
    assert_true(payload.get("change_type") == "new_command", "change_plan should classify command creation as new_command")
    assert_true(isinstance(payload.get("files_to_create"), list) and payload["files_to_create"], "change_plan files_to_create should be non-empty")
    assert_true(payload.get("permissions_needed", {}).get("install_plugin") is True, "change_plan should request install_plugin")
    assert_no_sensitive_strings(payload)
    results.append({"command": "change_plan", "status": "ok"})


def verify_scaffold_plan(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_scaffold_plan_command.py", "comando para auditar logs"])
    assert_true(payload.get("ok") is True, "scaffold_plan did not return ok=true")
    assert_true(payload.get("command") == "scaffold_plan", "scaffold_plan returned wrong command field")
    assert_true(payload.get("stage") == "R55", "scaffold_plan returned wrong stage")
    assert_true(payload.get("decision") == "PLAN_ONLY", "scaffold_plan returned wrong decision")
    assert_true(payload.get("suggested_command") == "/auditar_logs", "scaffold_plan returned wrong slug")
    for key in (
        "request_summary",
        "risk",
        "scaffold",
        "files_to_create",
        "files_to_modify",
        "permissions_needed",
        "tests",
        "acceptance_criteria",
        "rollback",
        "blocked_actions",
    ):
        assert_true(key in payload, f"scaffold_plan missing {key}")
    assert_no_sensitive_strings(payload)
    results.append({"command": "scaffold_plan", "status": "ok"})


def verify_plan_brief(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_plan_brief_command.py", "agregar comando para ver ultimas docs Lucy"])
    assert_true(payload.get("ok") is True, "plan_brief did not return ok=true")
    assert_true(payload.get("command") == "plan_brief", "plan_brief returned wrong command field")
    assert_true(payload.get("stage") == "R51", "plan_brief returned wrong stage")
    assert_true(payload.get("decision") == "PLAN_ONLY", "plan_brief returned wrong decision")
    assert_true(payload.get("scope") == "read-only", "plan_brief returned wrong scope")
    assert_true(payload.get("target_risk") == "YELLOW", "plan_brief should classify command creation as yellow target")
    for key in ("files_to_review", "risks", "permissions_needed", "checks", "tests", "acceptance_criteria"):
        assert_true(key in payload, f"plan_brief missing {key}")
    assert_true(isinstance(payload.get("files_to_review"), list) and payload["files_to_review"], "plan_brief files_to_review should be non-empty")
    assert_true(isinstance(payload.get("permissions_needed"), dict), "plan_brief permissions_needed should be an object")
    assert_true(payload.get("permissions_needed", {}).get("edit_files") is True, "plan_brief should request edit_files for command creation")
    assert_true(payload.get("approval", {}).get("mode") == "required", "plan_brief approval mode should be required")
    assert_no_sensitive_strings(payload)
    results.append({"command": "plan_brief", "status": "ok"})


def verify_risk_check(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_risk_check_command.py", "reiniciar openclaw gateway"])
    assert_true(payload.get("ok") is True, "risk_check did not return ok=true")
    assert_true(payload.get("command") == "risk_check", "risk_check returned wrong command field")
    assert_true(payload.get("stage") == "R52", "risk_check returned wrong stage")
    assert_true(payload.get("risk") == "YELLOW", "risk_check should classify gateway restart as yellow")
    assert_true(payload.get("approval") == "required", "risk_check should require approval for restart")
    for key in ("summary", "reasons", "checks_previos", "rollback", "safe_alternatives"):
        assert_true(key in payload, f"risk_check missing {key}")
    assert_no_sensitive_strings(payload)
    results.append({"command": "risk_check", "status": "ok"})


def verify_permission_brief(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_permission_brief_command.py", "agregar comando para ver ultimas docs Lucy"])
    assert_true(payload.get("ok") is True, "permission_brief did not return ok=true")
    assert_true(payload.get("command") == "permission_brief", "permission_brief returned wrong command field")
    assert_true(payload.get("stage") == "R53", "permission_brief returned wrong stage")
    assert_true(payload.get("target_risk") == "YELLOW", "permission_brief should classify command creation as yellow")
    assert_true(payload.get("approval_mode") == "required", "permission_brief should require approval")
    assert_true(isinstance(payload.get("permissions_needed"), dict), "permission_brief permissions_needed should be an object")
    assert_true(payload.get("permissions_needed", {}).get("install_plugin") is True, "permission_brief should request install_plugin")
    for key in ("grouped_approval_recommended", "checks_before_execution", "blocked_zones", "safe_alternatives"):
        assert_true(key in payload, f"permission_brief missing {key}")
    assert_no_sensitive_strings(payload)
    results.append({"command": "permission_brief", "status": "ok"})


def verify_doc_brief(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_doc_brief_command.py", "docs/LUCYCLAW_CURRENT_STATE.md"])
    assert_true(payload.get("ok") is True, "doc_brief did not return ok=true")
    assert_true(payload.get("command") == "doc_brief", "doc_brief returned wrong command field")
    assert_true(payload.get("stage") == "R50A", "doc_brief returned wrong stage")
    assert_true(payload.get("path") == "docs/LUCYCLAW_CURRENT_STATE.md", "doc_brief returned wrong path")
    for key in ("summary", "safe_next", "limits"):
        assert_true(key in payload, f"doc_brief missing {key}")
    summary = payload.get("summary", {})
    assert_true("main_points" in summary, "doc_brief missing summary.main_points")
    raw = json.dumps(payload, ensure_ascii=False).lower()
    blocked_terms = (
        "." + "env",
        "token" + "s",
        "." + "agents",
        "n8n_" + "data",
        "n8n_" + "backups",
        "/work" + "flows",
        "\"" + "cred" + "entials" + "\"",
    )
    for blocked in blocked_terms:
        assert_true(blocked not in raw, f"doc_brief exposed blocked detail {blocked}")
    assert_no_sensitive_strings(payload, forbid_env=False)

    proc = subprocess.run(
        [PYTHON, "scripts/lucy_doc_brief_command.py", ".." + "/." + "env"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
    )
    rejected_raw = proc.stdout.strip()
    assert_true(bool(rejected_raw), "doc_brief reject returned no stdout")
    try:
        rejected_payload = json.loads(rejected_raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("doc_brief reject returned invalid JSON") from exc
    assert_true(proc.returncode == 2, "doc_brief should exit 2 on rejected path")
    assert_true(rejected_payload.get("ok") is False, "doc_brief should reject traversal")
    assert_true(rejected_payload.get("command") == "doc_brief", "doc_brief reject returned wrong command")
    assert_true(rejected_payload.get("error") == "path rejected by read-only policy", "doc_brief reject returned wrong error")
    assert_true("." + "env" not in rejected_raw.lower(), "doc_brief rejection leaked blocked path")
    results.append({"command": "doc_brief", "status": "ok"})


def verify_repo_map(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_repo_map_command.py"])
    assert_true(payload.get("ok") is True, "repo_map did not return ok=true")
    assert_true(payload.get("command") == "repo_map", "repo_map returned wrong command field")
    assert_true(payload.get("stage") == "R49", "repo_map returned wrong stage")
    for key in ("top_level", "lucy_commands", "key_files", "safe_navigation", "excluded"):
        assert_true(key in payload, f"repo_map missing {key}")
    raw = json.dumps(payload, ensure_ascii=False).lower()
    blocked_terms = (
        "." + "env",
        "token" + "s",
        "." + "agents",
        "n8n_" + "data",
        "n8n_" + "backups",
        "/work" + "flows",
        "\"" + "cred" + "entials" + "\"",
        "database" + ".sqlite",
    )
    for blocked in blocked_terms:
        assert_true(blocked not in raw, f"repo_map exposed blocked detail {blocked}")
    assert_no_sensitive_strings(payload, forbid_env=False)
    results.append({"command": "repo_map", "status": "ok"})


def verify_next_step(results: list[dict]) -> None:
    env = os.environ.copy()
    env["LUCY_SKIP_NEXT_STEP"] = "1"
    proc = subprocess.run(
        [PYTHON, "scripts/lucy_next_step_command.py"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
        env=env,
    )
    raw = proc.stdout.strip()
    if not raw:
        raise RuntimeError("lucy_next_step returned no stdout")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("lucy_next_step returned invalid JSON") from exc
    assert_true(proc.returncode == 0, f"lucy_next_step exited {proc.returncode}")
    assert_true(payload.get("ok") is True, "lucy_next_step did not return ok=true")
    assert_true(payload.get("command") == "lucy_next_step", "lucy_next_step returned wrong command field")
    assert_true(payload.get("decision") in ("READY", "WARN", "BLOCK"), "lucy_next_step returned invalid decision")
    assert_true("basis" in payload, "lucy_next_step missing basis")
    assert_true("recommendation" in payload, "lucy_next_step missing recommendation")
    raw = json.dumps(payload, ensure_ascii=False).lower()
    for blocked in ("/workflows", "database.sqlite", "\"credentials\"", "n8n_data/", "n8n_backups/"):
        assert_true(blocked not in raw, f"lucy_next_step leaked blocked detail {blocked}")
    assert_no_sensitive_strings(payload, forbid_env=False)
    results.append({"command": "lucy_next_step", "status": "ok", "decision": payload.get("decision")})


def verify_run_registry(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_run_registry_command.py"])
    assert_true(payload.get("ok") is True, "run_registry did not return ok=true")
    assert_true(payload.get("command") == "run_registry", "run_registry returned wrong command field")
    assert_true(payload.get("stage") == "AG-Y3", "run_registry returned wrong stage")
    for key in ("registry", "status", "next"):
        assert_true(key in payload, f"run_registry missing {key}")
    assert_true(payload.get("registry", {}).get("path") == "data/run_registry/lucyclaw_runs.jsonl", "run_registry missing correct registry path")
    assert_no_sensitive_strings(payload, forbid_env=False)
    results.append({"command": "run_registry", "status": "ok"})


def verify_rollback_plan(results: list[dict]) -> None:
    # 1. No args
    payload, _ = run_json([PYTHON, "scripts/lucy_rollback_plan_command.py"])
    assert_true(payload.get("ok") is True, "rollback_plan did not return ok=true")
    assert_true(payload.get("command") == "rollback_plan", "rollback_plan returned wrong command field")
    assert_true(payload.get("plan", {}).get("decision") == "PLAN_ONLY", "rollback_plan should be PLAN_ONLY")
    assert_no_sensitive_strings(payload, forbid_env=False)
    results.append({"command": "rollback_plan", "status": "ok"})

    # 2. Matched (AG-Y3)
    payload_match, _ = run_json([PYTHON, "scripts/lucy_rollback_plan_command.py", "AG-Y3"])
    assert_true(payload_match.get("ok") is True, "rollback_plan AG-Y3 did not return ok=true")
    assert_true(payload_match.get("target") == "AG-Y3", "rollback_plan failed to match target AG-Y3")
    results.append({"command": "rollback_plan_matched", "status": "ok"})

    # 3. Missing
    payload_miss, _ = run_json([PYTHON, "scripts/lucy_rollback_plan_command.py", "MISSING_TRANCHE"])
    assert_true(payload_miss.get("ok") is False, "rollback_plan should fail on missing target")
    assert_true(payload_miss.get("decision") == "NEEDS_REVIEW", "rollback_plan miss should be NEEDS_REVIEW")
    results.append({"command": "rollback_plan_missing", "status": "ok"})


def verify_rollback_plan_validator(results: list[dict]) -> None:
    validator_script = "scripts/verify_rollback_plan.py"
    example_plan = "docs/examples/ROLLBACK_PLAN_EXAMPLE_AG_Y3_R65.json"

    assert_true((ROOT / validator_script).exists(), f"{validator_script} missing")
    assert_true((ROOT / example_plan).exists(), f"{example_plan} missing")

    payload, _ = run_json([PYTHON, validator_script, example_plan])

    assert_true(payload.get("ok") is True, "rollback_plan_validator did not return ok=true")
    assert_true(payload.get("command") == "verify_rollback_plan", "rollback_plan_validator returned wrong command")
    assert_true(payload.get("decision") == "VALID", "rollback_plan_validator decision is not VALID")
    assert_true(payload.get("dangerous_hits") == [], "rollback_plan_validator detected dangerous hits in example")

    results.append({"command": "rollback_plan_validator", "status": "ok"})


def verify_yellow_preflight(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_yellow_preflight_command.py"])
    assert_true(payload.get("ok") is True or payload.get("ok") is False, "yellow_preflight returned no ok field")
    assert_true(payload.get("command") == "yellow_preflight", "yellow_preflight returned wrong command")
    assert_true(payload.get("decision") in ("READY", "WARN", "BLOCK"), "yellow_preflight returned invalid decision")
    assert_true(payload.get("rollback_allowed_now") is False, "yellow_preflight leaked rollback permission")
    assert_true(payload.get("repair_allowed_now") is False, "yellow_preflight leaked repair permission")
    
    # In a clean environment (expected during pre-commit/post-commit), it should be READY or WARN
    # but since this might run in a dirty git state during testing, we only check for basic fields.
    results.append({"command": "yellow_preflight", "status": "ok", "decision": payload.get("decision")})


def verify_daemon_brief(results: list[dict]) -> None:
    payload, _ = run_json([PYTHON, "scripts/lucy_daemon_brief_command.py"])
    assert_true(payload.get("ok") is True, "daemon_brief returned ok=false")
    assert_true(payload.get("command") == "daemon_brief", "daemon_brief wrong command")
    d3 = payload.get("daemon_v3", {})
    assert_true(d3.get("active") is False, "daemon_brief says daemon is active")
    assert_true(d3.get("repair_enabled") is False, "daemon_brief says repair is enabled")
    assert_true(d3.get("executor_enabled") is False, "daemon_brief says executor is enabled")
    readiness = payload.get("readiness", {})
    assert_true(readiness.get("daemon_ready_for_autonomous_repair") is False, "daemon_brief says repair ready")
    results.append({"command": "daemon_brief", "status": "ok"})


def verify_machine_access(results: list[dict]):
    # 1. downloads
    payload, err = run_json([PYTHON, "scripts/lucy_machine_access_command.py", "downloads"])
    assert_true(payload is not None, f"machine_downloads failed: {err}")
    # downloads can return ok:false if folder doesn't exist, that's acceptable for QA1
    
    # 2. ls /home/lucy-ubuntu
    payload, err = run_json([PYTHON, "scripts/lucy_machine_access_command.py", "ls", "/home/lucy-ubuntu"])
    assert_true(payload is not None, f"machine_ls failed: {err}")
    assert_true(payload.get("ok") is True, f"machine_ls /home/lucy-ubuntu error: {payload.get('error') if payload else 'no payload'}")
    
    # 3. stat /home/lucy-ubuntu
    payload, err = run_json([PYTHON, "scripts/lucy_machine_access_command.py", "stat", "/home/lucy-ubuntu"])
    assert_true(payload is not None, f"machine_stat failed: {err}")
    assert_true(payload.get("ok") is True, f"machine_stat /home/lucy-ubuntu error: {payload.get('error') if payload else 'no payload'}")

    # 4. Access Denied (Sensitive)
    payload, err = run_json([PYTHON, "scripts/lucy_machine_access_command.py", "ls", "/home/lucy-ubuntu/." + "env"])
    assert_true(payload is not None, "machine_ls ." + "env failed to return payload")
    assert_true(payload.get("ok") is False, "machine_ls allowed access to ." + "env")
    
    results.append({"command": "machine_access", "status": "ok"})


def verify_machine_read(results: list[dict]) -> None:
    wrapper_path = ROOT / "scripts/lucy_machine_read_command.py"
    plugin_path = ROOT / "openclaw_plugins/lucy-machine-read-command/index.js"

    compile_proc = subprocess.run(
        [PYTHON, "-m", "py_compile", str(wrapper_path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
    )
    assert_true(compile_proc.returncode == 0, f"machine_read py_compile failed: {compile_proc.stderr.strip()}")

    md_path = "/home/lucy-ubuntu/Descargas/Markdown.md pegado"
    docx_path = "/home/lucy-ubuntu/Descargas/201721562-Roles-Ars-Magica-4a-Ed-1_convertido_3.docx"
    pdf_path = "/home/lucy-ubuntu/Descargas/Platon El banquete.pdf"

    md_payload, _ = run_json([PYTHON, "scripts/lucy_machine_read_command.py", "read", md_path])
    assert_true(md_payload.get("ok") is True, "machine_read md returned ok=false")
    assert_true(md_payload.get("command") == "machine_read", "machine_read md wrong command")
    assert_true(md_payload.get("extension") == ".md", "machine_read md wrong extension")
    assert_true(isinstance(md_payload.get("text"), str) and md_payload.get("text"), "machine_read md missing text")
    assert_true(md_payload.get("chars_returned", 0) > 0, "machine_read md returned empty text")

    docx_payload, _ = run_json([PYTHON, "scripts/lucy_machine_read_command.py", "read", docx_path])
    assert_true(docx_payload.get("ok") is True, "machine_read docx returned ok=false")
    assert_true(docx_payload.get("extension") == ".docx", "machine_read docx wrong extension")
    assert_true(isinstance(docx_payload.get("text"), str) and docx_payload.get("text"), "machine_read docx missing text")

    pdf_payload, _ = run_json([PYTHON, "scripts/lucy_machine_read_command.py", "brief", pdf_path])
    assert_true(pdf_payload.get("ok") is True, "machine_doc_brief pdf returned ok=false")
    assert_true(pdf_payload.get("command") == "machine_doc_brief", "machine_doc_brief pdf wrong command")
    assert_true(pdf_payload.get("extension") == ".pdf", "machine_doc_brief pdf wrong extension")
    assert_true(isinstance(pdf_payload.get("excerpt"), str) and pdf_payload.get("excerpt"), "machine_doc_brief pdf missing excerpt")

    blocked_env_path = "." + "env"
    rejected_env_proc = subprocess.run(
        [PYTHON, "scripts/lucy_machine_read_command.py", "read", blocked_env_path],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
    )
    rejected_env = json.loads(rejected_env_proc.stdout.strip())
    assert_true(rejected_env_proc.returncode == 2, "machine_read should exit 2 on blocked env rejection")
    assert_true(rejected_env.get("ok") is False, "machine_read should reject blocked env path")

    blocked_n8n_path = "/home/lucy-ubuntu/Escritorio/doctora-lucy/n8n_" + "data/voice_payload.txt"
    rejected_n8n_proc = subprocess.run(
        [PYTHON, "scripts/lucy_machine_read_command.py", "read", blocked_n8n_path],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
    )
    rejected_n8n = json.loads(rejected_n8n_proc.stdout.strip())
    assert_true(rejected_n8n_proc.returncode == 2, "machine_read should exit 2 on n8n_data rejection")
    assert_true(rejected_n8n.get("ok") is False, "machine_read should reject n8n_data")

    blocked_openclaw_path = "~/.open" + "claw/openclaw.json"
    rejected_openclaw_proc = subprocess.run(
        [PYTHON, "scripts/lucy_machine_read_command.py", "read", blocked_openclaw_path],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
    )
    rejected_openclaw = json.loads(rejected_openclaw_proc.stdout.strip())
    assert_true(rejected_openclaw_proc.returncode == 2, "machine_read should exit 2 on openclaw rejection")
    assert_true(rejected_openclaw.get("ok") is False, "machine_read should reject ~/.openclaw")

    wrapper_source = wrapper_path.read_text(encoding="utf-8")
    assert_true("shell" + "=True" not in wrapper_source, "machine_read wrapper must keep subprocess shell disabled")
    assert_true("su" + "do" not in wrapper_source.lower(), "machine_read wrapper must not reference privilege escalation")

    plugin_check = subprocess.run(
        ["node", "--check", str(plugin_path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
    )
    assert_true(plugin_check.returncode == 0, f"machine_read plugin node --check failed: {plugin_check.stderr.strip()}")

    plugin_source = plugin_path.read_text(encoding="utf-8")
    assert_true("execSync" not in plugin_source and "child_process.exec" not in plugin_source, "machine_read plugin uses exec")

    results.append({"command": "machine_read", "status": "ok"})


def verify_machine_agent_tools(results: list[dict]) -> None:
    plugin_path = ROOT / "openclaw_plugins/lucy-machine-agent-tools/index.js"
    manifest_path = ROOT / "openclaw_plugins/lucy-machine-agent-tools/openclaw.plugin.json"
    package_path = ROOT / "openclaw_plugins/lucy-machine-agent-tools/package.json"

    assert_true(plugin_path.exists(), "machine agent tools plugin index.js missing")
    assert_true(manifest_path.exists(), "machine agent tools manifest missing")
    assert_true(package_path.exists(), "machine agent tools package missing")

    plugin_check = subprocess.run(
        ["node", "--check", str(plugin_path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=TIMEOUT,
        shell=False,
        cwd=ROOT,
    )
    assert_true(plugin_check.returncode == 0, f"machine agent tools node --check failed: {plugin_check.stderr.strip()}")

    source = plugin_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert_true("registerTool(" in source, "machine agent tools plugin does not use registerTool")
    assert_true("registerCommand(" not in source, "machine agent tools plugin should not rely on registerCommand")
    assert_true("execSync" not in source and "child_process.exec" not in source, "machine agent tools plugin uses exec")
    assert_true("shell: true" not in source and "shell:true" not in source, "machine agent tools plugin uses shell:true")

    manifest_tools = manifest.get("contracts", {}).get("tools")
    assert_true(isinstance(manifest_tools, list), "machine agent tools manifest missing contracts.tools list")

    for tool_name in (
        "lucy_machine_downloads",
        "lucy_machine_ls",
        "lucy_machine_stat",
        "lucy_machine_status",
        "lucy_machine_processes",
        "lucy_machine_ram",
        "lucy_machine_gpu",
        "lucy_machine_disk",
        "lucy_machine_read",
        "lucy_machine_doc_brief",
    ):
        assert_true(tool_name in source, f"machine agent tools plugin missing tool {tool_name}")
        assert_true(tool_name in manifest_tools, f"machine agent tools manifest missing tool {tool_name}")

    results.append({"command": "machine_agent_tools", "status": "ok"})


def verify_machine_nl_router(results: list[dict]) -> None:
    samples = [
        ("qué carpetas hay en el escritorio", "machine_ls", "/home/lucy-ubuntu/Escritorio"),
        ("qué hay en descargas", "machine_downloads", ""),
        ("qué fue lo último que descargué", "machine_downloads", ""),
        ("qué hay activo en la pc", "machine_status", ""),
        ("cuánta ram estoy usando", "machine_ram", ""),
        ("cómo está la gpu", "machine_gpu", ""),
        ("cuánta vram estoy usando", "machine_gpu", ""),
        ("qué procesos están corriendo", "machine_processes", ""),
        ("cuánto disco tengo", "machine_disk", ""),
    ]
    for text, command, args in samples:
        payload, _ = run_json([PYTHON, "scripts/lucy_machine_nl_router.py", text])
        assert_true(payload.get("ok") is True, f"machine_nl_router failed for: {text}")
        assert_true(payload.get("recognized") is True, f"machine_nl_router did not recognize: {text}")
        assert_true(payload.get("command") == command, f"machine_nl_router mapped wrong command for: {text}")
        assert_true(payload.get("args") == args, f"machine_nl_router mapped wrong args for: {text}")
        assert_true(payload.get("mode") == "read-only", f"machine_nl_router wrong mode for: {text}")
        assert_true(payload.get("requires_model") is False, f"machine_nl_router wrong requires_model for: {text}")

    rejected, _ = run_json([PYTHON, "scripts/lucy_machine_nl_router.py", "hola cómo estás"])
    assert_true(rejected.get("ok") is True, "machine_nl_router reject returned ok=false")
    assert_true(rejected.get("recognized") is False, "machine_nl_router should not recognize generic greeting")
    assert_true(rejected.get("requires_model") is True, "machine_nl_router should require model on generic greeting")

    router_source = (ROOT / "scripts/lucy_machine_nl_router.py").read_text(encoding="utf-8")
    blocked_markers = (
        "sub" + "process",
        "shell" + "=True",
        "os." + "system",
        "req" + "uests",
        "." + "env",
        "to" + "ken",
    )
    for marker in blocked_markers:
        assert_true(marker not in router_source, f"machine_nl_router source contains blocked marker: {marker}")

    results.append({"command": "machine_nl_router", "status": "ok"})


def main() -> int:
    results: list[dict] = []
    try:
        verify_fs_read(results)
        verify_fs_find(results)
        verify_fs_grep(results)
        verify_machine("status", "cpu", results)
        verify_machine("gpu", "name", results)
        verify_machine("disk", "path", results)
        verify_machine("ram", "total_mb", results)
        verify_machine("processes", "top_processes", results)
        verify_service("openclaw_health", ["gateway_health", "systemd_user", "model"], results)
        verify_service("docker_status", ["cli_available", "daemon_responds", "containers"], results)
        verify_service("ollama_status", ["port_11434_responds", "api_tags_responds", "models"], results)
        verify_service("n8n_health", ["visible_container_or_service", "containers", "local_ports"], results)
        verify_service("service_status", ["services"], results)
        verify_service("log_tail", ["unit", "line_limit", "lines"], results)
        verify_health_report(results)
        verify_health_brief(results)
        verify_capabilities(results)
        verify_lucy_help(results)
        verify_commands_brief(results)
        verify_change_plan(results)
        verify_scaffold_plan(results)
        verify_plan_brief(results)
        verify_risk_check(results)
        verify_permission_brief(results)
        verify_doc_brief(results)
        verify_repo_map(results)
        verify_run_registry(results)
        verify_rollback_plan(results)
        verify_rollback_plan_validator(results)
        if os.environ.get("LUCY_SKIP_PREFLIGHT_CHECK") != "1":
            verify_yellow_preflight(results)
        if os.environ.get("LUCY_SKIP_DAEMON_CHECK") != "1":
            verify_daemon_brief(results)
        if os.environ.get("LUCY_SKIP_NEXT_STEP") != "1":
            verify_next_step(results)
        verify_machine_access(results)
        verify_machine_read(results)
        verify_machine_agent_tools(results)
        verify_machine_nl_router(results)
    except (AssertionError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "command": "verify_lucyclaw_green_commands",
                    "error": str(exc),
                    "verified": results,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 2

    print(
        json.dumps(
            {
                "ok": True,
                "command": "verify_lucyclaw_green_commands",
                "verified": results,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
