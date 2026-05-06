#!/usr/bin/env python3
"""Yellow Preflight command for LucyClaw."""

import json
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = "python3"
TIMEOUT = 60  # QA1 can be slow

def run_cmd(args):
    env = os.environ.copy()
    env["LUCY_SKIP_PREFLIGHT_CHECK"] = "1"
    env["LUCY_SKIP_DAEMON_CHECK"] = "1"
    try:
        proc = subprocess.run(
            args,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=TIMEOUT,
            shell=False,
            cwd=ROOT,
            env=env
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def run_json_cmd(args):
    rc, stdout, stderr = run_cmd(args)
    if not stdout:
        return None, f"exit {rc}: {stderr or 'no output'}"
    try:
        return json.loads(stdout), None
    except json.JSONDecodeError:
        return None, f"invalid json: {stdout[:100]}"

def main():
    checks = {}
    failed_checks = []

    # 1. git status
    rc, stdout, stderr = run_cmd(["git", "status", "--short", "--branch"])
    if rc == 0 and len(stdout.splitlines()) == 1: # Only branch line like "## branch...remote"
        checks["git_clean"] = "ok"
    else:
        checks["git_clean"] = "dirty"
        failed_checks.append("git_clean")

    # 2. registry validation
    registry_payload, err = run_json_cmd([PYTHON, "scripts/verify_run_registry.py", "data/run_registry/lucyclaw_runs.jsonl"])
    if registry_payload and registry_payload.get("decision") == "VALID":
        checks["registry"] = "ok"
    else:
        checks["registry"] = f"error: {err or 'invalid decision'}"
        failed_checks.append("registry")

    # 3. run_registry command
    registry_cmd_payload, err = run_json_cmd([PYTHON, "scripts/lucy_run_registry_command.py"])
    if registry_cmd_payload and registry_cmd_payload.get("ok") is True:
        checks["run_registry_command"] = "ok"
    else:
        checks["run_registry_command"] = f"error: {err or 'not ok'}"
        failed_checks.append("run_registry_command")

    # 4. rollback_plan AG-Y3
    rollback_payload, err = run_json_cmd([PYTHON, "scripts/lucy_rollback_plan_command.py", "AG-Y3"])
    if rollback_payload and rollback_payload.get("ok") is True:
        checks["rollback_plan"] = "ok"
    else:
        checks["rollback_plan"] = f"error: {err or 'not ok'}"
        failed_checks.append("rollback_plan")

    # 5. verify_rollback_plan
    rollback_val_payload, err = run_json_cmd([PYTHON, "scripts/verify_rollback_plan.py", "docs/examples/ROLLBACK_PLAN_EXAMPLE_AG_Y3_R65.json"])
    if rollback_val_payload and rollback_val_payload.get("decision") == "VALID":
        checks["rollback_plan_validator"] = "ok"
    else:
        checks["rollback_plan_validator"] = f"error: {err or 'invalid decision'}"
        failed_checks.append("rollback_plan_validator")

    # 6. SEC1
    sec1_payload, err = run_json_cmd([PYTHON, "scripts/verify_lucyclaw_security_policy.py"])
    if sec1_payload and sec1_payload.get("ok") is True and not sec1_payload.get("violations"):
        checks["sec1"] = "ok"
    else:
        checks["sec1"] = f"error: {err or 'violations found'}"
        failed_checks.append("sec1")

    # 7. QA1
    qa1_payload, err = run_json_cmd([PYTHON, "scripts/verify_lucyclaw_green_commands.py"])
    if qa1_payload and qa1_payload.get("ok") is True:
        checks["qa1"] = "ok"
    else:
        checks["qa1"] = f"error: {err or 'not ok'}"
        failed_checks.append("qa1")

    # 8. lucy_next_step
    next_step_payload, err = run_json_cmd([PYTHON, "scripts/lucy_next_step_command.py"])
    if next_step_payload:
        decision = next_step_payload.get("decision")
        checks["lucy_next_step"] = decision
        if decision == "BLOCK":
            failed_checks.append("lucy_next_step")
    else:
        checks["lucy_next_step"] = f"error: {err}"
        failed_checks.append("lucy_next_step")

    # 9. health_brief
    health_payload, err = run_json_cmd([PYTHON, "scripts/lucy_health_brief_command.py"])
    if health_payload:
        overall = health_payload.get("overall")
        checks["health"] = overall
        if overall == "error":
             failed_checks.append("health")
    else:
        checks["health"] = f"error: {err}"
        failed_checks.append("health")

    # Final Decision logic
    decision = "READY"
    yellow_ready = True
    
    if failed_checks:
        decision = "BLOCK"
        yellow_ready = False
    elif checks.get("health") == "warn" or checks.get("lucy_next_step") == "WARN":
        decision = "WARN"

    output = {
        "ok": decision != "BLOCK",
        "command": "yellow_preflight",
        "stage": "AG-Y5",
        "decision": decision,
        "mode": "read-only",
        "checks": checks,
        "yellow_ready": yellow_ready,
        "rollback_allowed_now": False,
        "repair_allowed_now": False,
        "requires_grouped_permission": True,
        "forbidden": [
            "rollback real",
            "repair",
            "." + "env",
            "tokens",
            "n8n_data",
            "memoria",
            "boveda",
            "su" + "do"
        ],
        "next": "Crear ticket amarillo específico con alcance, rollback_plan y Evidence Envelope." if yellow_ready else "Diagnosticar antes de iniciar tramo amarillo."
    }

    if not yellow_ready:
        output["failed_checks"] = failed_checks

    print(json.dumps(output, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
