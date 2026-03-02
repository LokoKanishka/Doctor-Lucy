import os
import json
import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import pathlib

# Cargar variables de entorno
env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

QDRANT_HOST = "127.0.0.1"
QDRANT_PORT = 6333
COLLECTION_NAME = "conciencia_doctor_lucy"
# Ollama config para embeddings
OLLAMA_EMBED_URL = "http://127.0.0.1:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"
OLLAMA_TIMEOUT = 5 # Timeout estricto en segundos (Fail-Fast)
QDRANT_TIMEOUT = 5 # Timeout para la DB Vectorial

class ConcienciaRAG:
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=QDRANT_TIMEOUT)
        self._inicializar_coleccion()

    def _inicializar_coleccion(self):
        """Crea la colección o la recrea si las dimensiones no coinciden."""
        collections = self.client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        target_size = 768 # Nomic size
        
        if exists:
            # Check dimensions to avoid 3072 (Gemini) vs 768 (Nomic) mismatch
            collection_info = self.client.get_collection(COLLECTION_NAME)
            current_size = collection_info.config.params.vectors.size
            if current_size != target_size:
                print(f"[RAG] Dimensiones incompatibles detectadas ({current_size} vs {target_size}). Recreando índice...")
                self.client.delete_collection(COLLECTION_NAME)
                exists = False
                
        if not exists:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=target_size, distance=models.Distance.COSINE),
            )
            print(f"[RAG] Colección '{COLLECTION_NAME}' creada con {target_size} dimensiones.")

    def generar_embedding(self, texto: str):
        """Genera embedding usando Ollama local (Fail-Fast)."""
        try:
            response = requests.post(
                OLLAMA_EMBED_URL,
                json={"model": OLLAMA_MODEL, "prompt": texto},
                timeout=OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        except requests.exceptions.Timeout:
            raise RuntimeError(f"[RAG FAIL-FAST] Timeout conectando a Ollama ({OLLAMA_TIMEOUT}s). El servicio local no responde.")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("[RAG FAIL-FAST] Conexión rechazada por Ollama. ¿Está el servicio corriendo en 11434?")
        except Exception as e:
            raise RuntimeError(f"[RAG FAIL-FAST] Error inesperado en embeddings: {e}")

    def guardar_fragmento(self, texto: str, metadata: dict):
        """Guarda un fragmento de texto con sus metadatos en Qdrant."""
        vector = self.generar_embedding(texto)
        point_id = hash(texto) % (2**63) # ID simple basado en hash
        
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"text": texto, **metadata}
                )
            ]
        )

    def buscar_similares(self, consulta: str, limite: int = 5):
        """Busca los fragmentos más parecidos a la consulta."""
        vector_consulta = self.generar_embedding(consulta)
        
        search_result = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector_consulta,
            limit=limite
        )
        
        return [hit.payload for hit in search_result.points]

if __name__ == "__main__":
    # Prueba rápida
    rag = ConcienciaRAG()
    test_text = "Esta es una prueba de la memoria infinita de Doctor Lucy."
    rag.guardar_fragmento(test_text, {"tipo": "test", "autor": "Antigravity"})
    
    resultados = rag.buscar_similares("¿Cómo es la memoria de Lucy?")
    print("Resultados de búsqueda semántica:")
    for res in resultados:
        print(f" - {res['text']}")
