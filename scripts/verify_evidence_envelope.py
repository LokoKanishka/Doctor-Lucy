#!/usr/bin/env python3
import sys
import json
import os
import re

REQUIRED_FIELDS = [
    "envelope_version", "tranche_id", "tranche_title", "date", "operator",
    "supervisor", "repo_path", "branch", "base_commit", "target_commit",
    "risk_level", "approval_mode", "ticket_summary", "allowed_scope",
    "forbidden_scope", "files_created", "files_modified", "files_deleted",
    "runtime_touched", "restart_count", "commands_run", "git_status_initial",
    "qa1_pre", "sec1_pre", "lucy_next_step_pre", "git_status_final",
    "qa1_post", "sec1_post", "lucy_next_step_post", "sensitive_confirmations",
    "voice_report_status", "final_decision", "next_recommendation"
]

FORBIDDEN_PATHS = [
    ".env", "n8n_data", "n8n_backups", "memoria", "boveda", "vault",
    "tokens", "credentials", ".agents"
]

FORBIDDEN_STRINGS = [
    "OPENAI_API_KEY=", "N8N_", "TOKEN=", "SECRET=", "PASSWORD=",
    "PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "api_key"
]

def check_path_policy(path):
    path_parts = path.split(os.sep)
    for forbidden in FORBIDDEN_PATHS:
        if forbidden in path_parts or any(forbidden in p for p in path_parts):
             return False
    return True

def verify_envelope(filepath):
    result = {
        "ok": False,
        "command": "verify_evidence_envelope",
        "checked_path": filepath,
        "missing_required_fields": [],
        "forbidden_hits": [],
        "decision": "INVALID"
    }
    
    if not os.path.exists(filepath):
        result["forbidden_hits"].append("File not found")
        return result
        
    abs_path = os.path.abspath(filepath)
    # Ensure it's not trying to escape repo implicitly
    if not check_path_policy(filepath) or not check_path_policy(abs_path):
        result["forbidden_hits"].append("Path violates security policy")
        return result
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result["forbidden_hits"].append(f"Cannot read file: {str(e)}")
        return result

    # Check for forbidden strings
    for f_str in FORBIDDEN_STRINGS:
        if f_str in content:
            result["forbidden_hits"].append(f"Found sensitive string: {f_str}")
            
    # Check for required fields
    for field in REQUIRED_FIELDS:
        # Looking for field names in markdown like "- field:" or "* field:" or in JSON
        # This regex matches the field name surrounded by common envelope structures
        # or just simply checks if the exact string exists (often as a key in JSON or Markdown list)
        pattern = re.compile(r'\b' + re.escape(field) + r'\b', re.IGNORECASE)
        if not pattern.search(content):
            result["missing_required_fields"].append(field)
            
    if not result["missing_required_fields"] and not result["forbidden_hits"]:
        result["ok"] = True
        result["decision"] = "VALID"
        
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "ok": False, 
            "command": "verify_evidence_envelope", 
            "checked_path": "", 
            "missing_required_fields": [], 
            "forbidden_hits": ["No path provided"], 
            "decision": "INVALID"
        }))
        sys.exit(1)
        
    filepath = sys.argv[1]
    res = verify_envelope(filepath)
    print(json.dumps(res, indent=2))
    # We exit with 0 to allow bash scripts to parse the JSON output even if INVALID,
    # or we could exit with 1 if INVALID. Let's exit 0 so JSON is always printed and parser decides.
    # Actually, QA scripts usually exit 0 and let caller read JSON.
