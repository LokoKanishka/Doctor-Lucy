#!/usr/bin/env python3
"""Verify the LucyClaw scaffold generator without creating live commands."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "create_lucy_command_scaffold.py"


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def run_json(args: list[str], *, cwd: Path = ROOT) -> tuple[dict, int]:
    proc = subprocess.run(
        args,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=20,
        shell=False,
        cwd=cwd,
    )
    raw = proc.stdout.strip()
    if not raw:
        raise RuntimeError(proc.stderr.strip() or "command produced no stdout")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("command returned invalid JSON") from exc
    return payload, proc.returncode


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    results: list[dict] = []
    try:
        with tempfile.TemporaryDirectory(prefix="lucyclaw_scaffold_") as tmpdir:
            tmp = Path(tmpdir)

            dry_payload, dry_code = run_json(
                [
                    "python3",
                    str(GENERATOR),
                    "--name",
                    "test_command",
                    "--stage",
                    "RXX",
                    "--description",
                    "Test command",
                    "--dry-run",
                    "--output-root",
                    str(tmp),
                ]
            )
            assert_true(dry_code == 0 and dry_payload.get("ok") is True, "dry-run did not succeed")
            assert_true(dry_payload.get("dry_run") is True, "dry-run flag missing")
            assert_true(dry_payload.get("plugin_id") == "lucy-test-command-command", "unexpected plugin id")
            planned = dry_payload.get("files_planned", [])
            assert_true(len(planned) == 5, "dry-run did not report five planned files")
            for relative in planned:
                assert_true(not (tmp / relative).exists(), f"dry-run wrote file unexpectedly: {relative}")
            results.append({"check": "dry_run_valid", "status": "ok"})

            invalid_payload, invalid_code = run_json(
                [
                    "python3",
                    str(GENERATOR),
                    "--name",
                    "../evil",
                    "--stage",
                    "RXX",
                    "--description",
                    "Bad",
                    "--dry-run",
                    "--output-root",
                    str(tmp),
                ]
            )
            assert_true(invalid_code == 2 and invalid_payload.get("ok") is False, "invalid name did not fail")
            results.append({"check": "invalid_name_rejected", "status": "ok"})

            create_payload, create_code = run_json(
                [
                    "python3",
                    str(GENERATOR),
                    "--name",
                    "test_command",
                    "--stage",
                    "RXX",
                    "--description",
                    "Test command",
                    "--output-root",
                    str(tmp),
                ]
            )
            assert_true(create_code == 0 and create_payload.get("ok") is True, "real generation did not succeed")
            created = [tmp / rel for rel in create_payload.get("files_created", [])]
            assert_true(all(path.exists() for path in created), "real generation missed expected files")
            results.append({"check": "real_generation_tempdir", "status": "ok"})

            wrapper_text = read_text(tmp / "scripts/lucy_test_command_command.py")
            index_text = read_text(tmp / "openclaw_plugins/lucy-test-command-command/index.js")
            plugin_json = read_text(tmp / "openclaw_plugins/lucy-test-command-command/openclaw.plugin.json")
            doc_text = read_text(tmp / "docs/LUCYCLAW_TEST_COMMAND_RXX.md")

            assert_true('"command": "test_command"' in wrapper_text, "wrapper command field missing")
            assert_true("shell: false" in index_text, "plugin template missing shell:false")
            assert_true("shell:true" not in index_text, "plugin template contains shell:true")
            assert_true("execSync" not in index_text, "plugin template contains execSync")
            assert_true("child_process.exec" not in index_text, "plugin template contains exec")
            assert_true("/home/lucy-ubuntu/Escritorio/doctor de lucy" not in index_text, "plugin template contains legacy path")
            assert_true('"additionalProperties": false' in plugin_json, "plugin config schema not locked down")
            assert_true("verify_lucyclaw_green_commands.py" in doc_text, "doc missing QA1 reference")
            assert_true("verify_lucyclaw_security_policy.py" in doc_text, "doc missing SEC1 reference")
            results.append({"check": "template_security_markers", "status": "ok"})

            overwrite_payload, overwrite_code = run_json(
                [
                    "python3",
                    str(GENERATOR),
                    "--name",
                    "test_command",
                    "--stage",
                    "RXX",
                    "--description",
                    "Test command",
                    "--output-root",
                    str(tmp),
                ]
            )
            assert_true(overwrite_code == 2 and overwrite_payload.get("ok") is False, "overwrite protection did not trigger")
            results.append({"check": "overwrite_protected", "status": "ok"})

    except (AssertionError, RuntimeError, subprocess.TimeoutExpired) as exc:
        return emit(
            {
                "ok": False,
                "command": "verify_lucy_command_scaffold",
                "error": str(exc),
                "checks": results,
            },
            2,
        )

    return emit({"ok": True, "command": "verify_lucy_command_scaffold", "checks": results})


if __name__ == "__main__":
    raise SystemExit(main())
