#!/usr/bin/env python3
import json
import argparse
import sys
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("data/music_brain")
REPORT_JSON = DATA_DIR / "core_profile_report.json"
TAXONOMY_JSON = DATA_DIR / "core_taxonomy.json"

def load_json(path):
    if not path.exists():
        print(f"Error: No se encontró la base en {path}")
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)

def load_data():
    report = load_json(REPORT_JSON)
    taxonomy_data = load_json(TAXONOMY_JSON)
    # Ensure taxonomy is a list
    if isinstance(taxonomy_data, dict):
        taxonomy = list(taxonomy_data.values())
    else:
        taxonomy = taxonomy_data
    return report, taxonomy

def print_header(title):
    print(f"\n=== {title.upper()} ===")
    
def print_kv(key, value):
    print(f"{key+':':<15} {value}")

def cmd_summary(report, taxonomy):
    total_artists = report.get('total_core_artists', len(taxonomy))
    total_score = sum(a.get('total_score', 0) for a in taxonomy)
    
    genres = report.get('top_genres', [])
    countries = report.get('top_countries', [])
    scenes = report.get('top_scenes', [])
    
    print_header("Music Brain Core Summary")
    print_kv("Total Artists", total_artists)
    print_kv("Total Score", total_score)
    print_kv("Unique Genres", len(genres))
    print_kv("Unique Scenes", len(scenes))
    print_kv("Unique Countries", len(countries))
    print("\nObservaciones Core:")
    for obs in report.get('observations', []):
        print(f"-> {obs}")

def print_top_list(title, items):
    print_header(title)
    if not items:
        print("No data available.")
        return
    for i, item in enumerate(items[:20], 1):
        name = item.get('name', str(item))
        weight = item.get('weight', item.get('count', 0))
        print(f"{i:2d}. {name:<25} (Weight: {weight:.0f})")

def cmd_top_genres(report):
    print_top_list("Top Canonical Genres", report.get('top_genres', []))

def cmd_top_subgenres(report):
    print_top_list("Top Canonical Subgenres", report.get('top_subgenres', []))

def cmd_top_scenes(report):
    print_top_list("Top Local Scenes", report.get('top_scenes', []))

def cmd_top_countries(report):
    print_top_list("Top Countries", report.get('top_countries', []))

def cmd_top_decades(report):
    print_top_list("Top Decades of Activity", report.get('top_decades', []))

def cmd_top_artists(taxonomy):
    ranked = sorted(taxonomy, key=lambda x: x.get('total_score', 0), reverse=True)
    print_header("Top Core Artists")
    for i, a in enumerate(ranked[:20], 1):
        print(f"{i:2d}. {a['name']:<25} (Score: {a.get('total_score', 0)})")

def fuzzy_match(query, target):
    q = str(query).lower().replace(" ", "")
    t = str(target).lower().replace(" ", "")
    return q in t

def cmd_artist(taxonomy, query):
    matches = [a for a in taxonomy if fuzzy_match(query, a.get('name', ''))]
    if not matches:
        print(f"Error: Artist '{query}' not found in core taxonomy.")
        sys.exit(1)
        
    a = matches[0]
    print_header(f"Artist Profile: {a.get('name', 'Unknown')}")
    print_kv("Score", a.get('total_score', 0))
    print_kv("Class", a.get('class_label', 'Unknown'))
    print_kv("Type", a.get('artist_type', 'Unknown'))
    print_kv("Country", a.get('country_name', 'Unknown'))
    
    genres = ", ".join(a.get('canonical_genres', []))
    print_kv("Genres", genres if genres else "None")
    
    subgenres = ", ".join(a.get('canonical_subgenres', []))
    print_kv("Subgenres", subgenres if subgenres else "None")
    
    scenes = ", ".join(a.get('scenes', []))
    print_kv("Scenes", scenes if scenes else "None")
    
    decades = ", ".join(a.get('decades', []))
    print_kv("Decades", decades if decades else "None")

    if len(matches) > 1:
        print("\nNote: Multiple partial matches found. Showing best match.")

def query_association(taxonomy, list_field, query, title):
    print_header(f"Artists associated with {title}: {query}")
    matches = []
    for a in taxonomy:
        items = a.get(list_field, [])
        if any(fuzzy_match(query, i) for i in items):
            matches.append(a)
            
    if not matches:
        print(f"No artists found for {title.lower()}: '{query}'")
        return
        
    matches = sorted(matches, key=lambda x: x.get('total_score',0), reverse=True)
    for i, a in enumerate(matches[:20], 1):
        print(f"{i:2d}. {a.get('name', 'Unknown'):<25} (Score: {a.get('total_score', 0)})")
        
    if len(matches) > 20:
        print(f"... and {len(matches)-20} more.")

def cmd_genre(taxonomy, query):
    query_association(taxonomy, 'canonical_genres', query, "Genre")

def cmd_scene(taxonomy, query):
    query_association(taxonomy, 'scenes', query, "Scene")
    
def cmd_country(taxonomy, query):
    print_header(f"Artists from Country: {query}")
    matches = [a for a in taxonomy if a.get('country_name') and fuzzy_match(query, a.get('country_name'))]
    
    if not matches:
        print(f"No artists found for country: '{query}'")
        return
        
    matches = sorted(matches, key=lambda x: x.get('total_score',0), reverse=True)
    for i, a in enumerate(matches[:20], 1):
        print(f"{i:2d}. {a.get('name', 'Unknown'):<25} (Score: {a.get('total_score', 0)})")
        
    if len(matches) > 20:
        print(f"... and {len(matches)-20} more.")

def cmd_decade(taxonomy, query):
    query_association(taxonomy, 'decades', query, "Decade")

def cmd_compare(taxonomy, e1, e2):
    print_header(f"Comparison: {e1} vs {e2}")
    
    def score_term(term):
        score = 0
        match_count = 0
        term_norm = term.lower()
        for a in taxonomy:
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
    parser = argparse.ArgumentParser(description="Music Brain Local Query Layer - Core Taxonomy")
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
    report, taxonomy = load_data()
    
    if args.command == "summary":
        cmd_summary(report, taxonomy)
    elif args.command == "top-genres":
        cmd_top_genres(report)
    elif args.command == "top-subgenres":
        cmd_top_subgenres(report)
    elif args.command == "top-scenes":
        cmd_top_scenes(report)
    elif args.command == "top-countries":
        cmd_top_countries(report)
    elif args.command == "top-decades":
        cmd_top_decades(report)
    elif args.command == "top-artists":
        cmd_top_artists(taxonomy)
    elif args.command == "artist":
        cmd_artist(taxonomy, args.name)
    elif args.command == "genre":
        cmd_genre(taxonomy, args.name)
    elif args.command == "scene":
        cmd_scene(taxonomy, args.name)
    elif args.command == "country":
        cmd_country(taxonomy, args.name)
    elif args.command == "decade":
        cmd_decade(taxonomy, args.name)
    elif args.command == "compare":
        cmd_compare(taxonomy, args.axis1, args.axis2)
