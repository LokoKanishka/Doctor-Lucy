#!/usr/bin/env python3
import json
import argparse
import sys
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("data/music_brain")
REPORT_JSON = DATA_DIR / "core_artists_enriched.json"

def load_data():
    if not REPORT_JSON.exists():
        print(f"Error: No se encontró la base de perfil core en {REPORT_JSON}")
        sys.exit(1)
    with open(REPORT_JSON, "r") as f:
        return json.load(f)

def print_header(title):
    print(f"\n=== {title.upper()} ===")
    
def print_kv(key, value):
    print(f"{key+':':<15} {value}")

def cmd_summary(data):
    total_artists = len(data)
    total_score = sum(a.get('total_score', 0) for a in data)
    
    genres = set()
    countries = set()
    for a in data:
        genres.update(a.get('canonical_genres', []))
        if a.get('country'):
            countries.add(a.get('country_name'))
            
    print_header("Music Brain Core Summary")
    print_kv("Total Artists", total_artists)
    print_kv("Total Score", total_score)
    print_kv("Unique Genres", len(genres))
    print_kv("Unique Countries", len(countries))
    print("\nObservaciones:")
    print("-> Perfil base establecido con alta consolidación de entidades.")
    print("-> Listo para consulta multidimensional local.")

def get_top_elements(data, field, is_list=True):
    counts = defaultdict(float)
    for a in data:
        score = a.get('total_score', 0)
        items = a.get(field)
        if items:
            if is_list:
                for item in items:
                    counts[item] += score
            else:
                counts[items] += score
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)

def cmd_top_genres(data):
    ranked = get_top_elements(data, 'tags', is_list=True)
    print_header("Top Tags/Genres (by Artist Score)")
    for i, (genre, score) in enumerate(ranked[:20], 1):
        print(f"{i:2d}. {genre:<25} (Score: {score:.0f})")

def cmd_top_subgenres(data):
    # En la base enriquecida (core_artists_enriched.json), géneros y subgéneros
    # están acoplados en la lista "tags" (o lastfm_tags). Se imprimirá una 
    # variante de tags para no romper la interfaz solicitada.
    ranked = get_top_elements(data, 'lastfm_tags', is_list=True)
    print_header("Top Last.fm Tags (by Artist Score)")
    if not ranked:
        print("No Last.fm tags currently indexed.")
    for i, (sub, score) in enumerate(ranked[:20], 1):
        print(f"{i:2d}. {sub:<25} (Score: {score:.0f})")

def cmd_top_scenes(data):
    ranked = get_top_elements(data, 'scenes', is_list=True)
    print_header("Top Local Scenes (by Artist Score)")
    if not ranked:
        print("No scenes currently indexed.")
    for i, (scene, score) in enumerate(ranked[:20], 1):
        print(f"{i:2d}. {scene:<35} (Score: {score:.0f})")

def cmd_top_countries(data):
    ranked = get_top_elements(data, 'country_name', is_list=False)
    print_header("Top Countries (by Artist Score)")
    for i, (country, score) in enumerate(ranked[:15], 1):
        if country and country != 'Desconocido':
            print(f"{i:2d}. {country:<20} (Score: {score:.0f})")

def cmd_top_decades(data):
    ranked = get_top_elements(data, 'decades', is_list=True)
    print_header("Top Decades of Activity (by Artist Score)")
    for i, (decade, score) in enumerate(ranked, 1):
        print(f"{i:2d}. {decade:<10} (Score: {score:.0f})")

def cmd_top_artists(data):
    ranked = sorted(data, key=lambda x: x.get('total_score', 0), reverse=True)
    print_header("Top Core Artists")
    for i, a in enumerate(ranked[:20], 1):
        print(f"{i:2d}. {a['name']:<25} (Score: {a.get('total_score', 0)})")

def fuzzy_match(query, target):
    q = query.lower().replace(" ", "")
    t = target.lower().replace(" ", "")
    return q in t

def cmd_artist(data, query):
    matches = [a for a in data if fuzzy_match(query, a['name'])]
    if not matches:
        print(f"Error: Artist '{query}' not found in core profile.")
        sys.exit(1)
        
    a = matches[0]
    print_header(f"Artist Profile: {a['name']}")
    print_kv("Score", a.get('total_score', 0))
    print_kv("Class", a.get('class_label', 'Unknown'))
    print_kv("Type", a.get('artist_type', 'Unknown'))
    print_kv("Country", a.get('country_name', 'Unknown'))
    
    genres = ", ".join(a.get('tags', []))
    print_kv("Primary Tags", genres if genres else "None")
    
    subgenres = ", ".join(a.get('lastfm_tags', []))
    print_kv("Last.fm Tags", subgenres if subgenres else "None")
    
    scenes = ", ".join(a.get('scenes', []))
    print_kv("Scenes", scenes if scenes else "None")
    
    decades = ", ".join(a.get('decades', []))
    print_kv("Decades", decades if decades else "None")
    
    sources = ", ".join(a.get('source_coverage', []))
    print_kv("Sources", sources if sources else "None")

    if len(matches) > 1:
        print("\nNote: Multiple partial matches found. Showing best match.")

def query_association(data, list_field, query, title):
    print_header(f"Artists associated with {title}: {query}")
    matches = []
    for a in data:
        items = a.get(list_field, [])
        if any(fuzzy_match(query, i) for i in items):
            matches.append(a)
            
    if not matches:
        print(f"No artists found for {title.lower()}: '{query}'")
        return
        
    matches = sorted(matches, key=lambda x: x.get('total_score',0), reverse=True)
    for i, a in enumerate(matches[:20], 1):
        print(f"{i:2d}. {a['name']:<25} (Score: {a.get('total_score', 0)})")
        
    if len(matches) > 20:
        print(f"... and {len(matches)-20} more.")

def cmd_genre(data, query):
    query_association(data, 'tags', query, "Genre/Tag")

def cmd_scene(data, query):
    query_association(data, 'scenes', query, "Scene")
    
def cmd_country(data, query):
    print_header(f"Artists from Country: {query}")
    matches = [a for a in data if a.get('country_name') and fuzzy_match(query, a['country_name'])]
    
    if not matches:
        print(f"No artists found for country: '{query}'")
        return
        
    matches = sorted(matches, key=lambda x: x.get('total_score',0), reverse=True)
    for i, a in enumerate(matches[:20], 1):
        print(f"{i:2d}. {a['name']:<25} (Score: {a.get('total_score', 0)})")
        
    if len(matches) > 20:
        print(f"... and {len(matches)-20} more.")

def cmd_decade(data, query):
    query_association(data, 'decades', query, "Decade")

def cmd_compare(data, e1, e2):
    print_header(f"Comparison: {e1} vs {e2}")
    
    def score_term(term):
        score = 0
        match_count = 0
        term_norm = term.lower()
        for a in data:
            # Check generically across all string fields and list fields
            matched = False
            for v in a.values():
                if isinstance(v, str) and term_norm in v.lower():
                    matched = True
                elif isinstance(v, list) and any(isinstance(i, str) and term_norm in i.lower() for i in v):
                    matched = True
            
            if matched:
                score += a.get('total_score', 0)
                match_count += 1
        return score, match_count

    s1, c1 = score_term(e1)
    s2, c2 = score_term(e2)
    
    print(f"--> '{e1}'")
    print(f"    Artists matched: {c1}")
    print(f"    Total Weight:    {s1:.0f}")
    
    print(f"\n--> '{e2}'")
    print(f"    Artists matched: {c2}")
    print(f"    Total Weight:    {s2:.0f}")
    
    if s1 > s2:
        print(f"\nResult: '{e1}' is more dominant in the core profile.")
    elif s2 > s1:
        print(f"\nResult: '{e2}' is more dominant in the core profile.")
    else:
        print(f"\nResult: Roughly equal weighting.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Music Brain Local Query Layer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("summary", help="Resumen global del perfil")
    subparsers.add_parser("top-genres", help="Listar top generos")
    subparsers.add_parser("top-subgenres", help="Listar top subgeneros")
    subparsers.add_parser("top-scenes", help="Listar top escenas")
    subparsers.add_parser("top-countries", help="Listar top paises")
    subparsers.add_parser("top-decades", help="Listar decadas de mayor actividad")
    subparsers.add_parser("top-artists", help="Listar artistas con mayor score")
    
    artist_p = subparsers.add_parser("artist", help="Info de un artista específico")
    artist_p.add_argument("name", help="Nombre del artista")
    
    genre_p = subparsers.add_parser("genre", help="Artistas en un género")
    genre_p.add_argument("name", help="Nombre del género")
    
    scene_p = subparsers.add_parser("scene", help="Artistas en una escena")
    scene_p.add_argument("name", help="Nombre de la escena")
    
    country_p = subparsers.add_parser("country", help="Artistas por país")
    country_p.add_argument("name", help="Nombre del país")
                 
    decade_p = subparsers.add_parser("decade", help="Artistas por década")
    decade_p.add_argument("name", help="Década (ej. 1990s)")
    
    compare_p = subparsers.add_parser("compare", help="Comparar dos ejes")
    compare_p.add_argument("axis1", help="Término 1")
    compare_p.add_argument("axis2", help="Término 2")
    
    args = parser.parse_args()
    data = load_data()
    
    if args.command == "summary":
        cmd_summary(data)
    elif args.command == "top-genres":
        cmd_top_genres(data)
    elif args.command == "top-subgenres":
        cmd_top_subgenres(data)
    elif args.command == "top-scenes":
        cmd_top_scenes(data)
    elif args.command == "top-countries":
        cmd_top_countries(data)
    elif args.command == "top-decades":
        cmd_top_decades(data)
    elif args.command == "top-artists":
        cmd_top_artists(data)
    elif args.command == "artist":
        cmd_artist(data, args.name)
    elif args.command == "genre":
        cmd_genre(data, args.name)
    elif args.command == "scene":
        cmd_scene(data, args.name)
    elif args.command == "country":
        cmd_country(data, args.name)
    elif args.command == "decade":
        cmd_decade(data, args.name)
    elif args.command == "compare":
        cmd_compare(data, args.axis1, args.axis2)
