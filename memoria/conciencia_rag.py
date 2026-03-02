import os
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models
import google.generativeai as genai
from dotenv import load_dotenv
import pathlib

# Cargar variables de entorno
env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_HOST = "127.0.0.1"
QDRANT_PORT = 6333
COLLECTION_NAME = "conciencia_doctor_lucy"

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)

class ConcienciaRAG:
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self._inicializar_coleccion()

    def _inicializar_coleccion(self):
        """Crea la colección si no existe."""
        collections = self.client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if not exists:
            # gemini-embedding-001 tiene 3072 dimensiones
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE),
            )
            print(f"[RAG] Colección '{COLLECTION_NAME}' creada.")

    def generar_embedding(self, texto: str):
        """Genera embedding usando Gemini."""
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=texto,
            task_type="retrieval_document",
            title="Conciencia Memoria"
        )
        return result['embedding']

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
