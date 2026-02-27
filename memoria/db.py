"""
db.py — Esquema SQLite y gestión de conexiones.
Base de datos: agente_memoria.db (en la misma carpeta, ignorada por git)
"""
import sqlite3
import pathlib

# Ruta absoluta a la base de datos (junto a este archivo)
DB_PATH = pathlib.Path(__file__).parent / "agente_memoria.db"

SCHEMA = """
-- Tabla principal de sesiones
CREATE TABLE IF NOT EXISTS sesiones (
    session_id      TEXT PRIMARY KEY,
    creada_en       TEXT NOT NULL DEFAULT (datetime('now')),
    cerrada_en      TEXT,
    resumen         TEXT,
    tokens_totales  INTEGER DEFAULT 0,
    estado          TEXT DEFAULT 'activa'  -- activa | cerrada | comprimida
);

-- Mensajes individuales de la sesión
CREATE TABLE IF NOT EXISTS mensajes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL REFERENCES sesiones(session_id),
    rol             TEXT NOT NULL,          -- user | assistant | tool | system
    contenido_json  TEXT NOT NULL,          -- JSON serializado del mensaje
    tokens_est      INTEGER DEFAULT 0,      -- estimación de tokens
    timestamp       TEXT DEFAULT (datetime('now'))
);

-- Metadatos clave-valor por sesión (decisiones, artefactos, notas)
CREATE TABLE IF NOT EXISTS metadatos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL REFERENCES sesiones(session_id),
    clave           TEXT NOT NULL,
    valor           TEXT NOT NULL,
    timestamp       TEXT DEFAULT (datetime('now'))
);

-- Caché global de búsquedas/herramientas (evita repetir búsquedas costosas)
CREATE TABLE IF NOT EXISTS cache_global (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    clave_hash      TEXT UNIQUE NOT NULL,   -- hash SHA256 de la consulta
    resultado       TEXT NOT NULL,          -- resultado serializado en JSON
    origen          TEXT,                   -- qué herramienta lo generó
    timestamp       TEXT DEFAULT (datetime('now')),
    expira_en       TEXT                    -- NULL = sin expiración
);

-- Índice de texto completo para búsqueda rápida por keywords
CREATE INDEX IF NOT EXISTS idx_mensajes_session ON mensajes(session_id);
CREATE INDEX IF NOT EXISTS idx_mensajes_rol ON mensajes(rol);
CREATE INDEX IF NOT EXISTS idx_metadatos_clave ON metadatos(clave);
CREATE INDEX IF NOT EXISTS idx_cache_hash ON cache_global(clave_hash);
"""


def get_connection() -> sqlite3.Connection:
    """Retorna una conexión SQLite con row_factory para acceso por nombre."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # write-ahead log: más rápido
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def inicializar_db() -> None:
    """Crea todas las tablas e índices si no existen. Idempotente."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
    print(f"[memoria] DB inicializada en: {DB_PATH}")
