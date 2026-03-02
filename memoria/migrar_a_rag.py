import sqlite3
import json
from conciencia_rag import ConcienciaRAG
from db import get_connection
import tqdm

def migrar():
    rag = ConcienciaRAG()
    
    print("[MIGRACIÓN] Conectando a SQLite para leer historial...")
    with get_connection() as conn:
        mensajes = conn.execute(
            "SELECT session_id, rol, contenido_json, timestamp FROM mensajes"
        ).fetchall()
    
    total = len(mensajes)
    print(f"[MIGRACIÓN] Se encontraron {total} mensajes. Iniciando indexación semántica...")
    
    for row in tqdm.tqdm(mensajes):
        try:
            texto = json.loads(row["contenido_json"])
            if not isinstance(texto, str):
                texto = json.dumps(texto, ensure_ascii=False)
            
            # Solo indexamos si tiene contenido real y no es demasiado corto
            if len(texto) > 10:
                metadata = {
                    "session_id": row["session_id"],
                    "rol": row["rol"],
                    "timestamp": row["timestamp"],
                    "fuente": "sqlite_migration"
                }
                rag.guardar_fragmento(texto, metadata)
        except Exception as e:
            print(f"Error al migrar mensaje: {e}")

    print(f"[MIGRACIÓN] ¡Completada! {total} mensajes procesados.")

if __name__ == "__main__":
    migrar()
