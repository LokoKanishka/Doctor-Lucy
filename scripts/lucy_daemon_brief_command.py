#!/usr/bin/env python3
"""Daemon Brief command for LucyClaw — read-only Daemon v3 readiness summary."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = "python3"
TIMEOUT = 60
REGISTRY_PATH = "data/run_registry/lucyclaw_runs.jsonl"


def run_cmd(args):
    env = os.environ.copy()
    env["LUCY_SKIP_PREFLIGHT_CHECK"] = "1"
    env["LUCY_SKIP_DAEMON_CHECK"] = "1"
    env["LUCY_SKIP_NEXT_STEP"] = "1"
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
            env=env,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as exc:
        return -1, "", str(exc)


def run_json(args):
    rc, stdout, stderr = run_cmd(args)
    if not stdout:
        return None, f"exit {rc}: {stderr or 'no output'}"
    try:
        return json.loads(stdout), None
    except json.JSONDecodeError:
        return None, f"invalid json: {stdout[:120]}"


def read_last_healthy_run():
    path = ROOT / REGISTRY_PATH
    if not path.exists():
        return None
    last = None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    if (
                        rec.get("final_decision") == "CLOSED"
                        and rec.get("qa1_post") == "ok"
                        and rec.get("sec1_post") == "ok"
                        and rec.get("sensitive_clean") is True
                        and rec.get("envelope_validated") is True
                    ):
                        last = rec
                except json.JSONDecodeError:
                    continue
    except OSError:
        return None
    return last


def main():
    failed = []

    # 1. Registry
    reg_payload, err = run_json(
        [PYTHON, "scripts/verify_run_registry.py", REGISTRY_PATH]
    )
    registry_ok = reg_payload and reg_payload.get("decision") == "VALID"
    if not registry_ok:
        failed.append("registry")

    # 2. Run registry command
    run_reg, err = run_json([PYTHON, "scripts/lucy_run_registry_command.py"])
    run_reg_ok = run_reg and run_reg.get("ok") is True
    if not run_reg_ok:
        failed.append("run_registry_command")

    # 3. Yellow preflight
    yp, err = run_json([PYTHON, "scripts/lucy_yellow_preflight_command.py"])
    yp_decision = yp.get("decision", "UNKNOWN") if yp else "UNKNOWN"
    yp_ready = yp.get("yellow_ready", False) if yp else False

    # 4. Next step
    ns, err = run_json([PYTHON, "scripts/lucy_next_step_command.py"])
    ns_decision = ns.get("decision", "UNKNOWN") if ns else "UNKNOWN"

    # 5. Last healthy run from local file
    last_healthy = read_last_healthy_run()
    last_summary = {}
    if last_healthy:
        last_summary = {
            "run_id": last_healthy.get("run_id"),
            "target_commit": last_healthy.get("target_commit"),
            "risk_level": last_healthy.get("risk_level"),
        }

    # Build output
    all_ok = len(failed) == 0
    design_loop_ready = all_ok and yp_ready and ns_decision != "BLOCK"

    output = {
        "ok": all_ok,
        "command": "daemon_brief",
        "stage": "AG-Y6",
        "mode": "read-only",
        "daemon_v3": {
            "architecture": "designed",
            "active": False,
            "executor_enabled": False,
            "repair_enabled": False,
            "n8n_memory_access_enabled": False,
        },
        "safety_stack": {
            "yellow_preflight": "available",
            "run_registry": "available",
            "evidence_envelope": "available",
            "rollback_plan": "available",
            "rollback_plan_validator": "available",
            "qa1": "required",
            "sec1": "required",
        },
        "last_healthy_run": last_summary,
        "readiness": {
            "yellow_preflight": yp_decision,
            "lucy_next_step": ns_decision,
            "registry": "VALID" if registry_ok else "INVALID",
            "daemon_ready_for_design_loop": design_loop_ready,
            "daemon_ready_for_autonomous_repair": False,
        },
        "next_recommendation": (
            "R66 daemon loop conceptual or AG-Y7 controlled yellow tranche."
            if design_loop_ready
            else "Resolve failed checks before proceeding."
        ),
        "forbidden_now": [
            "autonomous repair",
            "n8n workflow mutation",
            "memory mutation",
            "secrets access",
            "su" + "do",
        ],
    }

    if failed:
        output["failed_checks"] = failed
        output["decision"] = "NEEDS_REVIEW"

    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
