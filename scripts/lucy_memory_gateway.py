#!/usr/bin/env python3
"""Small local HTTP gateway for Doctora Lucy's SQLite memory vault."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "n8n_data" / "boveda_lucy.sqlite"
FINGERPRINT = "DOCTOR_LUCY__7X9K"
ALLOWED_PREFIXES = ("127.", "172.", "192.168.")


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def latest_memory(db_path: Path) -> dict[str, Any] | None:
    conn = connect(db_path)
    try:
        row = conn.execute(
            """
            SELECT id, rol, contenido_memoria, metadatos, fecha
            FROM memoria_core
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def insert_memory(db_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    content = str(payload.get("contenido_memoria") or payload.get("contenido") or "").strip()
    if not content:
        raise ValueError("contenido_memoria is required")

    role = str(payload.get("rol") or "lucy_agent").strip()
    metadata = payload.get("metadatos", {})
    if isinstance(metadata, str):
        metadata_text = metadata
    else:
        metadata_text = json.dumps(metadata, ensure_ascii=False, sort_keys=True)
    fecha = str(payload.get("fecha") or now_iso())

    conn = connect(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO memoria_core (rol, contenido_memoria, metadatos, fecha)
                VALUES (?, ?, ?, ?)
                """,
                (role, content, metadata_text, fecha),
            )
        return {
            "id": cursor.lastrowid,
            "rol": role,
            "fecha": fecha,
            "fingerprint": FINGERPRINT,
        }
    finally:
        conn.close()


class LucyMemoryHandler(BaseHTTPRequestHandler):
    server_version = "LucyMemoryGateway/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.log_date_time_string()} {self.client_address[0]} {fmt % args}", flush=True)

    @property
    def db_path(self) -> Path:
        return self.server.db_path  # type: ignore[attr-defined]

    @property
    def auth_token(self) -> str:
        return self.server.auth_token  # type: ignore[attr-defined]

    def _is_allowed(self) -> bool:
        remote = self.client_address[0]
        if not remote.startswith(ALLOWED_PREFIXES):
            return False
        if not self.auth_token:
            return True
        return self.headers.get("X-Lucy-Memory-Token") == self.auth_token

    def _json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _forbidden(self) -> None:
        self._json(HTTPStatus.FORBIDDEN, {"ok": False, "error": "forbidden"})

    def do_GET(self) -> None:
        if not self._is_allowed():
            self._forbidden()
            return
        if self.path == "/healthz":
            self._json(HTTPStatus.OK, {"ok": True, "fingerprint": FINGERPRINT})
            return
        if self.path == "/boot":
            self._json(
                HTTPStatus.OK,
                {"ok": True, "fingerprint": FINGERPRINT, "memory": latest_memory(self.db_path)},
            )
            return
        self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        if not self._is_allowed():
            self._forbidden()
            return
        if self.path != "/commit":
            self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
            return

        length = int(self.headers.get("Content-Length") or "0")
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            result = insert_memory(self.db_path, payload)
        except (json.JSONDecodeError, ValueError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return
        except sqlite3.Error as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": str(exc)})
            return

        self._json(HTTPStatus.OK, {"ok": True, "result": result})


def main() -> int:
    parser = argparse.ArgumentParser(description="Doctora Lucy memory vault HTTP gateway")
    parser.add_argument("--host", default=os.getenv("LUCY_MEMORY_HOST", "172.17.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("LUCY_MEMORY_PORT", "6970")))
    parser.add_argument("--db", type=Path, default=Path(os.getenv("LUCY_MEMORY_DB", DEFAULT_DB)))
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), LucyMemoryHandler)
    server.db_path = args.db
    server.auth_token = os.getenv("LUCY_MEMORY_TOKEN", "")
    print(f"Lucy memory gateway listening on http://{args.host}:{args.port}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
