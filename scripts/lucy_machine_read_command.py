#!/usr/bin/env python3
"""Read-only document reader for LucyClaw machine commands."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


DEFAULT_LIMIT = 6000
PDF_TIMEOUT_SECONDS = 12
ALLOWED_ROOTS = tuple(
    Path(path).resolve()
    for path in (
        "/home/lucy-ubuntu",
        "/home/lucy-ubuntu/Descargas",
        "/home/lucy-ubuntu/Downloads",
        "/home/lucy-ubuntu/Escritorio",
        "/home/lucy-ubuntu/Documentos",
        "/home/lucy-ubuntu/Imágenes",
    )
)
FORBIDDEN_SEGMENTS = (
    "." + "env",
    ".s" + "sh",
    ".gn" + "upg",
    ".con" + "fig",
    "n8" + "n_" + "data",
    "mem" + "oria",
    "bo" + "veda",
    "va" + "ult",
    "to" + "kens",
    "creden" + "tials",
    ".age" + "nts",
    "node_" + "modules",
    ".open" + "claw",
    ".ge" + "mini",
)
TEXT_EXTENSIONS = {".txt", ".md", ".json", ".csv", ".log"}
DOCX_EXTENSIONS = {".docx"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | DOCX_EXTENSIONS | PDF_EXTENSIONS
WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
EXTENSION_PATTERN = re.compile(r"(\.txt|\.md|\.json|\.csv|\.log|\.docx|\.pdf)(?:\s|$)", re.IGNORECASE)


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return code


def controlled_error(command: str, error: str, *, details: str | None = None, code: int = 0) -> int:
    payload = {
        "ok": False,
        "command": command,
        "mode": "read-only",
        "controlled_failure": True,
        "error": error,
    }
    if details:
        payload["details"] = details
    return emit(payload, code)


def is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def path_contains_forbidden(path: Path) -> bool:
    parts = tuple(part.lower() for part in path.parts)
    name = path.name.lower()
    return any(segment in parts or segment in name for segment in FORBIDDEN_SEGMENTS)


def resolve_safe_path(raw_path: str) -> Path:
    expanded = Path(os.path.expanduser(raw_path)).resolve()
    if ".." in raw_path.split("/"):
        raise ValueError("Access denied or unsafe path")
    if not any(is_path_within(expanded, root) for root in ALLOWED_ROOTS):
        raise ValueError("Access denied or unsafe path")
    if path_contains_forbidden(expanded):
        raise ValueError("Access denied or unsafe path")
    return expanded


def read_text_file(path: Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Unable to decode text file")


def detect_supported_extension(path: Path) -> str:
    name = path.name.lower()
    match = EXTENSION_PATTERN.search(name)
    if match:
        return match.group(1).lower()
    return path.suffix.lower()


def read_docx_file(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            with archive.open("word/document.xml") as handle:
                xml_bytes = handle.read()
    except KeyError as exc:
        raise ValueError("DOCX missing word/document.xml") from exc
    except zipfile.BadZipFile as exc:
        raise ValueError("Invalid DOCX file") from exc

    root = ET.fromstring(xml_bytes)
    paragraphs: list[str] = []
    for para in root.findall(".//w:p", WORD_NS):
        chunks: list[str] = []
        for node in para.iter():
            tag = node.tag.rsplit("}", 1)[-1]
            if tag == "t" and node.text:
                chunks.append(node.text)
            elif tag == "tab":
                chunks.append("\t")
            elif tag in {"br", "cr"}:
                chunks.append("\n")
        paragraph = "".join(chunks).strip()
        if paragraph:
            paragraphs.append(paragraph)
    return "\n\n".join(paragraphs).strip()


def read_pdf_file(path: Path) -> str:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        raise FileNotFoundError("pdftotext not available")

    proc = subprocess.run(
        [pdftotext, "-layout", "-enc", "UTF-8", str(path), "-"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
        timeout=PDF_TIMEOUT_SECONDS,
    )
    if proc.returncode != 0:
        raise ValueError(proc.stderr.strip() or "pdftotext failed")
    return proc.stdout


def read_document(path: Path) -> str:
    extension = detect_supported_extension(path)
    if extension in TEXT_EXTENSIONS:
        return read_text_file(path)
    if extension in DOCX_EXTENSIONS:
        return read_docx_file(path)
    if extension in PDF_EXTENSIONS:
        return read_pdf_file(path)
    raise ValueError("Unsupported file format")


def build_metadata(path: Path) -> dict:
    stat = path.stat()
    return {
        "path": str(path),
        "name": path.name,
        "extension": detect_supported_extension(path),
        "size_bytes": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def truncate_text(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit], True


def build_success_payload(command: str, path: Path, text: str, limit: int, *, brief: bool) -> dict:
    snippet, truncated = truncate_text(text, limit)
    payload = {
        "ok": True,
        "command": command,
        "mode": "read-only",
        **build_metadata(path),
        "chars_returned": len(snippet),
        "truncated": truncated,
        "controlled_failure": False,
    }
    if brief:
        payload["excerpt"] = snippet
        payload["summary_hint"] = "Extracto literal acotado; sin resumen semántico automático."
    else:
        payload["text"] = snippet
    return payload


def parse_args(argv: list[str]) -> tuple[str, str]:
    if len(argv) < 3:
        raise ValueError("Missing path argument")
    return argv[1], " ".join(argv[2:]).strip()


def main(argv: list[str]) -> int:
    try:
        action, raw_path = parse_args(argv)
    except ValueError as exc:
        command = "machine_doc_brief" if len(argv) > 1 and argv[1] == "brief" else "machine_read"
        return controlled_error(command, str(exc), code=2)

    if action == "read":
        command = "machine_read"
    elif action == "brief":
        command = "machine_doc_brief"
    else:
        return controlled_error("machine_read", f"Unknown action: {action}", code=2)

    try:
        path = resolve_safe_path(raw_path)
    except ValueError as exc:
        return controlled_error(command, str(exc), code=2)

    if not path.exists():
        return controlled_error(command, "Path not found", code=2)
    if not path.is_file():
        return controlled_error(command, "Path is not a file", code=2)
    if detect_supported_extension(path) not in SUPPORTED_EXTENSIONS:
        return controlled_error(command, "Unsupported file format", code=2)

    try:
        text = read_document(path)
    except FileNotFoundError as exc:
        return controlled_error(command, str(exc), code=2)
    except subprocess.TimeoutExpired:
        return controlled_error(command, "Document read timed out", code=2)
    except (OSError, ET.ParseError, ValueError) as exc:
        return controlled_error(command, str(exc), code=2)

    payload = build_success_payload(command, path, text, DEFAULT_LIMIT, brief=(action == "brief"))
    return emit(payload)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
