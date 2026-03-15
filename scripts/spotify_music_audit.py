#!/usr/bin/env python3
import os
import sys
import json
import base64
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
import sqlite3
from datetime import datetime
import time

# --- CONSTANTS ---
DATA_DIR = Path("data/music_brain")
RAW_DIR = DATA_DIR / "raw"
SQLITE_DB = DATA_DIR / "music_brain.sqlite"

REQUIRED_SCOPES = {
    "user-follow-read",
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-top-read",
    "user-read-recently-played",
    "user-read-playback-state",
    "user-read-currently-playing"
}

# --- ENV LOADING ---
def load_env():
    env_path = Path(".env")
    if not env_path.exists():
        print("Error: No .env file found.", file=sys.stderr)
        sys.exit(1)
    
    config = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'): continue
        if '=' in line:
            k, v = line.split('=', 1)
            config[k.strip()] = v.strip()
    return config

# --- SPOTIFY CLIENT ---
class SpotifyAuditClient:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.granted_scopes = set()

    def get_access_token(self):
        url = "https://accounts.spotify.com/api/token"
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {
            'Authorization': f'Basic {b64_auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = urllib.parse.urlencode({
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }).encode()

        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read())
                self.access_token = res['access_token']
                scope_str = res.get('scope', '')
                self.granted_scopes = set(scope_str.split()) if scope_str else set()
                return self.access_token
        except urllib.error.HTTPError as e:
            print(f"Auth Error: {e.read().decode()}", file=sys.stderr)
            sys.exit(1)

    def request(self, endpoint, is_full_url=False):
        if not self.access_token:
            self.get_access_token()
            
        url = endpoint if is_full_url else f"https://api.spotify.com/v1{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        req = urllib.request.Request(url, headers=headers)
        
        retries = 3
        while retries > 0:
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 204:
                        return None
                    return json.loads(resp.read())
            except urllib.error.HTTPError as e:
                msg = e.read().decode()
                if e.code == 429:
                    retry_after = int(e.headers.get('Retry-After', 5))
                    print(f"Rate limited. Retrying after {retry_after}s...")
                    time.sleep(retry_after)
                    retries -= 1
                    continue
                elif e.code == 403:
                    raise PermissionError(f"403 Forbidden: {msg}")
                else:
                    raise Exception(f"Spotify API Error {e.code}: {msg}")
            except Exception as e:
                print(f"Network error: {e}. Retrying in 5s...")
                time.sleep(5)
                retries -= 1
        return None

# --- PAGINATION HANDLER ---
def fetch_all(client, endpoint, key=None):
    items = []
    url = endpoint
    while url:
        try:
            res = client.request(url, is_full_url=url.startswith("http"))
            if not res: break
            
            # Extract items based on response structure
            if key and key in res:
                page_items = res[key].get('items', [])
                if not page_items and 'items' in res: # Fallback
                    page_items = res.get('items', [])
            elif 'artists' in res and 'items' in res['artists']: # Cursor-based
                page_items = res['artists']['items']
            else:
                page_items = res.get('items', [])
                
            items.extend(page_items)
            
            # Find next page
            if 'next' in res and res['next']:
                url = res['next']
            elif 'artists' in res and 'next' in res['artists'] and res['artists']['next']:
                 url = res['artists']['next']
            elif 'cursors' in res and 'after' in res['cursors']:
                 url = f"{endpoint}&after={res['cursors']['after']}"
                 if not res['items']: url = None # End of cursor
            else:
                url = None
                
            time.sleep(0.5) # Soft rate-limiting
        except PermissionError as e:
            raise e
        except Exception as e:
            print(f"Error fetching paginated data: {e}")
            break
            
    return items

# --- SQLITE SETUP ---
def init_db():
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS audit_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            missing_scopes TEXT,
            status TEXT
        );
        CREATE TABLE IF NOT EXISTS audit_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            endpoint TEXT,
            error_message TEXT,
            FOREIGN KEY(run_id) REFERENCES audit_runs(id)
        );
        CREATE TABLE IF NOT EXISTS artists_raw (
            spotify_id TEXT PRIMARY KEY,
            name TEXT,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS artist_sources (
            spotify_id TEXT,
            source TEXT,
            FOREIGN KEY(spotify_id) REFERENCES artists_raw(spotify_id),
            UNIQUE(spotify_id, source)
        );
        CREATE TABLE IF NOT EXISTS playlists_raw (
            spotify_id TEXT PRIMARY KEY,
            name TEXT,
            owner_id TEXT,
            snapshot_id TEXT
        );
        CREATE TABLE IF NOT EXISTS tracks_raw (
            spotify_id TEXT PRIMARY KEY,
            name TEXT,
            data_json TEXT
        );
    """)
    conn.commit()
    return conn

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    config = load_env()
    client = SpotifyAuditClient(
        config.get('SPOTIFY_CLIENT_ID'),
        config.get('SPOTIFY_CLIENT_SECRET'),
        config.get('SPOTIFY_REFRESH_TOKEN')
    )
    
    print("Iniciando auditoría de Spotify...", flush=True)
    client.get_access_token()
    
    missing_scopes = REQUIRED_SCOPES - client.granted_scopes
    summary = {
        "timestamp": datetime.now().isoformat(),
        "granted_scopes": list(client.granted_scopes),
        "missing_scopes_for_audit": list(missing_scopes),
        "endpoints_status": {}
    }
    
    if missing_scopes:
        print(f"⚠️ WARNING: Faltan scopes recomendados: {', '.join(missing_scopes)}")
        
    conn = init_db()
    c = conn.cursor()
    c.execute("INSERT INTO audit_runs (missing_scopes, status) VALUES (?, ?)", 
              (",".join(missing_scopes), "RUNNING"))
    run_id = c.lastrowid
    conn.commit()
    
    artists_inventory = {}

    def process_artist(artist_data, source):
        if not artist_data or 'id' not in artist_data: return
        sid = artist_data['id']
        name = artist_data.get('name', 'Unknown')
        
        if sid not in artists_inventory:
            artists_inventory[sid] = {"name": name, "sources": set()}
            c.execute("INSERT OR IGNORE INTO artists_raw (spotify_id, name) VALUES (?, ?)", (sid, name))
        
        artists_inventory[sid]['sources'].add(source)
        c.execute("INSERT OR IGNORE INTO artist_sources (spotify_id, source) VALUES (?, ?)", (sid, source))

    endpoints_to_run = [
        ("followed_artists", "/me/following?type=artist", "artists"),
        ("playlists", "/me/playlists?limit=50", None),
        ("saved_tracks", "/me/tracks?limit=50", None),
        ("saved_albums", "/me/albums?limit=50", None),
        ("top_artists_short", "/me/top/artists?time_range=short_term&limit=50", None),
        ("top_artists_medium", "/me/top/artists?time_range=medium_term&limit=50", None),
        ("top_artists_long", "/me/top/artists?time_range=long_term&limit=50", None),
        ("top_tracks_short", "/me/top/tracks?time_range=short_term&limit=50", None),
        ("top_tracks_medium", "/me/top/tracks?time_range=medium_term&limit=50", None),
        ("top_tracks_long", "/me/top/tracks?time_range=long_term&limit=50", None),
        ("recently_played", "/me/player/recently-played?limit=50", None)
    ]

    for name, endpoint, key in endpoints_to_run:
        print(f"Consultando {name}...", flush=True)
        try:
            items = fetch_all(client, endpoint, key)
            
            # Save raw json
            with open(RAW_DIR / f"raw_{name}.json", "w") as f:
                json.dump(items, f, indent=2)
                
            summary["endpoints_status"][name] = {"status": "SUCCESS", "count": len(items)}
            
            # Parse specific data for inventory
            if "artists" in name:
                for a in items: process_artist(a, name)
            elif name == "saved_tracks" or "tracks" in name or name == "recently_played":
                for item in items:
                    track = item.get('track', item) 
                    if not track: continue
                    # Store track
                    tid = track.get('id')
                    if tid:
                        c.execute("INSERT OR IGNORE INTO tracks_raw (spotify_id, name, data_json) VALUES (?, ?, ?)",
                                  (tid, track.get('name', ''), json.dumps(track)))
                    for artist in track.get('artists', []):
                        process_artist(artist, name)
            elif name == "playlists":
                for pl in items:
                    c.execute("INSERT OR REPLACE INTO playlists_raw (spotify_id, name, owner_id, snapshot_id) VALUES (?, ?, ?, ?)",
                              (pl.get('id'), pl.get('name'), pl.get('owner', {}).get('id'), pl.get('snapshot_id')))
                    
        except PermissionError as e:
            print(f"  -> OMITIDO: Scopes insuficientes ({e})")
            summary["endpoints_status"][name] = {"status": "FAILED_SCOPE", "error": str(e)}
            c.execute("INSERT INTO audit_errors (run_id, endpoint, error_message) VALUES (?, ?, ?)", (run_id, name, str(e)))
        except Exception as e:
            print(f"  -> ERROR: {e}")
            summary["endpoints_status"][name] = {"status": "FAILED_ERROR", "error": str(e)}
            c.execute("INSERT INTO audit_errors (run_id, endpoint, error_message) VALUES (?, ?, ?)", (run_id, name, str(e)))
            
    # Serialize artist inventory
    inventory_out = {}
    for k, v in artists_inventory.items():
        inventory_out[k] = {"name": v["name"], "sources": list(v["sources"])}
        
    with open(DATA_DIR / "artist_inventory.json", "w") as f:
        json.dump(inventory_out, f, indent=2)
        
    with open(DATA_DIR / "bootstrap_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    c.execute("UPDATE audit_runs SET status = 'COMPLETED' WHERE id = ?", (run_id,))
    conn.commit()
    conn.close()
    
    print("\nAuditoría Bootstrap Finalizada.")
    print(f"Artistas únicos encontrados: {len(artists_inventory)}")
    for name, stat in summary['endpoints_status'].items():
        print(f" - {name}: {stat['status']} (Items: {stat.get('count', 0)})")

if __name__ == "__main__":
    main()
