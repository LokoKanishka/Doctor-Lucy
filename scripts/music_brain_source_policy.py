#!/usr/bin/env python3
import json
import sqlite3
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Paths
DATA_DIR = Path("data/music_brain")
POLICIES_JSON = DATA_DIR / "source_policies.json"
HEALTH_JSON = DATA_DIR / "source_health.json"
SQLITE_DB = DATA_DIR / "music_brain.sqlite"

def get_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def init_db():
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    # Policies Table
    c.execute('''CREATE TABLE IF NOT EXISTS source_policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_name TEXT,
        entity_type TEXT,
        job_type TEXT,
        allowed INTEGER,
        reason TEXT,
        status TEXT,
        updated_at TEXT,
        UNIQUE(source_name, entity_type, job_type)
    )''')
    
    # Health Table
    c.execute('''CREATE TABLE IF NOT EXISTS source_health (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_name TEXT,
        job_type TEXT,
        success_count INTEGER DEFAULT 0,
        empty_count INTEGER DEFAULT 0,
        error_count INTEGER DEFAULT 0,
        status TEXT,
        last_success_at TEXT,
        last_failure_at TEXT,
        notes TEXT,
        UNIQUE(source_name, job_type)
    )''')

    # Audit Log Table
    c.execute('''CREATE TABLE IF NOT EXISTS source_decisions_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        source_name TEXT,
        entity_type TEXT,
        job_type TEXT,
        decision TEXT,
        reason TEXT
    )''')
    conn.commit()
    conn.close()

def log_decision(source, entity, job, decision, reason):
    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()
        c.execute('''INSERT INTO source_decisions_log 
                     (timestamp, source_name, entity_type, job_type, decision, reason) 
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (get_now(), source, entity, job, decision, reason))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to log decision to SQLite: {e}")

def seed_defaults():
    init_db()
    
    policies = [
        {
            "source_name": "MusicBrainz",
            "entity_type": "artist",
            "job_type": "artist_enrichment_basic",
            "allowed": True,
            "reason": "Referencia core principal verificada",
            "status": "active",
            "updated_at": get_now()
        },
        {
            "source_name": "Wikipedia",
            "entity_type": "artist",
            "job_type": "artist_enrichment_basic",
            "allowed": True,
            "reason": "Excelente para resúmenes de contexto biográfico",
            "status": "active",
            "updated_at": get_now()
        },
        {
            "source_name": "Last.fm",
            "entity_type": "artist",
            "job_type": "artist_enrichment_basic",
            "allowed": True,
            "reason": "Probado y validado como fuente principal de tags y similitudes",
            "status": "active",
            "updated_at": get_now()
        },
        {
            "source_name": "Last.fm",
            "entity_type": "artist",
            "job_type": "artist_similarity",
            "allowed": True,
            "reason": "Fuente principal consolidada de grafos de similitud",
            "status": "active",
            "updated_at": get_now()
        },
        {
            "source_name": "Last.fm",
            "entity_type": "artist",
            "job_type": "artist_tags",
            "allowed": True,
            "reason": "Fuente principal para microgéneros y taxonomía folclórica",
            "status": "active",
            "updated_at": get_now()
        },
        {
            "source_name": "Discogs",
            "entity_type": "artist",
            "job_type": "artist_enrichment_basic",
            "allowed": False,
            "reason": "Discogs a nivel artista no devuelve estilos útiles de forma fiable; reservar para release/master",
            "status": "disabled",
            "updated_at": get_now()
        },
        {
            "source_name": "Discogs",
            "entity_type": "release",
            "job_type": "release_master_enrichment",
            "allowed": True,
            "reason": "Candidato futuro para estilos y géneros precisos a nivel de álbum",
            "status": "active",
            "updated_at": get_now()
        },
        {
            "source_name": "Discogs",
            "entity_type": "master",
            "job_type": "release_master_enrichment",
            "allowed": True,
            "reason": "Candidato futuro para estilos y géneros precisos a nivel master",
            "status": "active",
            "updated_at": get_now()
        }
    ]
    
    healths = [
        {
            "source_name": "MusicBrainz",
            "job_type": "artist_enrichment_basic",
            "success_count": 403,
            "empty_count": 0,
            "error_count": 0,
            "status": "healthy",
            "last_success_at": get_now(),
            "last_failure_at": None,
            "notes": "Validado al 100% en bootstraps y fase 1/2"
        },
        {
            "source_name": "Wikipedia",
            "job_type": "artist_enrichment_basic",
            "success_count": 308,
            "empty_count": 95,
            "error_count": 0,
            "status": "healthy",
            "last_success_at": get_now(),
            "last_failure_at": None,
            "notes": "Validado en fase 1/2"
        },
        {
            "source_name": "Last.fm",
            "job_type": "artist_enrichment_basic",
            "success_count": 383,
            "empty_count": 20,
            "error_count": 1,
            "status": "healthy",
            "last_success_at": get_now(),
            "last_failure_at": None,
            "notes": "Validado en fase 3C con éxito"
        },
        {
            "source_name": "Discogs",
            "job_type": "artist_enrichment_basic",
            "success_count": 0,
            "empty_count": 403,
            "error_count": 0,
            "status": "disabled",
            "last_success_at": None,
            "last_failure_at": None,
            "notes": "Disabled by policy: empty styles returned at API artist level"
        }
    ]

    with open(POLICIES_JSON, "w") as f:
        json.dump(policies, f, indent=2, ensure_ascii=False)
        
    with open(HEALTH_JSON, "w") as f:
        json.dump(healths, f, indent=2, ensure_ascii=False)

    # Sync to SQLite
    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()
        for p in policies:
            c.execute('''INSERT OR REPLACE INTO source_policies 
                         (source_name, entity_type, job_type, allowed, reason, status, updated_at) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (p['source_name'], p['entity_type'], p['job_type'], int(p['allowed']), p['reason'], p['status'], p['updated_at']))
            
        for h in healths:
            c.execute('''INSERT OR REPLACE INTO source_health 
                         (source_name, job_type, success_count, empty_count, error_count, status, last_success_at, last_failure_at, notes) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (h['source_name'], h['job_type'], h['success_count'], h['empty_count'], h['error_count'], h['status'], h['last_success_at'], h['last_failure_at'], h['notes']))
        conn.commit()
        conn.close()
        print(" Políticas y logs de salud sembrados correctamente en JSON y SQLite.")
    except Exception as e:
        print(f"Error escribiendo en SQLite: {e}")

def show():
    if not POLICIES_JSON.exists():
        print("No se encontraron políticas. Ejecuta 'seed-defaults' primero.")
        sys.exit(1)
        
    with open(POLICIES_JSON, "r") as f:
        policies = json.load(f)
        
    print("=== SOURCE POLICIES ===")
    for p in policies:
        status_str = " ALLOW " if p['allowed'] else " DENY  "
        print(f"[{status_str}] {p['source_name']} | Entity: {p['entity_type']} | Job: {p['job_type']}")
        print(f"          Reason: {p['reason']}")
        print("-" * 50)

def health():
    if not HEALTH_JSON.exists():
        print("No se encontraron datos de salud. Ejecuta 'seed-defaults' primero.")
        sys.exit(1)
        
    with open(HEALTH_JSON, "r") as f:
        healths = json.load(f)
        
    print("=== SOURCE HEALTH ===")
    for h in healths:
        print(f"[{h['status'].upper()}] {h['source_name']} | Job: {h['job_type']}")
        print(f"          Success: {h['success_count']} | Empty: {h['empty_count']} | Errors: {h['error_count']}")
        print(f"          Notes: {h['notes']}")
        print("-" * 50)

def check(source, entity, job):
    if not POLICIES_JSON.exists() or not HEALTH_JSON.exists():
        print("DENIED: Sistema no inicializado. Faltan los archivos JSON de políticas.")
        return False
        
    with open(POLICIES_JSON, "r") as f:
        policies = json.load(f)
        
    with open(HEALTH_JSON, "r") as f:
        healths = json.load(f)
        
    source_norm = ''.join(e for e in source.lower() if e.isalnum())
    
    # Check policy
    policy_match = None
    for p in policies:
        p_source_norm = ''.join(e for e in p['source_name'].lower() if e.isalnum())
        if p_source_norm == source_norm and \
           p['entity_type'].lower() == entity.lower() and \
           p['job_type'].lower() == job.lower():
            policy_match = p
            break
            
    if not policy_match:
        reason = f"No explicit policy found for {source}/{entity}/{job}. Defaulting to DENY."
        log_decision(source, entity, job, "DENIED", reason)
        print(f"DENIED: {reason}")
        return False
        
    if not policy_match['allowed']:
        reason = policy_match['reason']
        log_decision(source, entity, job, "DENIED", reason)
        print(f"DENIED: Policy -> {reason}")
        return False
        
    # Check health as secondary layer
    health_match = None
    for h in healths:
        h_source_norm = ''.join(e for e in h['source_name'].lower() if e.isalnum())
        if h_source_norm == source_norm and \
           h['job_type'].lower() == job.lower():
            health_match = h
            break
            
    if health_match and health_match['status'].lower() in ['disabled', 'paused', 'down']:
        reason = f"Source is currently {health_match['status']}: {health_match.get('notes', '')}"
        log_decision(source, entity, job, "DENIED", reason)
        print(f"DENIED: Health -> {reason}")
        return False
        
    reason = "Allowed by policy and health checks passed."
    log_decision(source, entity, job, "ALLOWED", reason)
    print(f"ALLOWED: {reason}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Music Brain Source Policy & Health Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("show", help="Muestra las políticas actuales")
    subparsers.add_parser("health", help="Muestra las métricas actuales de salud")
    subparsers.add_parser("seed-defaults", help="Siembra políticas y salud iniciales")
    
    check_parser = subparsers.add_parser("check", help="Verifica si una fuente es válida para un job")
    check_parser.add_argument("source", help="Nombre de fuente (ej. Discogs, Last.fm)")
    check_parser.add_argument("entity", help="Tipo de entidad (ej. artist, release)")
    check_parser.add_argument("job", help="Tipo de job (ej. artist_enrichment_basic)")
    
    args = parser.parse_args()
    
    if args.command == "show":
        show()
    elif args.command == "health":
        health()
    elif args.command == "seed-defaults":
        seed_defaults()
    elif args.command == "check":
        allowed = check(args.source, args.entity, args.job)
        sys.exit(0 if allowed else 1)
