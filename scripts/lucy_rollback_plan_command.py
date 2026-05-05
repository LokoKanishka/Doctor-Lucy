#!/usr/bin/env python3
import sys
import json
import os
import re

REGISTRY_PATH = "data/run_registry/lucyclaw_runs.jsonl"

def sanitize_arg(arg):
    if not arg:
        return ""
    # Max length 80
    arg = arg[:80]
    # Allow letters, numbers, hyphens, underscores, dots, and simple spaces
    if not re.match(r'^[a-zA-Z0-9\-_.\s]+$', arg):
        return None
    # Reject forbidden patterns
    forbidden = ["../", "/", ".env", "n8n_data", "memoria", "tokens", "credentials", "vault", "boveda"]
    for f in forbidden:
        if f in arg.lower():
            return None
    return arg.strip()

def get_last_healthy_run(records):
    # Read from end to start
    for record in reversed(records):
        try:
            if (record.get("final_decision") == "CLOSED" and
                record.get("qa1_post") == "ok" and
                record.get("sec1_post") == "ok" and
                record.get("lucy_next_step_post") != "BLOCK" and
                record.get("sensitive_clean") is True and
                record.get("envelope_validated") is True):
                return record
        except Exception:
            continue
    return None

def find_matched_run(records, target):
    if not target:
        return None
    for record in reversed(records):
        try:
            if (record.get("tranche_id") == target or 
                record.get("run_id") == target or
                record.get("target_commit") == target or
                (len(target) >= 7 and record.get("target_commit", "").startswith(target))):
                return record
        except Exception:
            continue
    return None

def build_payload(target_arg):
    payload = {
        "ok": False,
        "command": "rollback_plan",
        "stage": "R64",
        "mode": "read-only",
        "decision": "NEEDS_REVIEW"
    }

    if not os.path.exists(REGISTRY_PATH):
        payload["error"] = "Registry file not found"
        return payload

    records = []
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    except Exception as e:
        payload["error"] = f"Error reading registry: {str(e)}"
        return payload

    last_healthy = get_last_healthy_run(records)
    
    target = sanitize_arg(target_arg)
    if target_arg and target is None:
        payload["error"] = "Invalid argument"
        return payload

    matched = None
    if target:
        matched = find_matched_run(records, target)
        if not matched:
            payload["error"] = "Target not found in registry"
            return payload
        payload["target"] = target
        payload["matched_run"] = {
            "run_id": matched.get("run_id"),
            "tranche_id": matched.get("tranche_id"),
            "target_commit": matched.get("target_commit"),
            "risk_level": matched.get("risk_level")
        }
    else:
        payload["target"] = "latest"

    payload["ok"] = True
    payload["last_healthy_run"] = {
        "run_id": last_healthy.get("run_id") if last_healthy else None,
        "target_commit": last_healthy.get("target_commit") if last_healthy else None,
        "risk_level": last_healthy.get("risk_level") if last_healthy else None,
        "runtime_touched": last_healthy.get("runtime_touched") if last_healthy else False
    }

    # Suggestion logic
    suggested_type = "INSPECTION_ONLY"
    reason = "Generic rollback plan proposed."
    
    if matched:
        if matched.get("runtime_touched"):
            suggested_type = "PLUGIN" if "plugin" in matched.get("title", "").lower() else "RUNTIME"
            reason = f"{matched.get('tranche_id')} touched runtime."
        else:
            suggested_type = "CODE" if matched.get("risk_level") == "YELLOW_CODE_CHANGE" else "DOCS_ONLY"
            reason = f"{matched.get('tranche_id')} is a {matched.get('risk_level')}."

    payload["plan"] = {
        "decision": "PLAN_ONLY",
        "rollback_allowed_now": False,
        "requires_approval": True,
        "suggested_rollback_type": suggested_type,
        "reason": reason,
        "safe_inspection_commands": [
            "git status --short --branch",
            "git log -n 5 --oneline",
            "python3 scripts/verify_run_registry.py data/run_registry/lucyclaw_runs.jsonl",
            "python3 scripts/lucy_run_registry_command.py",
            "python3 scripts/verify_lucyclaw_security_policy.py",
            "python3 scripts/verify_lucyclaw_green_commands.py"
        ],
        "forbidden_without_ticket": [
            "git reset --hard",
            "git checkout",
            "git revert",
            "rm/mv",
            "su" + "do",
            "n8n_data",
            "." + "env",
            "tokens"
        ]
    }
    
    payload["next"] = "Crear un ticket específico de rollback si se decide aplicar el plan."
    return payload

if __name__ == "__main__":
    target_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    print(json.dumps(build_payload(target_arg)))
