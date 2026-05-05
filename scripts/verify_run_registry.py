#!/usr/bin/env python3
import sys
import json
import os

REQUIRED_FIELDS = [
    "registry_version", "run_id", "tranche_id", "title", "date",
    "operator", "risk_level", "final_decision", "base_commit",
    "target_commit", "branch", "repo_path", "evidence_path",
    "envelope_validated", "qa1_post", "sec1_post", "lucy_next_step_post",
    "runtime_touched", "restart_count", "sensitive_clean",
    "voice_report_status"
]

ALLOWED_STATES = [
    "CLOSED", "BLOCKED", "FAILED_SAFE", "NEEDS_REVIEW", "REPEAT_REQUIRED"
]

FORBIDDEN_PATHS = [
    ".env", "n8n_data", "n8n_backups", "memoria", "boveda", "vault",
    "tokens", "credentials", ".agents"
]

def check_path_policy(path):
    path_parts = path.split(os.sep)
    for forbidden in FORBIDDEN_PATHS:
        if forbidden in path_parts or any(forbidden in p for p in path_parts):
             return False
    return True

def verify_registry(filepath):
    result = {
        "ok": False,
        "command": "verify_run_registry",
        "checked_path": filepath,
        "total_records": 0,
        "valid_records": 0,
        "invalid_records": [],
        "last_healthy_run": None,
        "decision": "INVALID"
    }

    if not os.path.exists(filepath):
        result["invalid_records"].append({"line": 0, "error": "File not found"})
        return result

    abs_path = os.path.abspath(filepath)
    if not check_path_policy(filepath) or not check_path_policy(abs_path):
        result["invalid_records"].append({"line": 0, "error": "Path violates security policy"})
        return result

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        result["invalid_records"].append({"line": 0, "error": f"Cannot read file: {str(e)}"})
        return result

    result["total_records"] = len(lines)
    healthy_runs = []

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        try:
            record = json.loads(line)
        except json.JSONDecodeError as e:
            result["invalid_records"].append({"line": i, "error": f"Invalid JSON: {str(e)}"})
            continue

        missing = [f for f in REQUIRED_FIELDS if f not in record]
        if missing:
            result["invalid_records"].append({"line": i, "error": f"Missing fields: {missing}"})
            continue

        decision = record.get("final_decision")
        if decision not in ALLOWED_STATES:
            result["invalid_records"].append({"line": i, "error": f"Invalid final_decision: {decision}"})
            continue

        if decision == "CLOSED":
            if not record.get("sensitive_clean"):
                result["invalid_records"].append({"line": i, "error": "CLOSED but sensitive_clean is false"})
                continue
            if record.get("lucy_next_step_post") == "BLOCK":
                result["invalid_records"].append({"line": i, "error": "CLOSED but lucy_next_step_post is BLOCK"})
                continue

        result["valid_records"] += 1

        # Check for healthy run
        if (record.get("final_decision") == "CLOSED" and
            record.get("qa1_post") == "ok" and
            record.get("sec1_post") == "ok" and
            record.get("lucy_next_step_post") != "BLOCK" and
            record.get("sensitive_clean") == True and
            record.get("envelope_validated") == True):
            healthy_runs.append(record)

    if healthy_runs:
        result["last_healthy_run"] = healthy_runs[-1]

    if not result["invalid_records"]:
        result["ok"] = True
        result["decision"] = "VALID"

    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "ok": False,
            "command": "verify_run_registry",
            "checked_path": "",
            "invalid_records": [{"line": 0, "error": "No path provided"}],
            "decision": "INVALID"
        }))
        sys.exit(1)

    filepath = sys.argv[1]
    res = verify_registry(filepath)
    print(json.dumps(res, indent=2))
