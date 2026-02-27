"""
herramientas.py — Tool de recuperación selectiva de memoria.

Función principal:
  - consultar_historial(palabras_clave, session_id, limite) 
    → Búsqueda por keywords en SQLite, retorna SOLO los fragmentos relevantes.
    
El objetivo es no saturar la ventana de contexto del modelo:
se inyecta solo lo necesario, no toda la base de datos.
"""
import json
import hashlib
from typing import Optional

from .db import get_connection


def consultar_historial(
    palabras_clave: str,
    session_id: Optional[str] = None,
    limite: int = 10
) -> list[dict]:
    """
    Búsqueda de contexto histórico por palabras clave.
    
    Parámetros:
        palabras_clave : Término(s) de búsqueda, separados por espacios.
        session_id     : Si se provee, limita la búsqueda a esa sesión.
                         Si None, busca en TODAS las sesiones.
        limite         : Máximo de resultados a retornar (default: 10).
    
    Retorna:
        Lista de dicts con: session_id, rol, fragmento de contenido, timestamp.
        
    Ejemplo de uso (el agente lo llama autónomamente):
        resultados = consultar_historial("esquema Docker puerto 7851")
    """
    keywords = [k.strip() for k in palabras_clave.split() if k.strip()]
    if not keywords:
        return []

    with get_connection() as conn:
        resultados = []

        for keyword in keywords:
            patron = f"%{keyword}%"
            if session_id:
                rows = conn.execute(
                    "SELECT session_id, rol, contenido_json, timestamp "
                    "FROM mensajes "
                    "WHERE session_id = ? AND contenido_json LIKE ? "
                    "ORDER BY id DESC LIMIT ?",
                    (session_id, patron, limite)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT session_id, rol, contenido_json, timestamp "
                    "FROM mensajes "
                    "WHERE contenido_json LIKE ? "
                    "ORDER BY id DESC LIMIT ?",
                    (patron, limite)
                ).fetchall()

            for row in rows:
                try:
                    contenido = json.loads(row["contenido_json"])
                    if isinstance(contenido, str):
                        fragmento = contenido[:500]  # max 500 chars por fragmento
                    else:
                        fragmento = json.dumps(contenido, ensure_ascii=False)[:500]
                except Exception:
                    fragmento = str(row["contenido_json"])[:500]

                resultados.append({
                    "session_id": row["session_id"],
                    "rol": row["rol"],
                    "fragmento": fragmento,
                    "timestamp": row["timestamp"],
                    "keyword_match": keyword,
                })

        # Deduplicar por fragmento
        vistos = set()
        unicos = []
        for r in resultados:
            key = r["fragmento"][:100]
            if key not in vistos:
                vistos.add(key)
                unicos.append(r)

    return unicos[:limite]


def consultar_cache(consulta: str) -> Optional[str]:
    """
    Recupera un resultado previamente cacheado por hash SHA256 de la consulta.
    Retorna None si no existe o si expiró.
    """
    hash_clave = hashlib.sha256(consulta.encode()).hexdigest()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT resultado, expira_en FROM cache_global WHERE clave_hash = ?",
            (hash_clave,)
        ).fetchone()

    if row is None:
        return None

    # Verificar expiración
    if row["expira_en"] is not None:
        from datetime import datetime
        if datetime.now().isoformat() > row["expira_en"]:
            return None  # expirado

    return row["resultado"]


def guardar_cache(consulta: str, resultado: str, origen: str = "manual", ttl_horas: Optional[int] = None) -> None:
    """
    Guarda un resultado en el caché global.
    
    Parámetros:
        consulta  : Texto de la consulta (se hashea).
        resultado : Resultado a cachear (JSON string o texto plano).
        origen    : Nombre de la herramienta que generó el resultado.
        ttl_horas : Horas hasta expiración. None = sin expiración.
    """
    hash_clave = hashlib.sha256(consulta.encode()).hexdigest()
    expira_en = None
    if ttl_horas is not None:
        from datetime import datetime, timedelta
        expira_en = (datetime.now() + timedelta(hours=ttl_horas)).isoformat()

    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO cache_global (clave_hash, resultado, origen, expira_en) "
            "VALUES (?, ?, ?, ?)",
            (hash_clave, resultado, origen, expira_en)
        )
