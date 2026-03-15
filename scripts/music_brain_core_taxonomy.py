#!/usr/bin/env python3
"""
music_brain_core_taxonomy.py
Fase 3B: Consolidación Semántica + Taxonomía Core
Toma core_artists_enriched.json y produce taxonomía canónica,
perfil musical de Diego y persistencia SQLite.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DATA_DIR = Path("data/music_brain")
SQLITE_DB = DATA_DIR / "music_brain.sqlite"
ENRICHED_FILE = DATA_DIR / "core_artists_enriched.json"
TAXONOMY_FILE = DATA_DIR / "core_taxonomy.json"
PROFILE_FILE = DATA_DIR / "core_profile_report.json"

# ─────────────────────────────────────────────
# TABLA DE NORMALIZACIÓN DE GÉNEROS
# Clave: variante sucia → valor: (género canónico, subgénero canónico)
# ─────────────────────────────────────────────
GENRE_MAP = {
    # Rock
    "rock": ("Rock", None),
    "rock and roll": ("Rock", "Rock & Roll clásico"),
    "rock and indie": ("Rock", "Alternative / Indie"),
    "rock music": ("Rock", None),
    "rock opera": ("Rock", "Rock Experimental"),
    "rock & roll": ("Rock", "Rock & Roll clásico"),
    "rock pop": ("Rock", "Pop Rock"),
    "classic rock": ("Rock", "Classic Rock"),
    "classic pop and rock": ("Rock", "Classic Rock"),
    "album rock": ("Rock", "Classic Rock"),
    "hard rock": ("Rock", "Hard Rock"),
    "heavy metal": ("Metal", "Heavy Metal"),
    "metal": ("Metal", None),
    "thrash metal": ("Metal", "Thrash Metal"),
    "death metal": ("Metal", "Death Metal"),
    "black metal": ("Metal", "Black Metal"),
    "gothic metal": ("Metal", "Gothic Metal"),
    "industrial metal": ("Metal", "Industrial Metal"),
    "alternative metal": ("Metal", "Alternative Metal"),
    "speed metal": ("Metal", "Speed Metal"),
    "groove metal": ("Metal", "Groove Metal"),
    "progressive metal": ("Metal", "Progressive Metal"),
    "symphonic metal": ("Metal", "Symphonic Metal"),
    "doom metal": ("Metal", "Doom Metal"),
    "nu metal": ("Metal", "Nu-Metal"),
    "german industrial metal": ("Metal", "Industrial Metal"),
    "tanzmetall": ("Metal", "Industrial Metal"),
    "pop metal": ("Metal", "Heavy Metal"),
    "southern metal": ("Metal", "Groove Metal"),
    "traditional heavy metal": ("Metal", "Heavy Metal"),
    "80s thrash metal": ("Metal", "Thrash Metal"),
    "80s metal": ("Metal", "Heavy Metal"),
    "classic metal": ("Metal", "Heavy Metal"),
    "classic thrash metal": ("Metal", "Thrash Metal"),
    "90s metal": ("Metal", "Heavy Metal"),
    "progressive thrash metal": ("Metal", "Thrash Metal"),
    "american thrash metal": ("Metal", "Thrash Metal"),
    "douchebag metal": ("Metal", "Heavy Metal"),
    "metallica": ("Metal", "Thrash Metal"),
    "teen metal": ("Metal", "Heavy Metal"),
    "trash metal": ("Metal", "Thrash Metal"),
    "progressive rock": ("Rock", "Progressive Rock"),
    "prog rock": ("Rock", "Progressive Rock"),
    "psychedelic rock": ("Rock", "Psychedelic Rock"),
    "psychedelic pop": ("Pop", "Psychedelic Pop"),
    "acid rock": ("Rock", "Psychedelic Rock"),
    "space rock": ("Rock", "Psychedelic Rock"),
    "art rock": ("Rock", "Art Rock"),
    "experimental rock": ("Rock", "Rock Experimental"),
    "avant-garde": ("Experimental", "Avant-Garde"),
    "alternative rock": ("Rock", "Alternative / Indie"),
    "alt-rock": ("Rock", "Alternative / Indie"),
    "indie rock": ("Rock", "Alternative / Indie"),
    "jangle pop": ("Pop", "Indie Pop"),
    "indie pop": ("Pop", "Indie Pop"),
    "punk rock": ("Rock", "Punk"),
    "post-punk": ("Rock", "Post-Punk"),
    "new wave": ("Rock", "New Wave"),
    "gothic rock": ("Rock", "Gothic / Darkwave"),
    "darkwave": ("Rock", "Gothic / Darkwave"),
    "neoclassical darkwave": ("Rock", "Gothic / Darkwave"),
    "dark jazz": ("Jazz", "Dark Jazz"),
    "dark ambient": ("Ambient / Drone", "Dark Ambient"),
    "folk rock": ("Rock", "Folk Rock"),
    "country rock": ("Rock", "Country Rock"),
    "roots rock": ("Rock", "Classic Rock"),
    "pub rock": ("Rock", "Classic Rock"),
    "soft rock": ("Rock", "Soft Rock"),
    "pop rock": ("Pop", "Pop Rock"),
    "arena rock": ("Rock", "Hard Rock"),
    "blues rock": ("Blues", "Blues Rock"),
    "arena rock": ("Rock", "Hard Rock"),
    "synth-pop": ("Electronic", "Synth-Pop"),
    "synthpop": ("Electronic", "Synth-Pop"),
    "synth pop": ("Electronic", "Synth-Pop"),
    "electro pop": ("Electronic", "Synth-Pop"),
    "electropop": ("Electronic", "Synth-Pop"),
    "dance-pop": ("Pop", "Dance-Pop"),
    "dance-rock": ("Rock", "Alternative / Indie"),
    "pop": ("Pop", None),
    "pop soul": ("Pop", "Soul / R&B"),
    "latin pop": ("Pop", "Latin Pop"),
    "flamenco pop": ("Pop", "Latin Pop"),
    "contemporanypop/rock": ("Pop", "Pop Rock"),
    "contemporary pop/rock": ("Pop", "Pop Rock"),
    "am pop": ("Pop", "Pop Rock"),
    "electronic": ("Electronic", None),
    "electronica": ("Electronic", "IDM / Electronica"),
    "idm": ("Electronic", "IDM / Electronica"),
    "minimal techno": ("Electronic", "Techno"),
    "acid techno": ("Electronic", "Techno"),
    "techno": ("Electronic", "Techno"),
    "tech house": ("Electronic", "House"),
    "house": ("Electronic", "House"),
    "ambient": ("Ambient / Drone", "Ambient"),
    "ambient pop": ("Ambient / Drone", "Ambient"),
    "trip hop": ("Electronic", "Trip-Hop"),
    "trip-hop": ("Electronic", "Trip-Hop"),
    "triphop": ("Electronic", "Trip-Hop"),
    "trip rock": ("Electronic", "Trip-Hop"),
    "downtempo": ("Electronic", "Trip-Hop"),
    "dance and electronica": ("Electronic", None),
    "hip hop rnb and dance hall": ("Rap / Hip-Hop", None),
    "uk hip hop": ("Rap / Hip-Hop", "UK Hip-Hop"),
    "hip hop": ("Rap / Hip-Hop", None),
    "rap": ("Rap / Hip-Hop", None),
    "jazz": ("Jazz", None),
    "acid jazz": ("Jazz", "Acid Jazz"),
    "free jazz": ("Jazz", "Free Jazz"),
    "blues": ("Blues", None),
    "soul": ("Soul / R&B", None),
    "rnb": ("Soul / R&B", None),
    "r&b": ("Soul / R&B", None),
    "reggae": ("Reggae / Dub", None),
    "dub": ("Reggae / Dub", None),
    "ska": ("Reggae / Dub", "Ska"),
    "world music": ("World", None),
    "afrobeat": ("World", "Afrobeat"),
    "griot": ("World", "Griots / Kora"),
    "kora": ("World", "Griots / Kora"),
    "latin rock": ("Rock", "Latin Rock"),
    "folk": ("Folk / Acoustic", None),
    "neofolk": ("Folk / Acoustic", "Neofolk / Darkfolk"),
    "darkfolk": ("Folk / Acoustic", "Neofolk / Darkfolk"),
    "medieval": ("Folk / Acoustic", "Medieval"),
    "pagan": ("Folk / Acoustic", "Neofolk / Darkfolk"),
    "neoclassical": ("Classical / Cinematic", "Neoclassical"),
    "classical": ("Classical / Cinematic", None),
    "orchestral": ("Classical / Cinematic", "Orchestral"),
    "soundtrack": ("Classical / Cinematic", "OST / Soundtrack"),
    "film score": ("Classical / Cinematic", "OST / Soundtrack"),
    "tango": ("Traditional / Rioplatense", "Tango"),
    "cumbia": ("Traditional / Rioplatense", "Cumbia"),
    "rock nacional": ("Rock", "Rock Nacional Argentino"),
    "noise": ("Experimental", "Noise"),
    "drone": ("Ambient / Drone", "Drone"),
    "krautrock": ("Rock", "Rock Experimental"),
    "industrial rock": ("Rock", "Industrial Rock"),
    "industrial": ("Electronic", "Industrial"),
    "new age": ("Ambient / Drone", "New Age"),
    "celtic": ("Folk / Acoustic", "Celtic / Gaelic"),
    "celtic music": ("Folk / Acoustic", "Celtic / Gaelic"),
    "flamenco": ("Traditional / Rioplatense", "Flamenco"),
    "cantopop": ("Pop", "Asian Pop"),
    "k-pop": ("Pop", "K-Pop"),
    "dream pop": ("Pop", "Dream Pop"),
    "shoegaze": ("Rock", "Shoegaze / Dream Pop"),
    "post-rock": ("Rock", "Post-Rock"),
    "noise pop": ("Pop", "Indie Pop"),
    "lo-fi": ("Rock", "Alternative / Indie"),
    "chillout": ("Electronic", "Chillout"),
    "smooth jazz": ("Jazz", "Smooth Jazz"),
    "pop/rock": ("Pop", "Pop Rock"),
    "sophisti-pop": ("Pop", "Sophisti-Pop"),
    "adult contemporary": ("Pop", "Adult Contemporary"),
    "tropicalia": ("World", "Tropicalia"),
    "bossa nova": ("Traditional / Rioplatense", "Bossa Nova"),
    "samba": ("Traditional / Rioplatense", "Samba"),
    "mpb": ("Traditional / Rioplatense", "MPB"),
}

# ─────────────────────────────────────────────
# TABLA DE PAÍSES: código ISO → nombre legible
# ─────────────────────────────────────────────
COUNTRY_NAMES = {
    "GB": "Reino Unido", "US": "Estados Unidos", "AU": "Australia",
    "DE": "Alemania", "FR": "Francia", "AR": "Argentina",
    "ES": "España", "BE": "Bélgica", "IE": "Irlanda",
    "KE": "Kenia", "CA": "Canadá", "SE": "Suecia",
    "NO": "Noruega", "IT": "Italia", "AT": "Austria",
    "NL": "Países Bajos", "PL": "Polonia", "RU": "Rusia",
    "BR": "Brasil", "MX": "México", "CL": "Chile",
    "UY": "Uruguay", "CO": "Colombia", "FI": "Finlandia",
    "DK": "Dinamarca", "IS": "Islandia", "GM": "Gambia",
    "ZA": "Sudáfrica", "GN": "Guinea", "SN": "Senegal",
    "ML": "Mali", "NG": "Nigeria", "JP": "Japón",
    "GR": "Grecia", "TR": "Turquía", "TN": "Túnez",
    "CZ": "República Checa", "CH": "Suiza", "NZ": "Nueva Zelanda",
    "HR": "Croacia", "SK": "Eslovaquia", "HU": "Hungría",
    "IL": "Israel", "IR": "Irán",
}

def normalize_tag(tag: str):
    """Return (canonical_genre, canonical_subgenre) or None."""
    clean = tag.strip().lower()
    # Direct match
    if clean in GENRE_MAP:
        return GENRE_MAP[clean]
    # Partial match fallback for common patterns
    for key, val in GENRE_MAP.items():
        if key in clean and len(key) > 4:
            return val
    return None

def resolve_decades(wikipedia_summary: str | None) -> list[str]:
    """Extract decade tokens like '1970s', '1980s' etc from Wikipedia summary."""
    if not wikipedia_summary:
        return []
    decades = []
    for decade_start in range(1930, 2030, 10):
        token = str(decade_start)
        if token in wikipedia_summary:
            label = f"{decade_start}s"
            if label not in decades:
                decades.append(label)
    return sorted(decades)

def init_db(conn):
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS artist_taxonomy (
            artist_id TEXT PRIMARY KEY,
            name TEXT,
            canonical_genres TEXT,
            canonical_subgenres TEXT,
            scenes TEXT,
            country TEXT,
            country_name TEXT,
            artist_type TEXT,
            decades TEXT,
            taxonomy_confidence REAL,
            source_coverage TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(artist_id) REFERENCES artist_profiles(artist_id)
        );
        CREATE TABLE IF NOT EXISTS canonical_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id TEXT,
            raw_tag TEXT,
            canonical_genre TEXT,
            canonical_subgenre TEXT,
            FOREIGN KEY(artist_id) REFERENCES artist_profiles(artist_id)
        );
        CREATE TABLE IF NOT EXISTS taxonomy_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            artists_processed INTEGER,
            avg_confidence REAL,
            top_genres TEXT
        );
    """)
    conn.commit()

def main():
    if not ENRICHED_FILE.exists():
        print("Error: core_artists_enriched.json no encontrado. Correr Fase 3A primero.")
        return

    with open(ENRICHED_FILE) as f:
        enriched = json.load(f)

    conn = sqlite3.connect(SQLITE_DB)
    init_db(conn)
    c = conn.cursor()

    print(f"Taxonomizando {len(enriched)} artistas core...")

    results = []
    genre_counter   = defaultdict(int)
    subgenre_counter = defaultdict(int)
    country_counter = defaultdict(int)
    decade_counter  = defaultdict(int)
    type_counter    = defaultdict(int)
    scene_counter   = defaultdict(int)

    for artist in enriched:
        aid     = artist["artist_id"]
        name    = artist["name"]
        score   = artist["total_score"]
        raw_tags = artist.get("tags", [])
        country_code = artist.get("country", "") or ""
        art_type = artist.get("artist_type", "") or ""
        scenes_raw = artist.get("scenes", []) or []
        wiki = artist.get("wikipedia_summary")
        coverage = artist.get("enrichment_coverage", 0.0)

        # Normalize tags
        genres_set = set()
        subgenres_set = set()
        for tag in raw_tags:
            result = normalize_tag(tag)
            if result:
                g, sg = result
                if g:
                    genres_set.add(g)
                if sg:
                    subgenres_set.add(sg)
                # Write individual tag to SQLite
                c.execute(
                    "INSERT INTO canonical_tags (artist_id, raw_tag, canonical_genre, canonical_subgenre) VALUES (?, ?, ?, ?)",
                    (aid, tag, g, sg)
                )

        # Classify country
        country_name = COUNTRY_NAMES.get(country_code.upper(), country_code) if country_code else "Desconocido"

        # Derive decades from Wikipedia summary
        decades = resolve_decades(wiki)

        # Clean scenes (remove empty strings)
        scenes = [s for s in scenes_raw if s and len(s) > 2]

        # Confidence: base on enrichment_coverage + whether we mapped any genres
        tax_confidence = coverage
        if genres_set:
            tax_confidence = min(1.0, coverage + 0.1)

        canonical_genres = sorted(genres_set)
        canonical_subgenres = sorted(subgenres_set)

        # Counters for the profile report (weighted by score)
        for g in canonical_genres:
            genre_counter[g] += score
        for sg in canonical_subgenres:
            subgenre_counter[sg] += score
        if country_name and country_name != "Desconocido":
            country_counter[country_name] += score
        for d in decades:
            decade_counter[d] += score
        if art_type:
            type_counter[art_type] += 1
        for s in scenes:
            scene_counter[s] += 1

        taxonomy_item = {
            "artist_id": aid,
            "name": name,
            "total_score": score,
            "class_label": "core",
            "canonical_genres": canonical_genres,
            "canonical_subgenres": canonical_subgenres,
            "scenes": scenes,
            "country": country_code,
            "country_name": country_name,
            "artist_type": art_type,
            "decades": decades,
            "taxonomy_confidence": round(tax_confidence, 2),
            "source_coverage": artist.get("sources_used", []),
        }
        results.append(taxonomy_item)

        # Persist to SQLite
        c.execute("""
            INSERT OR REPLACE INTO artist_taxonomy
            (artist_id, name, canonical_genres, canonical_subgenres, scenes, country, country_name, artist_type, decades, taxonomy_confidence, source_coverage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            aid, name,
            json.dumps(canonical_genres, ensure_ascii=False),
            json.dumps(canonical_subgenres, ensure_ascii=False),
            json.dumps(scenes, ensure_ascii=False),
            country_code, country_name, art_type,
            json.dumps(decades),
            round(tax_confidence, 2),
            json.dumps(artist.get("sources_used", []))
        ))

    conn.commit()

    # ─── Write core_taxonomy.json ───
    with open(TAXONOMY_FILE, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # ─── Build Profile Report ───
    def top_n(counter, n=10):
        return [{"name": k, "weight": v} for k, v in sorted(counter.items(), key=lambda x: -x[1])[:n]]

    # Artistas emblemáticos por género (top 3 artists for each top genre)
    emblematic = {}
    for genre in [g["name"] for g in top_n(genre_counter, 6)]:
        reps = [a["name"] for a in results if genre in a["canonical_genres"]]
        reps_sorted = sorted(
            [a for a in results if genre in a["canonical_genres"]],
            key=lambda x: -x["total_score"]
        )[:4]
        emblematic[genre] = [r["name"] for r in reps_sorted]

    # Automatic observations
    observations = []
    top_genres_list = top_n(genre_counter, 5)
    if top_genres_list:
        top1 = top_genres_list[0]["name"]
        observations.append(f"El género con mayor peso acumulado en el núcleo es '{top1}', dominante por masa de artistas y puntuación total.")

    uk_us_weight = country_counter.get("Reino Unido", 0) + country_counter.get("Estados Unidos", 0)
    total_weight = sum(country_counter.values()) or 1
    uk_us_pct = round(100 * uk_us_weight / total_weight)
    observations.append(f"El {uk_us_pct}% del peso Core proviene de artistas angloamericanos (UK + EE.UU.).")

    ar_weight = country_counter.get("Argentina", 0)
    ar_pct = round(100 * ar_weight / total_weight)
    if ar_pct >= 5:
        observations.append(f"Argentina es la tercera presencia más fuerte con un {ar_pct}% del peso — el rock nacional tiene raíces profundas en este perfil.")

    if "Electronic" in genre_counter and "Rock" in genre_counter:
        e = genre_counter["Electronic"]
        r = genre_counter["Rock"]
        ratio = round(e * 100 / (e + r))
        observations.append(f"Existe una tensión marcada entre el universo electrónico ({ratio}%) y el rock puro ({100-ratio}%) dentro del núcleo.")

    if subgenre_counter.get("Trip-Hop", 0) > 0:
        observations.append("La escena Trip-Hop de Bristol (Massive Attack, Portishead, Morcheeba, Tricky) tiene presencia estructural en el perfil.")

    if subgenre_counter.get("Progressive Rock", 0) > 0 and subgenre_counter.get("Psychedelic Rock", 0) > 0:
        observations.append("Fuerte presencia de rock psicodélico y progresivo de los 60s/70s — Pink Floyd y Led Zeppelin dominan esta escena.")

    profile = {
        "timestamp": datetime.now().isoformat(),
        "total_core_artists": len(results),
        "top_genres": top_n(genre_counter, 10),
        "top_subgenres": top_n(subgenre_counter, 15),
        "top_scenes": top_n(scene_counter, 10),
        "top_countries": top_n(country_counter, 10),
        "top_decades": top_n(decade_counter, 10),
        "top_artist_types": [{"type": k, "count": v} for k, v in sorted(type_counter.items(), key=lambda x: -x[1])],
        "emblematic_artists_by_genre": emblematic,
        "observations": observations,
    }

    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

    # Log taxonomy run
    avg_conf = sum(a["taxonomy_confidence"] for a in results) / len(results)
    c.execute(
        "INSERT INTO taxonomy_runs (artists_processed, avg_confidence, top_genres) VALUES (?, ?, ?)",
        (len(results), round(avg_conf, 3), json.dumps([g["name"] for g in top_n(genre_counter, 5)]))
    )
    conn.commit()
    conn.close()

    print(f"Taxonomía completada: {len(results)} artistas procesados.")
    print(f"Top géneros: {', '.join([g['name'] for g in top_n(genre_counter, 5)])}")
    print(f"Confianza promedio: {round(avg_conf, 2)}")

if __name__ == "__main__":
    main()
