import os
import requests
from dotenv import load_dotenv
import pathlib

# Cargar variables de entorno
env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def buscar_web(query: str):
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "include_answer": True
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "detail": response.text}

if __name__ == "__main__":
    print(f"[OJOS] Probando visión web para: 'Últimas noticias sobre n8n y IA'...")
    resultado = buscar_web("últimas noticias sobre n8n y agentes de IA")
    
    if "answer" in resultado:
        print(f"\nRespuesta Inteligente:\n{resultado['answer']}")
    elif "results" in resultado:
        print("\nResultados encontrados:")
        for res in resultado["results"][:3]:
            print(f" - {res['title']}: {res['url']}")
    else:
        print(f"Error o sin resultados: {resultado}")
