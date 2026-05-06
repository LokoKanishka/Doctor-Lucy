#!/usr/bin/env python3
"""Static security policy verifier for LucyClaw code, plugins, and docs."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK_GLOBS = (
    "scripts/lucy_*_command.py",
    "scripts/verify_lucyclaw_*.py",
    "openclaw_plugins/lucy-*/index.js",
    "openclaw_plugins/lucy-*/openclaw.plugin.json",
    "openclaw_plugins/lucy-*/package.json",
    "docs/LUCYCLAW_CURRENT_STATE.md",
    "docs/LUCYCLAW_*R*.md",
    "docs/LUCYCLAW_GREEN_QA_QA1.md",
    "docs/LUCYCLAW_SECURITY_POLICY_SEC1.md",
)
KNOWN_PENDING_LINES = {
    "M .gitignore": "known local .gitignore drift remains pending for HYG2",
    "?? .agents/archive_openclaw_scope_fix_20260429_153235/": "known .agents archive remains pending for HYG2",
    "?? docs/OPENCLAW_REBUILD_1A_PROFILE.md": "known rebuild profile doc remains pending for HYG2",
}
LEGACY_TREE = "/home/lucy-ubuntu/Escritorio/doctor de lucy"

NO_SHELL_TRUE_RE = re.compile(r'(?i)(?:["\']?shell["\']?\s*:\s*true)')
NO_SUBPROCESS_SHELL_TRUE_RE = re.compile(r"\bshell\s*=\s*True\b")
NO_CHILD_PROCESS_EXEC_RE = re.compile(r"\bchild_process\.exec\b|\bexecSync\b|import\s*\{[^}]*\bexec(?:Sync)?\b", re.IGNORECASE)
NO_SUDO_RE = re.compile(r"\bsudo\b", re.IGNORECASE)
NO_ENV_ACCESS_RE = re.compile(r"(?i)(?:\.env\b|dotenv\b|OPENAI_API_KEY\b)")
NO_SECRET_LEAK_RE = re.compile(
    r"(?i)\b(?:token|secret|api[_-]?key|apikey|authorization|accessToken|refreshToken|password)\b"
    r"[^\n:=]{0,20}[:=][^\n]{1,120}"
)
NO_N8N_ACCESS_RE = re.compile(r"(?i)(?:n8n_data[\\/]|database\.sqlite\b|\bcredentials\b|/workflows\b)")
NO_REPAIR_RE = re.compile(
    r"(?i)(?:systemctl\s+restart|docker\s+restart|openclaw\s+gateway\s+restart|\brm\s+-rf\b|"
    r"\.unlink\(|shutil\.rmtree\b|os\.remove\b|os\.unlink\b|Path\([^)]*\)\.unlink\()"
)
ACCEPTS_ARGS_TRUE_RE = re.compile(r"\bacceptsArgs\s*:\s*true\b")
ALLOWED_ACCEPTS_ARGS_TRUE = {
    "openclaw_plugins/lucy-fs-readonly-command/index.js",
    "openclaw_plugins/lucy-fs-search-command/index.js",
    "openclaw_plugins/lucy-doc-brief-command/index.js",
    "openclaw_plugins/lucy-change-plan-command/index.js",
    "openclaw_plugins/lucy-plan-brief-command/index.js",
    "openclaw_plugins/lucy-risk-check-command/index.js",
    "openclaw_plugins/lucy-permission-brief-command/index.js",
    "openclaw_plugins/lucy-scaffold-plan-command/index.js",
    "openclaw_plugins/lucy-machine-access-command/index.js",
    "openclaw_plugins/lucy-machine-status-command/index.js",
}


def classify(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("scripts/lucy_") and rel.endswith("_command.py"):
        return "lucy_py"
    if rel.startswith("scripts/verify_lucyclaw_") and rel.endswith(".py"):
        return "verify_py"
    if rel.startswith("openclaw_plugins/") and rel.endswith("/index.js"):
        return "plugin_js"
    if rel.startswith("openclaw_plugins/") and rel.endswith((".json", "package.json")):
        return "plugin_meta"
    return "doc"


def collect_files() -> list[Path]:
    paths: set[Path] = set()
    for pattern in CHECK_GLOBS:
        paths.update(ROOT.glob(pattern))
    return sorted(path for path in paths if path.is_file())


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def compact_text(text: str, limit: int = 200) -> str:
    collapsed = " ".join(text.strip().split())
    return collapsed[: limit - 3] + "..." if len(collapsed) > limit else collapsed


def is_negated_context(line: str) -> bool:
    lowered = line.lower()
    return any(
        token in lowered
        for token in (
            "no sudo",
            "no shell",
            "no .env",
            "no tokens",
            "no token",
            "no memoria",
            "no n8n workflows",
            "without reading workflows",
            "without touching workflows",
            "no tocar",
            "must not",
            "do not",
            "prohibited",
            "prohibido",
            "forbidden",
            "salvo autorización",
            "except for",
            "prohibidas",
        )
    )


def is_guardrail_context(path: Path, *context_lines: str) -> bool:
    lowered = "\n".join(context_lines).lower()
    name = path.name
    return any(
        token in lowered
        for token in (
            "re.compile(",
            "sanitize",
            "sanitiz",
            "redact",
            "forbidden_result_segments",
            "secret_re",
            "sensitive_query_re",
            "sensitive_word_re",
            "env_path_re",
            "legacy_path_re",
            "no_shell_true_re",
            "no_subprocess_shell_true_re",
            "no_child_process_exec_re",
            "no_secret_leak_re",
            "no_env_access_re",
            "known_pending_lines",
            "no_n8n_access_re",
            "no_repair_re",
            "accepts_args_true_re",
            "blocked_actions",
            "safe_steps",
            "allowed_next_actions",
        )
    ) or name == "verify_lucyclaw_security_policy.py"


def add_violation(violations: list[dict], path: Path, line_no: int, rule: str, text: str) -> None:
    violations.append(
        {
            "file": rel(path),
            "line": line_no,
            "rule": rule,
            "text": compact_text(text),
        }
    )


def add_warning(warnings: list[dict], path: str, rule: str, text: str, line_no: int | None = None) -> None:
    warning = {
        "file": path,
        "rule": rule,
        "text": compact_text(text),
    }
    if line_no is not None:
        warning["line"] = line_no
    warnings.append(warning)


def scan_line(
    path: Path,
    kind: str,
    line_no: int,
    line: str,
    context_lines: tuple[str, ...],
    violations: list[dict],
    warnings: list[dict],
) -> None:
    stripped = line.strip()
    if not stripped:
        return

    if kind in {"plugin_js", "plugin_meta"} and NO_SHELL_TRUE_RE.search(line):
        add_violation(violations, path, line_no, "no_shell_true", line)

    if kind in {"lucy_py", "verify_py"} and NO_SUBPROCESS_SHELL_TRUE_RE.search(line):
        add_violation(violations, path, line_no, "no_subprocess_shell_true", line)

    if kind == "plugin_js" and NO_CHILD_PROCESS_EXEC_RE.search(line):
        add_violation(violations, path, line_no, "no_child_process_exec", line)

    if kind in {"lucy_py", "verify_py", "plugin_js", "plugin_meta"} and NO_SUDO_RE.search(line):
        if not is_negated_context(line) and not is_guardrail_context(path, *context_lines):
            add_violation(violations, path, line_no, "no_sudo", line)

    if kind in {"lucy_py", "verify_py", "plugin_js", "plugin_meta"} and NO_ENV_ACCESS_RE.search(line):
        if not is_negated_context(line) and not is_guardrail_context(path, *context_lines):
            add_violation(violations, path, line_no, "no_env_access", line)

    if kind in {"lucy_py", "verify_py", "plugin_js", "plugin_meta"} and NO_SECRET_LEAK_RE.search(line):
        if not is_guardrail_context(path, *context_lines) and "***" not in line:
            add_violation(violations, path, line_no, "no_secret_leak_patterns", line)
        elif is_guardrail_context(path, *context_lines):
            add_warning(warnings, rel(path), "sanitizer_secret_pattern", line, line_no)

    if LEGACY_TREE in line:
        if kind in {"lucy_py", "plugin_js", "plugin_meta"}:
            rule = "no_absolute_legacy_command_paths" if "COMMAND" in line or "resolve(" in line else "no_legacy_tree"
            add_violation(violations, path, line_no, rule, line)
        else:
            add_warning(warnings, rel(path), "legacy_tree_reference", line, line_no)

    if kind in {"lucy_py", "plugin_js"} and NO_N8N_ACCESS_RE.search(line):
        if not is_negated_context(line) and not is_guardrail_context(path, *context_lines):
            add_violation(violations, path, line_no, "no_n8n_workflow_access", line)

    if kind in {"lucy_py", "plugin_js"} and NO_REPAIR_RE.search(line):
        if not is_negated_context(line) and not is_guardrail_context(path, *context_lines):
            add_violation(violations, path, line_no, "no_auto_repair_green", line)

    if kind == "plugin_js" and ACCEPTS_ARGS_TRUE_RE.search(line):
        if rel(path) not in ALLOWED_ACCEPTS_ARGS_TRUE:
            add_violation(violations, path, line_no, "no_accepts_args_true_by_default", line)

    if kind == "plugin_js":
        lowered = line.lower()
        for forbidden, rule in (("/bash", "no_bash_command"), ("/exec", "no_exec_command"), ("/mcp", "no_mcp_shortcut")):
            if forbidden in lowered and not is_negated_context(line):
                add_violation(violations, path, line_no, rule, line)


def scan_files(paths: list[Path]) -> tuple[list[dict], list[dict]]:
    violations: list[dict] = []
    warnings: list[dict] = []

    for path in paths:
        kind = classify(path)
        lines = read_lines(path)
        for index, line in enumerate(lines):
            context_lines = tuple(lines[max(0, index - 6) : index + 1])
            scan_line(path, kind, index + 1, line, context_lines, violations, warnings)

    try:
        proc = subprocess.run(
            ["git", "status", "--short", "--branch"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=ROOT,
            timeout=10,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        add_warning(warnings, "git", "no_hyg_pending_commit", "git status timed out while checking known pending items")
        return violations, warnings

    if proc.returncode == 0:
        seen = set(proc.stdout.splitlines())
        for line, message in KNOWN_PENDING_LINES.items():
            if line in seen:
                add_warning(warnings, line.split()[-1], "no_hyg_pending_commit", message)

    return violations, warnings


def main() -> int:
    paths = collect_files()
    violations, warnings = scan_files(paths)
    payload = {
        "ok": not violations,
        "command": "verify_lucyclaw_security_policy",
        "checked_files": len(paths),
        "violations": violations,
        "warnings": warnings,
    }
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
