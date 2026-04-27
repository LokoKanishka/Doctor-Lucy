#!/usr/bin/env python3
import os
import sys
import json
import requests
import time

# Cargar variables de entorno
def load_env(filepath):
    if not os.path.exists(filepath): return
    with open(filepath) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                try:
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val
                except: pass

load_env("/home/lucy-ubuntu/Escritorio/doctor de lucy/.env")

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
SEARXNG_URL = "http://127.0.0.1:8080/search"

def search_tavily(query):
    if not TAVILY_API_KEY:
        return None, "No TAVILY_API_KEY found"
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "max_results": 5
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 429:
            return None, "Quota exceeded (429)"
        else:
            return None, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return None, str(e)

def search_searxng(query):
    params = {
        "q": query,
        "format": "json",
        "language": "es-ES"
    }
    try:
        response = requests.get(SEARXNG_URL, params=params, timeout=20)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}"
    except Exception as e:
        return None, str(e)

def format_results(results, provider):
    output = f"--- Resultados de Búsqueda ({provider}) ---\n"
    
    if provider == "Tavily":
        if results.get("answer"):
            output += f"Respuesta Directa: {results['answer']}\n\n"
        for res in results.get("results", []):
            output += f"- {res['title']}: {res['url']}\n  {res['content'][:200]}...\n\n"
            
    elif provider == "SearXNG":
        for res in results.get("results", [])[:5]:
            output += f"- {res['title']}: {res.get('url', res.get('pretty_url'))}\n  {res.get('content', '')[:200]}...\n\n"
            
    return output

def master_search(query):
    # 1. Intentar Tavily
    print(f"[*] Intentando búsqueda con Tavily...", file=sys.stderr)
    res, err = search_tavily(query)
    if res:
        return format_results(res, "Tavily")
    
    print(f"[!] Tavily falló: {err}. Intentando SearXNG Local...", file=sys.stderr)
    
    # 2. Intentar SearXNG
    res, err = search_searxng(query)
    if res:
        return format_results(res, "SearXNG")
    
    return f"Error crítico: Todos los proveedores de búsqueda fallaron. Último error: {err}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 master_search.py \"tu consulta\"")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    result = master_search(query)
    print(result)
