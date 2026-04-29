#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOWED_EXTENSIONS = {
    ".py",
    ".sh",
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".html",
    ".css",
    ".js",
}
EXCLUDED_DIRS = {
    ".git",
    ".agents",
    "n8n_data",
    "__pycache__",
    ".venv",
    ".voice_env",
    "node_modules",
}
EXCLUDED_SUFFIXES = {
    ".sqlite",
    ".log",
    ".sqlite-wal",
    ".sqlite-shm",
    ".pyc",
}
EXCLUDED_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}
EXCLUDED_SUBSTRINGS = {
    "backup",
    "secret",
}
DEFAULT_MAX_RESULTS = 20
MAX_RESULTS_LIMIT = 50
MAX_READ_LINES = 120
MAX_LINE_LENGTH = 300


class ValidationError(Exception):
    pass


def emit(payload, exit_code=0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(exit_code)


def error(message, **details):
    payload = {"ok": False, "error": message}
    if details:
        payload["details"] = details
    emit(payload, 2)


def validate_max_results(value):
    if value < 1 or value > MAX_RESULTS_LIMIT:
        raise ValidationError(f"max-results must be between 1 and {MAX_RESULTS_LIMIT}")
    return value


def ensure_relative_input(raw_path):
    path = Path(raw_path)
    if path.is_absolute():
        raise ValidationError("absolute paths are not allowed")
    if any(part == ".." for part in path.parts):
        raise ValidationError("parent traversal is not allowed")
    return path


def is_within_repo(path):
    try:
        path.resolve().relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def normalize_target(raw_path):
    rel_path = ensure_relative_input(raw_path)
    target = (REPO_ROOT / rel_path).resolve()
    if not is_within_repo(target):
        raise ValidationError("path escapes repository root")
    return target


def is_excluded(path):
    rel_parts = path.relative_to(REPO_ROOT).parts
    if any(part in EXCLUDED_DIRS for part in rel_parts[:-1]):
        return True
    name = path.name
    lowered = name.lower()
    if name in EXCLUDED_NAMES:
        return True
    if any(lowered.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return True
    if any(token in lowered for token in EXCLUDED_SUBSTRINGS):
        return True
    return False


def is_allowed_file(path):
    if not path.is_file():
        return False
    if is_excluded(path):
        return False
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False
    if path.is_symlink() and not is_within_repo(path):
        return False
    return True


def safe_relative(path):
    return str(path.relative_to(REPO_ROOT))


def iter_allowed_files(base_dir):
    for path in sorted(base_dir.rglob("*")):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(REPO_ROOT).parts):
            continue
        if is_allowed_file(path):
            yield path


def trim_text(text, limit=MAX_LINE_LENGTH):
    text = text.rstrip("\n")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def cmd_find_files(args):
    max_results = validate_max_results(args.max_results)
    query = args.query.strip().lower()
    if not query:
        raise ValidationError("query must not be empty")
    results = []
    for path in iter_allowed_files(REPO_ROOT):
        if query in path.name.lower():
            results.append(safe_relative(path))
            if len(results) >= max_results:
                break
    emit(
        {
            "ok": True,
            "action": "find_files",
            "base_path": str(REPO_ROOT),
            "query": args.query,
            "count": len(results),
            "results": results,
        }
    )


def cmd_grep_text(args):
    max_results = validate_max_results(args.max_results)
    query = args.query
    if not query.strip():
        raise ValidationError("query must not be empty")
    base_dir = normalize_target(args.path)
    if not base_dir.exists():
        raise ValidationError("path does not exist")
    if base_dir.is_file():
        files = [base_dir] if is_allowed_file(base_dir) else []
    else:
        files = iter_allowed_files(base_dir)
    results = []
    for path in files:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as fh:
                for number, line in enumerate(fh, 1):
                    if query in line:
                        results.append(
                            {
                                "path": safe_relative(path),
                                "line": number,
                                "text": trim_text(line),
                            }
                        )
                        if len(results) >= max_results:
                            emit(
                                {
                                    "ok": True,
                                    "action": "grep_text",
                                    "base_path": str(REPO_ROOT),
                                    "query": query,
                                    "search_path": args.path,
                                    "count": len(results),
                                    "results": results,
                                }
                            )
        except OSError:
            continue
    emit(
        {
            "ok": True,
            "action": "grep_text",
            "base_path": str(REPO_ROOT),
            "query": query,
            "search_path": args.path,
            "count": len(results),
            "results": results,
        }
    )


def cmd_read_lines(args):
    target = normalize_target(args.path)
    if not is_allowed_file(target):
        raise ValidationError("path is not an allowed file")
    start = args.start
    end = args.end
    if start < 1 or end < start:
        raise ValidationError("invalid line range")
    if (end - start + 1) > MAX_READ_LINES:
        raise ValidationError(f"line range exceeds maximum of {MAX_READ_LINES}")
    lines = []
    try:
        with target.open("r", encoding="utf-8", errors="replace") as fh:
            for number, line in enumerate(fh, 1):
                if number < start:
                    continue
                if number > end:
                    break
                lines.append({"line": number, "text": trim_text(line, 500)})
    except OSError as exc:
        raise ValidationError(f"could not read file: {exc}") from exc
    emit(
        {
            "ok": True,
            "action": "read_lines",
            "base_path": str(REPO_ROOT),
            "path": safe_relative(target),
            "start": start,
            "end": end,
            "count": len(lines),
            "lines": lines,
        }
    )


def build_parser():
    parser = argparse.ArgumentParser(description="Read-only filesystem helper for Doctor-Lucy repo.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    find_parser = subparsers.add_parser("find_files")
    find_parser.add_argument("--query", required=True)
    find_parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS)
    find_parser.set_defaults(handler=cmd_find_files)

    grep_parser = subparsers.add_parser("grep_text")
    grep_parser.add_argument("--query", required=True)
    grep_parser.add_argument("--path", default=".")
    grep_parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS)
    grep_parser.set_defaults(handler=cmd_grep_text)

    read_parser = subparsers.add_parser("read_lines")
    read_parser.add_argument("--path", required=True)
    read_parser.add_argument("--start", required=True, type=int)
    read_parser.add_argument("--end", required=True, type=int)
    read_parser.set_defaults(handler=cmd_read_lines)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except ValidationError as exc:
        error(str(exc))


if __name__ == "__main__":
    main()
