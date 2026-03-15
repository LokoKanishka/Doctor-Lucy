#!/usr/bin/env python3
"""
music_brain_enrich_core_3c.py
Fase 3C: Enriquecimiento Semántico Avanzado con Last.fm y Discogs
Lee los 403 artistas "core", extrae tags curados y aristas similares de Last.fm,
y estilos musicales específicos de Discogs. Indexa todo en la base de datos local SQLite.
"""
import os
import json
import time
import sqlite3
import requests
import socket
import urllib3.util.connection as urllib3_cn

# Force IPv4 to prevent hanging on misconfigured Ubuntu IPv6 stacks
def allowed_gai_family():
    return socket.AF_INET
urllib3_cn.allowed_gai_family = allowed_gai_family

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

DATA_DIR = Path("data/music_brain")
SQLITE_DB = DATA_DIR / "music_brain.sqlite"
INPUT_JSON = DATA_DIR / "core_artists_enriched.json"
OUTPUT_JSON = DATA_DIR / "core_artists_enriched_3c.json"
SUMMARY_JSON = DATA_DIR / "core_enrichment_3c_summary.json"

LASTFM_KEY = os.environ.get("LASTFM_API_KEY", "").strip()
DISCOGS_KEY = os.environ.get("DISCOGS_KEY", "").strip()
DISCOGS_SECRET = os.environ.get("DISCOGS_SECRET", "").strip()

if not LASTFM_KEY or not DISCOGS_KEY or not DISCOGS_SECRET:
    print("Error: Faltan claves de API en .env. Requeridas: LASTFM_API_KEY, DISCOGS_KEY, DISCOGS_SECRET.")
    exit(1)

def init_db(conn):
    c = conn.cursor()
    c.execute("PRAGMA table_info(artist_enrichment)")
    columns = [col[1] for col in c.fetchall()]
    if "lastfm_tags" not in columns:
        c.execute("ALTER TABLE artist_enrichment ADD COLUMN lastfm_tags TEXT")
    if "discogs_styles" not in columns:
        c.execute("ALTER TABLE artist_enrichment ADD COLUMN discogs_styles TEXT")
        
    c.execute('''CREATE TABLE IF NOT EXISTS artist_similar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_id TEXT,
        similar_artist_name TEXT,
        similar_artist_mbid TEXT,
        match_score REAL,
        UNIQUE(artist_id, similar_artist_name),
        FOREIGN KEY(artist_id) REFERENCES artist_profiles(artist_id)
    )''')
    conn.commit()

def fetch_lastfm_tags(artist_name):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {'method': 'artist.getTopTags', 'artist': artist_name, 'api_key': LASTFM_KEY, 'format': 'json'}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            tags = [t['name'].lower() for t in data.get('toptags', {}).get('tag', [])][:15]
            return tags
        else:
            print(f"  [!] LFM Tags Error: HTTP {r.status_code} - {r.text[:50]}")
    except Exception as e:
        print(f"  [!] LFM Tags Error: {e}")
    return []

def fetch_lastfm_similar(artist_name):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {'method': 'artist.getSimilar', 'artist': artist_name, 'api_key': LASTFM_KEY, 'format': 'json', 'limit': 15}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            similar = []
            for a in data.get('similarartists', {}).get('artist', []):
                similar.append({
                    "name": a.get("name"),
                    "mbid": a.get("mbid", ""),
                    "match": float(a.get("match", 0.0))
                })
            return similar
        else:
            print(f"  [!] LFM Similar Error: HTTP {r.status_code} - {r.text[:50]}")
    except Exception as e:
        print(f"  [!] LFM Similar Error: {e}")
    return []

def fetch_discogs_styles(artist_name):
    url = "https://api.discogs.com/database/search"
    headers = {
        'Authorization': f'OAuth oauth_consumer_key="{DISCOGS_KEY}", oauth_signature="{DISCOGS_SECRET}&"',
        'User-Agent': 'LucyMusicBrain/1.0'
    }
    params = {'q': artist_name, 'type': 'artist'}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return data["results"][0].get("style", [])
            else:
                return []
        elif r.status_code == 429:
            print("  [!] Discogs limit hit, sleeping...")
            time.sleep(2)
            return fetch_discogs_styles(artist_name)
        else:
            print(f"  [!] Discogs Error: HTTP {r.status_code} - {r.text[:50]}")
    except Exception as e:
        print(f"  [!] Discogs Error: {e}")
    return []

def main():
    if not INPUT_JSON.exists():
        print(f"Error: No se encuentra {INPUT_JSON}. Fase 3A incompleta.")
        return

    with open(INPUT_JSON, "r") as f:
        core_artists = json.load(f)

    conn = sqlite3.connect(SQLITE_DB)
    init_db(conn)
    c = conn.cursor()

    # Determine already processed artists reading SQLite
    c.execute("SELECT artist_id FROM artist_enrichment WHERE lastfm_tags IS NOT NULL")
    processed_ids = {row[0] for row in c.fetchall()}

    print(f"=== MUSIC BRAIN FASE 3C: Last.fm & Discogs ===")
    print(f"Artistas totales (Core): {len(core_artists)}")
    print(f"Ya procesados en SQLite: {len(processed_ids)}")
    
    to_process = [a for a in core_artists if a["artist_id"] not in processed_ids]
    print(f"Pendientes por procesar: {len(to_process)}")

    results = []
    # If resuming, load existing from output file if it exists
    if OUTPUT_JSON.exists():
        with open(OUTPUT_JSON, "r") as f:
            try:
                results = json.load(f)
            except:
                results = []

    success = 0
    failed = 0

    for idx, artist in enumerate(to_process):
        aid = artist["artist_id"]
        name = artist["name"]
        print(f"[{idx+1}/{len(to_process)}] {name}...")

        tags = fetch_lastfm_tags(name)
        time.sleep(0.3) 
        
        similar = fetch_lastfm_similar(name)
        time.sleep(0.3)
        
        styles = fetch_discogs_styles(name)
        time.sleep(1.1) # Strict 1 req/sec Discogs limit

        if not tags and not similar and not styles:
            failed += 1
            print(f"  -> Ninguna API retornó datos. Fallido.")
            artist["lastfm_tags"] = []
            artist["lastfm_similar"] = []
            artist["discogs_styles"] = []
        else:
            success += 1
            print(f"  -> OK: {len(tags)} tags | {len(similar)} similares | {len(styles)} estilos")
            artist["lastfm_tags"] = tags
            artist["lastfm_similar"] = similar
            artist["discogs_styles"] = styles
            artist["enrichment_coverage"] = artist.get("enrichment_coverage", 0) + 0.3 # bump it a bit
            if "Last.fm" not in artist.get("sources_used", []):
                artist.setdefault("sources_used", []).extend(["Last.fm", "Discogs"])

        # Update SQLite enrichment
        c.execute("""
            UPDATE artist_enrichment 
            SET lastfm_tags = ?, discogs_styles = ?, enrichment_coverage = ? 
            WHERE artist_id = ?
        """, (json.dumps(tags), json.dumps(styles), artist.get("enrichment_coverage", 0), aid))

        # Update SQLite graph
        for s in similar:
            c.execute("""
                INSERT OR IGNORE INTO artist_similar (artist_id, similar_artist_name, similar_artist_mbid, match_score)
                VALUES (?, ?, ?, ?)
            """, (aid, s["name"], s["mbid"], s["match"]))
            # Also update match score if existing but match is better
            c.execute("""
                UPDATE artist_similar SET match_score = ?
                WHERE artist_id = ? AND similar_artist_name = ? AND match_score < ?
            """, (s["match"], aid, s["name"], s["match"]))
        
        conn.commit()
        results.append(artist)

        # Partial save every 10 items
        if (idx + 1) % 10 == 0:
            with open(OUTPUT_JSON, "w") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

    # Final save
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    conn.close()

    summary = {
        "total_core_artists": len(core_artists),
        "total_processed_this_run": len(to_process),
        "success": success,
        "failed": failed
    }

    with open(SUMMARY_JSON, "w") as f:
        json.dump(summary, f, indent=2)

    print("=== ENRIQUECIMIENTO 3C COMPLETADO ===")
    print(f"Éxito: {success} | Fallidos: {failed}")
    print("Graph de similitud almacenado en SQLite -> artist_similar")

if __name__ == "__main__":
    main()
