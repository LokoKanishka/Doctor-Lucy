#!/usr/bin/env python3
"""Run Registry command for LucyClaw."""

import json
import os
import sys

REGISTRY_PATH = "data/run_registry/lucyclaw_runs.jsonl"
STAGE = "AG-Y3"

def build_payload(argv: list[str]) -> tuple[dict, int]:
    if len(argv) != 1:
        return {
            "ok": False,
            "command": "run_registry",
            "stage": STAGE,
            "error": "arguments are not supported",
            "decision": "NEEDS_REVIEW"
        }, 2

    if not os.path.exists(REGISTRY_PATH):
        return {
            "ok": False,
            "command": "run_registry",
            "stage": STAGE,
            "error": f"registry not found at {REGISTRY_PATH}",
            "decision": "NEEDS_REVIEW"
        }, 1

    total_records = 0
    valid_records = 0
    last_healthy_run = None

    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_records += 1
                try:
                    record = json.loads(line)
                    valid_records += 1
                    
                    if (record.get("final_decision") == "CLOSED" and
                        record.get("qa1_post") == "ok" and
                        record.get("sec1_post") == "ok" and
                        record.get("lucy_next_step_post") != "BLOCK" and
                        record.get("sensitive_clean") is True and
                        record.get("envelope_validated") is True):
                        
                        last_healthy_run = {
                            "run_id": record.get("run_id"),
                            "tranche_id": record.get("tranche_id"),
                            "target_commit": record.get("target_commit"),
                            "risk_level": record.get("risk_level"),
                            "final_decision": record.get("final_decision")
                        }
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        return {
            "ok": False,
            "command": "run_registry",
            "stage": STAGE,
            "error": f"failed to read registry: {str(e)}",
            "decision": "NEEDS_REVIEW"
        }, 1

    return {
        "ok": True,
        "command": "run_registry",
        "stage": STAGE,
        "registry": {
            "path": REGISTRY_PATH,
            "total_records": total_records,
            "valid_records": valid_records,
            "last_healthy_run": last_healthy_run
        },
        "status": {
            "read_only": True,
            "runtime_touched": False,
            "sensitive_paths_excluded": True
        },
        "next": "Usar /lucy_next_step antes de iniciar un tramo amarillo."
    }, 0

def main(argv: list[str]) -> int:
    payload, code = build_payload(argv)
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code

if __name__ == "__main__":
    sys.exit(main(sys.argv))
