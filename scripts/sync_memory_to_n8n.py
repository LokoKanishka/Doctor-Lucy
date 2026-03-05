#!/usr/bin/env python3
"""
sync_memory_to_n8n.py — Sincroniza el estado actual de Lucy al Búnker JSONL.

Lee:
  - boveda_lucy.sqlite (último estado guardado)
  - Knowledge Graph stats (entidades, relaciones)

Escribe:
  - data/lucy_bunker_log.jsonl (append, una línea JSON por sync)
  - Opcionalmente envía a n8n webhook (cuando esté activo)

Uso:
  python3 scripts/sync_memory_to_n8n.py
  python3 scripts/sync_memory_to_n8n.py --webhook http://localhost:6969/webhook/lucy/commit
"""
import json
import sqlite3
import datetime
import pathlib
import argparse
import sys

# Rutas
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
BOVEDA_PATH = PROJECT_ROOT / "n8n_data" / "boveda_lucy.sqlite"
AGENTE_DB_PATH = PROJECT_ROOT / "memoria" / "agente_memoria.db"
BUNKER_PATH = PROJECT_ROOT / "data" / "lucy_bunker_log.jsonl"
FINGERPRINT = "DOCTOR_LUCY__7X9K"


def leer_boveda() -> dict:
    """Lee el último registro de la bóveda SQLite."""
    if not BOVEDA_PATH.exists():
        return {"error": "boveda_lucy.sqlite no encontrada"}

    conn = sqlite3.connect(str(BOVEDA_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT contenido_memoria, metadatos, fecha FROM memoria_core ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if row is None:
        return {"estado": "vacía"}

    try:
        metadatos = json.loads(row["metadatos"]) if row["metadatos"] else {}
    except json.JSONDecodeError:
        metadatos = {"raw": row["metadatos"]}

    return {
        "contenido": row["contenido_memoria"],
        "metadatos": metadatos,
        "fecha": row["fecha"],
    }


def leer_kg_stats() -> dict:
    """Lee estadísticas del Knowledge Graph."""
    if not AGENTE_DB_PATH.exists():
        return {"error": "agente_memoria.db no encontrada"}

    conn = sqlite3.connect(str(AGENTE_DB_PATH))
    stats = {}
    try:
        for tabla in ("kg_entidades", "kg_relaciones", "kg_observaciones"):
            row = conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()
            stats[tabla] = row[0] if row else 0
    except Exception:
        stats["error"] = "Tablas KG no inicializadas aún"
    conn.close()
    return stats


def sync(webhook_url: str = None):
    """Ejecuta la sincronización completa."""
    ahora = datetime.datetime.now().isoformat()

    # Recolectar estado
    boveda = leer_boveda()
    kg_stats = leer_kg_stats()

    registro = {
        "ts": ahora,
        "fingerprint": FINGERPRINT,
        "boveda": boveda,
        "knowledge_graph": kg_stats,
        "sync_type": "manual",
    }

    # Asegurar que el directorio data/ exista
    BUNKER_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Append al JSONL
    with open(BUNKER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"[sync] ✅ Estado sincronizado al búnker: {BUNKER_PATH}")
    print(f"[sync]    Timestamp: {ahora}")
    print(f"[sync]    KG stats: {kg_stats}")

    # Webhook opcional
    if webhook_url:
        try:
            import urllib.request
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(registro, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                print(f"[sync]    n8n webhook: {resp.status}")
        except Exception as e:
            print(f"[sync]    ⚠️  Webhook falló (no crítico): {e}")

    return registro


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Lucy memory to JSONL bunker")
    parser.add_argument("--webhook", type=str, default=None, help="n8n webhook URL")
    args = parser.parse_args()
    sync(webhook_url=args.webhook)
