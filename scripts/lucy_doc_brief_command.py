#!/usr/bin/env python3
"""Deterministic read-only document brief for safe LucyClaw repo files."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
STAGE = "R50A"
MAX_FILE_BYTES = 256 * 1024
MAX_ANALYZED_LINES = 300
MAX_POINTS = 5
MAX_SECTIONS = 8
MAX_SAFE_NEXT = 5
MAX_TEXT = 160
KIND_MAP = {
    ".md": "markdown",
    ".py": "python",
    ".js": "javascript",
    ".json": "json",
}
MARKDOWN_KEYWORDS = (
    "objective",
    "estado",
    "tests",
    "security",
    "rollback",
    "commands",
    "usage",
    "summary",
)
SENSITIVE_SEGMENTS = tuple(
    "".join(parts)
    for parts in (
        (".", "env"),
        (".", "git"),
        (".", "agents"),
        ("n8n_", "data"),
        ("n8n_", "backups"),
        ("work", "flows"),
        ("cred", "entials"),
        ("database", ".sqlite"),
        ("token", "s"),
        ("secret", "s"),
        ("api", "_keys"),
        ("pass", "word"),
    )
)
ALLOWED_DOC_PREFIX = "docs/"
ALLOWED_SCRIPT_PREFIXES = ("scripts/lucy_", "scripts/verify_lucyclaw_")
ALLOWED_PLUGIN_PREFIX = "openclaw_plugins/lucy-"
ALLOWED_PLUGIN_FILES = ("index.js", "openclaw.plugin.json", "package.json")
SAFE_FOCUS_WORDS = re.compile(r"(?i)\b(?:read-?only|safe|bounded|deterministic|qa1|sec1|plugin|command|summary|health|repo)\b")


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def compact(text: str, limit: int = MAX_TEXT) -> str:
    collapsed = " ".join(text.strip().split())
    return collapsed[: limit - 3] + "..." if len(collapsed) > limit else collapsed


def contains_sensitive(path_text: str) -> bool:
    lowered = path_text.lower()
    return any(segment in lowered for segment in SENSITIVE_SEGMENTS)


def is_allowed_relative_path(path_text: str) -> bool:
    if not path_text or path_text.startswith("/"):
        return False
    normalized = PurePosixPath(path_text).as_posix()
    if normalized.startswith("../") or "/../" in normalized or normalized == "..":
        return False
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if contains_sensitive(normalized):
        return False
    if normalized.startswith(ALLOWED_DOC_PREFIX):
        return normalized.endswith(".md")
    if any(normalized.startswith(prefix) for prefix in ALLOWED_SCRIPT_PREFIXES):
        return normalized.endswith(".py")
    if normalized.startswith(ALLOWED_PLUGIN_PREFIX):
        return normalized.endswith(ALLOWED_PLUGIN_FILES)
    return False


def resolve_safe_path(raw_path: str) -> tuple[Path | None, str | None]:
    if not is_allowed_relative_path(raw_path):
        return None, None
    normalized = PurePosixPath(raw_path).as_posix()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    target = (ROOT / normalized).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return None, None
    if not target.is_file():
        return None, None
    if target.stat().st_size > MAX_FILE_BYTES:
        return None, None
    return target, normalized


def reject_payload() -> tuple[dict, int]:
    return {
        "ok": False,
        "command": "doc_brief",
        "stage": STAGE,
        "error": "path rejected by read-only policy",
    }, 2


def read_text_lines(target: Path) -> tuple[list[str], bool]:
    raw = target.read_bytes()
    if b"\x00" in raw:
        raise ValueError("binary files are not supported")
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    return lines[:MAX_ANALYZED_LINES], len(lines) > MAX_ANALYZED_LINES


def kind_for_path(path_text: str) -> str:
    return KIND_MAP.get(Path(path_text).suffix.lower(), "text")


def markdown_title(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            return compact(stripped[2:])
    return compact(Path("document").name)


def first_paragraph(lines: list[str]) -> str:
    chunks: list[str] = []
    started = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if started and chunks:
                break
            continue
        if stripped.startswith(("#", "-", "*", "```")):
            if started and chunks:
                break
            continue
        if stripped.lower().startswith("date:"):
            continue
        started = True
        chunks.append(stripped)
        if len(" ".join(chunks)) >= MAX_TEXT:
            break
    return compact(" ".join(chunks))


def markdown_sections(lines: list[str]) -> list[str]:
    sections: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            sections.append(compact(stripped.lstrip("# ").strip(), 80))
    seen: list[str] = []
    for entry in sections:
        if entry not in seen:
            seen.append(entry)
    return seen[:MAX_SECTIONS]


def markdown_points(lines: list[str]) -> list[str]:
    points: list[str] = []
    for line in lines:
        stripped = line.strip()
        lowered = stripped.lower()
        if stripped.startswith("# "):
            continue
        if stripped.startswith(("- ", "* ")):
            candidate = compact(stripped[2:])
            if candidate and candidate not in points:
                points.append(candidate)
        elif any(keyword in lowered for keyword in MARKDOWN_KEYWORDS) and len(stripped) > 12:
            candidate = compact(stripped.lstrip("#").strip())
            if candidate and candidate not in points:
                points.append(candidate)
        elif SAFE_FOCUS_WORDS.search(stripped):
            candidate = compact(stripped)
            if candidate and candidate not in points:
                points.append(candidate)
        if len(points) >= MAX_POINTS:
            break
    return points[:MAX_POINTS]


def parse_python(lines: list[str]) -> tuple[str, list[str], list[str]]:
    source = "\n".join(lines)
    purpose = ""
    points: list[str] = []
    sections: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return purpose, points, sections

    docstring = ast.get_docstring(tree) or ""
    if docstring:
        purpose = compact(docstring.splitlines()[0])
    imports: list[str] = []
    functions: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names[:4])
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
    if imports:
        sections.append("imports: " + ", ".join(imports[:4]))
    if functions:
        sections.append("functions: " + ", ".join(functions[:5]))
    command_match = re.search(r'"command"\s*:\s*"([^"]+)"', source)
    if command_match:
        points.append(f"Command payload: {command_match.group(1)}.")
    if docstring:
        points.append(purpose)
    if functions:
        points.append("Top-level functions: " + ", ".join(functions[:4]) + ".")
    if "MAX_" in source:
        points.append("Aplica límites explícitos de lectura y salida.")
    return purpose, [compact(point) for point in points[:MAX_POINTS]], [compact(item, 100) for item in sections[:MAX_SECTIONS]]


def parse_javascript(lines: list[str]) -> tuple[str, list[str], list[str]]:
    source = "\n".join(lines)
    purpose = ""
    points: list[str] = []
    sections: list[str] = []
    comment_match = re.search(r"/\*\*\s*(.*?)\s*\*/", source, re.DOTALL)
    if comment_match:
        purpose = compact(comment_match.group(1).replace("*", " "))
    imports = re.findall(r'^import\s+.*?from\s+"([^"]+)"', source, re.MULTILINE)
    functions = re.findall(r"function\s+([A-Za-z0-9_]+)\s*\(", source)
    command_names = re.findall(r'name:\s*"([A-Za-z0-9_]+)"', source)
    accepts_args = "acceptsArgs: true" in source
    if imports:
        sections.append("imports: " + ", ".join(imports[:4]))
    if functions:
        sections.append("functions: " + ", ".join(functions[:5]))
    if command_names:
        points.append("Registered names: " + ", ".join(command_names[:4]) + ".")
    if accepts_args:
        points.append("Acepta argumentos y valida uso desde el plugin.")
    if purpose:
        points.append(purpose)
    return purpose, [compact(point) for point in points[:MAX_POINTS]], [compact(item, 100) for item in sections[:MAX_SECTIONS]]


def parse_json_file(lines: list[str]) -> tuple[str, list[str], list[str]]:
    source = "\n".join(lines)
    purpose = ""
    points: list[str] = []
    sections: list[str] = []
    try:
        payload = json.loads(source)
    except json.JSONDecodeError:
        return purpose, points, sections
    if isinstance(payload, dict):
        if "description" in payload and isinstance(payload["description"], str):
            purpose = compact(payload["description"])
        keys = list(payload.keys())
        if keys:
            sections.append("keys: " + ", ".join(keys[:8]))
        if "id" in payload:
            points.append(f"Identifier: {payload['id']}.")
        if "name" in payload:
            points.append(f"Name: {payload['name']}.")
        if "main" in payload:
            points.append(f"Main entry: {payload['main']}.")
    return purpose, [compact(point) for point in points[:MAX_POINTS]], [compact(item, 100) for item in sections[:MAX_SECTIONS]]


def build_safe_next(path_text: str, total_lines: int) -> list[str]:
    end_line = min(80, total_lines if total_lines > 0 else 80)
    scope = "docs" if path_text.startswith("docs/") else "scripts" if path_text.startswith("scripts/") else "openclaw_plugins"
    hint = Path(path_text).stem.replace("LUCYCLAW_", "").replace("lucy_", "")
    grep_term = hint.split("_")[0] if hint else "repo"
    entries = [
        f"/fs_read {path_text} 1 {end_line}",
        f"/fs_grep {grep_term} {scope}",
        "/repo_map",
    ]
    return entries[:MAX_SAFE_NEXT]


def build_summary(path_text: str, lines: list[str], truncated: bool, total_lines: int) -> dict:
    kind = kind_for_path(path_text)
    title = Path(path_text).name
    purpose = ""
    main_points: list[str] = []
    detected_sections: list[str] = []

    if kind == "markdown":
        title = markdown_title(lines)
        purpose = first_paragraph(lines) or "Documento operativo del repo LucyClaw."
        main_points = markdown_points(lines)
        detected_sections = markdown_sections(lines)
    elif kind == "python":
        purpose, main_points, detected_sections = parse_python(lines)
        title = Path(path_text).name
    elif kind == "javascript":
        purpose, main_points, detected_sections = parse_javascript(lines)
        title = Path(path_text).name
    elif kind == "json":
        purpose, main_points, detected_sections = parse_json_file(lines)
        title = Path(path_text).name

    if not purpose:
        purpose = "Resumen seguro y determinístico de archivo permitido del repo."
    if not main_points:
        main_points = ["Archivo permitido inspeccionado con límites read-only."]

    payload = {
        "ok": True,
        "command": "doc_brief",
        "stage": STAGE,
        "path": path_text,
        "kind": kind,
        "lines": total_lines,
        "truncated": truncated,
        "summary": {
            "title": compact(title, 100),
            "purpose": compact(purpose),
            "main_points": [compact(item) for item in main_points[:MAX_POINTS]],
        },
        "safe_next": build_safe_next(path_text, total_lines),
        "limits": [
            "Resumen extractivo/determinístico.",
            "No lee zonas sensibles.",
            "No usa modelo externo.",
        ],
    }
    if detected_sections:
        payload["summary"]["detected_sections"] = [compact(item, 100) for item in detected_sections[:MAX_SECTIONS]]
    return payload


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return emit(
            {
                "ok": False,
                "command": "doc_brief",
                "stage": STAGE,
                "error": "usage: lucy_doc_brief_command.py <relative-path>",
            },
            2,
        )

    target, normalized = resolve_safe_path(argv[1])
    if not target or not normalized:
        payload, code = reject_payload()
        return emit(payload, code)

    try:
        all_lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        lines, was_truncated = read_text_lines(target)
    except ValueError as exc:
        return emit({"ok": False, "command": "doc_brief", "stage": STAGE, "error": compact(str(exc))}, 2)

    truncated = was_truncated or len(lines) < len(all_lines)
    return emit(build_summary(normalized, lines, truncated, len(all_lines)))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
