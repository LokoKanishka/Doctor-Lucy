#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DATA_DIR = Path("data/music_brain")
RAW_DIR = DATA_DIR / "raw"
SQLITE_DB = DATA_DIR / "music_brain.sqlite"

# --- SCORING WEIGHTS ---
# Las fuentes explícitas (follow/guardado) y a largo plazo valen más.
# Las de corto plazo o incidentales valen menos.
SCORE_WEIGHTS = {
    "followed_artists": 20,
    "saved_albums": 15,
    "top_artists_long": 20,
    "top_tracks_long": 15,
    "saved_tracks": 10,
    "top_artists_medium": 15,
    "top_tracks_medium": 10,
    "top_artists_short": 10,
    "top_tracks_short": 5,
    "recently_played": 5,
    "playlists": 5
}

def classify_artist(score):
    if score >= 50:
        return "core"
    elif score >= 20:
        return "recurrent"
    elif score >= 5:
        return "satellite"
    else:
        return "incidental"

def init_db():
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS artist_profiles (
            artist_id TEXT PRIMARY KEY,
            name TEXT,
            total_score INTEGER,
            class_label TEXT,
            sources_present TEXT,
            normalization_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS artist_source_metrics (
            artist_id TEXT,
            source TEXT,
            occurrence_count INTEGER,
            FOREIGN KEY(artist_id) REFERENCES artist_profiles(artist_id),
            UNIQUE(artist_id, source)
        );
        CREATE TABLE IF NOT EXISTS normalization_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_artists INTEGER,
            core_count INTEGER,
            recurrent_count INTEGER,
            satellite_count INTEGER,
            incidental_count INTEGER
        );
    """)
    conn.commit()
    return conn

def main():
    if not RAW_DIR.exists():
        print("Error: data/music_brain/raw no existe. Correr el bootstrap primero.")
        sys.exit(1)
        
    print("Iniciando Fase 2: Normalización y Scoring de Lucy Music Brain...")
    
    # 1. Base counts & sources dictionary
    # format: artist_id -> { "name": str, "sources_count": dict, "first_seen_source": str }
    artists = defaultdict(lambda: {"name": "Unknown", "sources_count": defaultdict(int), "first_seen_source": None})
    
    # Helper to process an artist instance
    def count_artist(item_artist, source):
        if not item_artist or 'id' not in item_artist: return
        aid = item_artist['id']
        name = item_artist.get('name', 'Unknown')
        if name and name != "Unknown":
            artists[aid]["name"] = name
        
        if not artists[aid]["first_seen_source"]:
            artists[aid]["first_seen_source"] = source
            
        artists[aid]["sources_count"][source] += 1

    # 2. Leer JSONs crudos
    raw_files = {
        "followed_artists": "raw_followed_artists.json",
        "saved_albums": "raw_saved_albums.json",
        "saved_tracks": "raw_saved_tracks.json",
        "top_artists_long": "raw_top_artists_long.json",
        "top_artists_medium": "raw_top_artists_medium.json",
        "top_artists_short": "raw_top_artists_short.json",
        "top_tracks_long": "raw_top_tracks_long.json",
        "top_tracks_medium": "raw_top_tracks_medium.json",
        "top_tracks_short": "raw_top_tracks_short.json",
        "recently_played": "raw_recently_played.json"
        # playlists was just metadata in phase 1, no tracks inside it.
    }
    
    for source, filename in raw_files.items():
        filepath = RAW_DIR / filename
        if not filepath.exists():
            print(f"Advertencia: No se encontró {filename}")
            continue
            
        with open(filepath, "r") as f:
            try:
                items = json.load(f)
            except json.JSONDecodeError:
                continue
                
        for item in items:
            # Handle different structures
            if source == "followed_artists" or source.startswith("top_artists"):
                count_artist(item, source)
                
            elif source == "saved_albums":
                album = item.get('album', item)
                for a in album.get('artists', []):
                    count_artist(a, source)
                    
            elif source == "saved_tracks" or source.startswith("top_tracks") or source == "recently_played":
                track = item.get('track', item)
                for a in track.get('artists', []):
                    count_artist(a, source)
                    
    # 3. Calculate Scores & Classes
    profiles_out = {}
    rankings_out = []
    
    for aid, data in artists.items():
        score = 0
        sources_present = list(data["sources_count"].keys())
        
        for src, count in data["sources_count"].items():
            # Base logic:
            # - Si aparece en tops o follows, se suma el peso base. 
            # - Si acumula múltiples tracks (ej. top_tracks_long con 10 temas), multiplicamos o sumamos bonus.
            # Para mantenerlo simple según el script, sumaremos el peso base + un extra por persistencia (count)
            base_weight = SCORE_WEIGHTS.get(src, 1)
            score += base_weight + (count * 0.5) # Bonus ligero por repetición dentro de la misma lista
            
        # Normalizar redondeo
        score = int(score)
        label = classify_artist(score)
        
        profile = {
            "artist_id": aid,
            "name": data["name"],
            "sources_present": sources_present,
            "followed_present": "followed_artists" in sources_present,
            "saved_track_count": data["sources_count"].get("saved_tracks", 0),
            "saved_album_count": data["sources_count"].get("saved_albums", 0),
            "top_short_count": data["sources_count"].get("top_tracks_short", 0) + data["sources_count"].get("top_artists_short", 0),
            "top_medium_count": data["sources_count"].get("top_tracks_medium", 0) + data["sources_count"].get("top_artists_medium", 0),
            "top_long_count": data["sources_count"].get("top_tracks_long", 0) + data["sources_count"].get("top_artists_long", 0),
            "recent_count": data["sources_count"].get("recently_played", 0),
            "total_score": score,
            "class_label": label,
            "first_seen_source": data["first_seen_source"],
            "normalization_timestamp": datetime.now().isoformat()
        }
        
        profiles_out[aid] = profile
        rankings_out.append(profile)

    # Ordenar ranking
    rankings_out.sort(key=lambda x: x["total_score"], reverse=True)
    
    # 4. Construir Summary
    class_counts = {"core": 0, "recurrent": 0, "satellite": 0, "incidental": 0}
    for p in rankings_out:
        class_counts[p["class_label"]] += 1
        
    top_25 = [{"name": p["name"], "score": p["total_score"], "class": p["class_label"]} for p in rankings_out[:25]]
    
    summary = {
        "total_artists": len(rankings_out),
        "class_counts": class_counts,
        "top_25": top_25,
        "observations": []
    }
    
    if class_counts["core"] > 0:
        pct_core = round(100 * class_counts["core"] / len(rankings_out), 1)
        summary["observations"].append(f"El núcleo musical fuerte (Core) representa el {pct_core}% de la biblioteca completa.")
        
    if class_counts["incidental"] > class_counts["recurrent"] * 2:
        summary["observations"].append("Existe una anomalía de periferia amplia: Demasiados artistas incidentales (probablemente playlists aleatorias).")
        
    # 5. Escribir Archivos
    with open(DATA_DIR / "artist_profiles.json", "w") as f:
        json.dump(profiles_out, f, indent=2)
        
    with open(DATA_DIR / "artist_rankings.json", "w") as f:
        # Just export a list sorted by score
        json.dump(rankings_out, f, indent=2)
        
    with open(DATA_DIR / "profile_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
        
    # 6. Guardar en SQLite
    conn = init_db()
    c = conn.cursor()
    
    for aid, p in profiles_out.items():
        c.execute("""
            INSERT OR REPLACE INTO artist_profiles 
            (artist_id, name, total_score, class_label, sources_present, normalization_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (aid, p["name"], p["total_score"], p["class_label"], json.dumps(p["sources_present"]), p["normalization_timestamp"]))
        
        for src, ct in artists[aid]["sources_count"].items():
            c.execute("""
                INSERT OR REPLACE INTO artist_source_metrics (artist_id, source, occurrence_count)
                VALUES (?, ?, ?)
            """, (aid, src, ct))
            
    c.execute("""
        INSERT INTO normalization_runs (total_artists, core_count, recurrent_count, satellite_count, incidental_count)
        VALUES (?, ?, ?, ?, ?)
    """, (summary["total_artists"], class_counts["core"], class_counts["recurrent"], class_counts["satellite"], class_counts["incidental"]))
        
    conn.commit()
    conn.close()

    print(f"Normalización completada. Procesados {summary['total_artists']} artistas.")
    print(f"Clases: Core={class_counts['core']}, Recurrent={class_counts['recurrent']}, Satellite={class_counts['satellite']}, Incidental={class_counts['incidental']}")

if __name__ == "__main__":
    main()
