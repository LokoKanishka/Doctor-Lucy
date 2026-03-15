#!/usr/bin/env python3
import os
import sys
import json
import time
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data/music_brain")
SQLITE_DB = DATA_DIR / "music_brain.sqlite"
QUEUE_FILE = DATA_DIR / "core_artists_queue.json"
ENRICHED_FILE = DATA_DIR / "core_artists_enriched.json"
SUMMARY_FILE = DATA_DIR / "core_enrichment_summary.json"

USER_AGENT = "LucyMusicBrain/1.0 ( lucy@localhost )"

def init_db():
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS enrichment_jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            target_class TEXT,
            artists_queued INTEGER
        );
        CREATE TABLE IF NOT EXISTS artist_enrichment (
            artist_id TEXT PRIMARY KEY,
            name TEXT,
            country TEXT,
            artist_type TEXT,
            tags TEXT,
            similar_artists TEXT,
            decades TEXT,
            scenes TEXT,
            wikipedia_summary TEXT,
            sources_used TEXT,
            enrichment_coverage REAL,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(artist_id) REFERENCES artist_profiles(artist_id)
        );
        CREATE TABLE IF NOT EXISTS artist_external_ids (
            artist_id TEXT,
            source TEXT,
            external_id TEXT,
            FOREIGN KEY(artist_id) REFERENCES artist_profiles(artist_id),
            UNIQUE(artist_id, source)
        );
        CREATE TABLE IF NOT EXISTS enrichment_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id TEXT,
            source TEXT,
            error_message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    return conn

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def search_musicbrainz(artist_name):
    # MusicBrainz rate limit is 1 req/sec. Be a good citizen.
    time.sleep(1.1)
    query = urllib.parse.quote(artist_name)
    url = f"https://musicbrainz.org/ws/2/artist/?query=artist:{query}&fmt=json"
    res = fetch_json(url)
    
    if "error" in res:
        return None, res["error"]
        
    artists = res.get("artists", [])
    if not artists:
        return None, "Not found"
        
    # Take the top match closely matching the exact name
    best_match = None
    for a in artists:
        if a.get("name", "").lower() == artist_name.lower():
            best_match = a
            break
            
    if not best_match:
        best_match = artists[0]
        
    mbid = best_match.get("id")
    country = best_match.get("country", "")
    artist_type = best_match.get("type", "")
    
    tags = [t["name"] for t in best_match.get("tags", [])]
    # Filter out very generic tags or low confidence
    genres = [t for t in tags if "rock" in t or "pop" in t or "metal" in t or "jazz" in t or "electronic" in t or "hop" in t]
    
    return {
        "mbid": mbid,
        "country": country,
        "artist_type": artist_type,
        "tags": genres if genres else tags[:5],
        "disambiguation": best_match.get("disambiguation", "")
    }, None

def search_wikipedia(artist_name):
    time.sleep(0.1)
    # Using the en.wikipedia REST API for extracts
    query = urllib.parse.quote(artist_name)
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    res = fetch_json(url)
    
    if "error" in res or "extract" not in res:
        return None, res.get("error", "Not found")
        
    return res.get("extract"), None

def main():
    if not SQLITE_DB.exists():
        print("Error: SQLite DB missing. Run normalization first.")
        sys.exit(1)
        
    conn = init_db()
    c = conn.cursor()
    
    print("Iniciando Fase 3A: Enriquecimiento de Artistas Core...")
    
    c.execute("SELECT artist_id, name, total_score, class_label FROM artist_profiles WHERE class_label = 'core' ORDER BY total_score DESC")
    core_artists = c.fetchall()
    
    if not core_artists:
        print("No se encontraron artistas 'core'.")
        sys.exit(1)
        
    # Generate Queue (Phase 3 Requirement)
    queue = [{"artist_id": aid, "name": name, "score": score, "status": "pending"} for aid, name, score, _ in core_artists]
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)
    c.execute("INSERT INTO enrichment_jobs (target_class, artists_queued) VALUES (?, ?)", ("core", len(queue)))
    conn.commit()
    
    print(f"Generada cola de {len(queue)} artistas core. Procesando enriquecimiento (MusicBrainz + Wikipedia)...")
    print("Aviso: Last.fm requiere API Key, se omiten similar_artists por ahora.")
    
    results = []
    stats = {"ok": 0, "partial": 0, "fail": 0}
    sources_coverage = {"musicbrainz": 0, "wikipedia": 0}
    
    # Process the queue locally
    for i, artist in enumerate(queue):
        aid = artist["artist_id"]
        name = artist["name"]
        score = artist["score"]
        
        print(f"[{i+1}/{len(queue)}] Enriqueciendo: {name}...", end="", flush=True)
        
        mb_data, mb_err = search_musicbrainz(name)
        wiki_data, wiki_err = search_wikipedia(name)
        
        sources_used = []
        coverage = 0.0
        
        if mb_data:
            sources_used.append("MusicBrainz")
            sources_coverage["musicbrainz"] += 1
            coverage += 0.5
            
            # Save MB_ID external id
            c.execute("INSERT OR IGNORE INTO artist_external_ids (artist_id, source, external_id) VALUES (?, ?, ?)", 
                      (aid, "musicbrainz", mb_data["mbid"]))
                      
        else:
            c.execute("INSERT INTO enrichment_errors (artist_id, source, error_message) VALUES (?, ?, ?)", (aid, "musicbrainz", mb_err))
            
        if wiki_data:
            sources_used.append("Wikipedia")
            sources_coverage["wikipedia"] += 1
            coverage += 0.5
        else:
             c.execute("INSERT INTO enrichment_errors (artist_id, source, error_message) VALUES (?, ?, ?)", (aid, "wikipedia", wiki_err))
             
        if coverage == 1.0:
            stats["ok"] += 1
        elif coverage > 0:
            stats["partial"] += 1
        else:
            stats["fail"] += 1
            
        print(f" [{'OK' if coverage == 1.0 else 'PARTIAL' if coverage > 0 else 'FAIL'}]")
        
        tags_str = json.dumps(mb_data.get("tags", [])) if mb_data else "[]"
        country = mb_data.get("country", "") if mb_data else ""
        art_type = mb_data.get("artist_type", "") if mb_data else ""
        sources_str = json.dumps(sources_used)
        
        enriched_item = {
            "artist_id": aid,
            "name": name,
            "class_label": "core",
            "total_score": score,
            "external_ids": {"musicbrainz": mb_data["mbid"]} if mb_data else {},
            "country": country,
            "artist_type": art_type,
            "tags": mb_data.get("tags", []) if mb_data else [],
            "similar_artists": [], # Requires last.fm
            "decades": [], # Hard to parse without release dates
            "scenes": [mb_data["disambiguation"]] if mb_data and mb_data.get("disambiguation") else [],
            "wikipedia_summary": wiki_data,
            "enrichment_coverage": coverage,
            "sources_used": sources_used
        }
        
        results.append(enriched_item)
        
        c.execute("""
            INSERT OR REPLACE INTO artist_enrichment 
            (artist_id, name, country, artist_type, tags, similar_artists, decades, scenes, wikipedia_summary, sources_used, enrichment_coverage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (aid, name, country, art_type, tags_str, "[]", "[]", json.dumps(enriched_item["scenes"]), wiki_data, sources_str, coverage))
        
        # Commit every 10 artists to be safe
        if i % 10 == 0:
            conn.commit()
            
    conn.commit()
    conn.close()
    
    with open(ENRICHED_FILE, "w") as f:
        json.dump(results, f, indent=2)
        
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_core_artists": len(queue),
        "artists_enriched_ok": stats["ok"],
        "artists_partial": stats["partial"],
        "artists_failed": stats["fail"],
        "sources_coverage": sources_coverage,
        "missing_apis": ["Last.fm (requires API Key)", "Discogs (requires API Key)"]
    }
    
    with open(SUMMARY_FILE, "w") as f:
        json.dump(summary, f, indent=2)
        
    print("\nEnriquecimiento completado.")
    print(f"Exito: {stats['ok']}, Parcial: {stats['partial']}, Fallo: {stats['fail']}")

if __name__ == "__main__":
    main()
