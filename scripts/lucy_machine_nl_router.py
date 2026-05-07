#!/usr/bin/env python3
"""Deterministic natural-language router for Lucy machine commands."""

from __future__ import annotations

import json
import re
import sys
import unicodedata


DESKTOP_PATH = "/home/lucy-ubuntu/Escritorio"


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_text(text: str) -> str:
    lowered = strip_accents(text.lower())
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def has_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def build_match(intent: str, command: str, args: str = "") -> dict:
    return {
        "ok": True,
        "recognized": True,
        "intent": intent,
        "command": command,
        "args": args,
        "mode": "read-only",
        "requires_model": False,
    }


def build_fallback() -> dict:
    return {
        "ok": True,
        "recognized": False,
        "requires_model": True,
    }


def route_message(message: str) -> dict:
    normalized = normalize_text(message)
    if not normalized:
        return build_fallback()

    if has_any(normalized, ("vram", "gpu", "placa de video", "tarjeta grafica", "grafica")):
        return build_match("gpu_status", "machine_gpu")

    if has_any(normalized, ("ram", "memoria")) and has_any(
        normalized,
        ("uso", "usando", "estoy usando", "cuanta", "cuanto", "consumo", "ocupada"),
    ):
        return build_match("ram_usage", "machine_ram")

    if "proceso" in normalized and has_any(
        normalized,
        ("corriendo", "activos", "activo", "ejecutando", "ejecucion", "andando"),
    ):
        return build_match("processes_status", "machine_processes")

    if "disco" in normalized or has_any(normalized, ("almacenamiento", "espacio disponible", "espacio libre")):
        return build_match("disk_usage", "machine_disk")

    if has_any(normalized, ("descargas", "downloads")) or (
        "descarg" in normalized and has_any(normalized, ("ultimo", "ultima", "reciente", "baje"))
    ):
        return build_match("downloads_listing", "machine_downloads")

    if "escritorio" in normalized and has_any(
        normalized,
        ("que hay", "carpetas", "archivos", "listar", "mostrame", "mostrar", "hay en"),
    ):
        return build_match("desktop_listing", "machine_ls", DESKTOP_PATH)

    if has_any(normalized, ("pc", "computadora", "maquina", "equipo")) and has_any(
        normalized,
        ("activo", "activa", "hay activo", "estado", "como esta", "status"),
    ):
        return build_match("machine_status", "machine_status")

    return build_fallback()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(json.dumps({"ok": False, "error": "missing message argument"}, ensure_ascii=False, indent=2))
        return 1

    message = " ".join(argv[1:]).strip()
    print(json.dumps(route_message(message), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
