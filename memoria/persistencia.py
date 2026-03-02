"""
persistencia.py — Lógica de guardado automático y recuperación de contexto.

Funciones principales:
  - iniciar_sesion(session_id)  → recupera contexto previo o crea sesión nueva
  - auto_save_back(session_id, eventos)  → serializa y persiste la sesión actual
  - cerrar_sesion(session_id)  → marca la sesión como cerrada
"""
import json
import uuid
import datetime
from typing import Optional

from .db import get_connection, inicializar_db


def _estimar_tokens(texto: str) -> int:
    """Estimación rápida: ~4 caracteres por token (aproximación GPT)."""
    return max(1, len(texto) // 4)


def iniciar_sesion(session_id: Optional[str] = None) -> dict:
    """
    Inicializa o recupera una sesión de trabajo.
    
    - Si session_id es None → crea una sesión nueva con UUID.
    - Si session_id ya existe en DB → recupera historial previo.
    
    Retorna:
        {
          'session_id': str,
          'nueva': bool,
          'mensajes': list[dict],  ← historial previo ordenado
          'metadatos': dict,
          'tokens_totales': int,
        }
    """
    inicializar_db()
    
    # --- GARANTÍA DE IDENTIDAD Y JURISDICCIÓN ---
    # Inyectar las reglas de oro de Doctora Lucy en cada inicio.
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO sesiones (session_id, estado) VALUES ('global', 'activa')")
        conn.execute("INSERT OR REPLACE INTO metadatos (session_id, clave, valor) VALUES ('global', 'nombre_asistente', 'Doctora Lucy')")
        conn.execute("INSERT OR REPLACE INTO metadatos (session_id, clave, valor) VALUES ('global', 'nombre_usuario', 'Diego')")
        conn.execute("INSERT OR REPLACE INTO metadatos (session_id, clave, valor) VALUES ('global', 'rol_alt', 'demonio bebe 14b')")
        conn.execute(
            "INSERT OR REPLACE INTO metadatos (session_id, clave, valor) VALUES ('global', 'directiva_oro', "
            "'Diagnosticar y proponer soluciones. Prohibido alterar proyectos externos sin orden explícita.')"
        )
        conn.commit()
    # --------------------------------------------
    
    if session_id is None:
        session_id = str(uuid.uuid4())

    with get_connection() as conn:
        # ¿Existe ya?
        row = conn.execute(
            "SELECT * FROM sesiones WHERE session_id = ?", (session_id,)
        ).fetchone()

        if row is None:
            # Sesión nueva
            conn.execute(
                "INSERT INTO sesiones (session_id) VALUES (?)", (session_id,)
            )
            print(f"[memoria] Nueva sesión creada: {session_id}")
            return {
                "session_id": session_id,
                "nueva": True,
                "mensajes": [],
                "metadatos": {},
                "tokens_totales": 0,
            }
        else:
            # Sesión existente → cargar historial
            mensajes = [
                dict(m)
                for m in conn.execute(
                    "SELECT rol, contenido_json, timestamp FROM mensajes "
                    "WHERE session_id = ? ORDER BY id ASC",
                    (session_id,)
                ).fetchall()
            ]
            # Deserializar contenido_json
            for m in mensajes:
                try:
                    m["contenido"] = json.loads(m["contenido_json"])
                except json.JSONDecodeError:
                    m["contenido"] = m["contenido_json"]

            metas_rows = conn.execute(
                "SELECT clave, valor FROM metadatos WHERE session_id = ?",
                (session_id,)
            ).fetchall()
            metadatos = {r["clave"]: r["valor"] for r in metas_rows}

            print(
                f"[memoria] Sesión recuperada: {session_id} "
                f"({len(mensajes)} mensajes, {row['tokens_totales']} tokens)"
            )
            return {
                "session_id": session_id,
                "nueva": False,
                "mensajes": mensajes,
                "metadatos": metadatos,
                "tokens_totales": row["tokens_totales"],
                "resumen": row["resumen"],
            }


def auto_save_back(session_id: str, eventos: list, metadatos: Optional[dict] = None) -> int:
    """
    Guarda automáticamente el estado actual de la sesión en SQLite.
    
    Parámetros:
        session_id  : ID de la sesión activa.
        eventos     : Lista de dicts con keys 'rol' y 'contenido' (str o dict).
        metadatos   : Pares clave-valor opcionales para guardar decisiones, artefactos, etc.
    
    Retorna el total de tokens estimados acumulados.
    
    Llamar después de CADA respuesta del modelo para no perder contexto.
    """
    tokens_acum = 0

    with get_connection() as conn:
        # Verificar que la sesión existe
        existe = conn.execute(
            "SELECT 1 FROM sesiones WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not existe:
            raise ValueError(f"session_id '{session_id}' no existe. Llama primero a iniciar_sesion().")

        # Insertar mensajes nuevos (solo los que no están ya guardados)
        ya_guardados = conn.execute(
            "SELECT COUNT(*) FROM mensajes WHERE session_id = ?", (session_id,)
        ).fetchone()[0]

        nuevos = eventos[ya_guardados:]  # solo los eventos nuevos

        for evento in nuevos:
            rol = evento.get("rol", "unknown")
            contenido = evento.get("contenido", "")
            contenido_json = json.dumps(contenido, ensure_ascii=False)
            tokens = _estimar_tokens(contenido_json)
            tokens_acum += tokens

            conn.execute(
                "INSERT INTO mensajes (session_id, rol, contenido_json, tokens_est) "
                "VALUES (?, ?, ?, ?)",
                (session_id, rol, contenido_json, tokens)
            )

        # Actualizar total de tokens en sesiones
        conn.execute(
            "UPDATE sesiones SET tokens_totales = tokens_totales + ? WHERE session_id = ?",
            (tokens_acum, session_id)
        )

        # Guardar metadatos adicionales
        if metadatos:
            for clave, valor in metadatos.items():
                conn.execute(
                    "INSERT OR REPLACE INTO metadatos (session_id, clave, valor) VALUES (?, ?, ?)",
                    (session_id, clave, str(valor))
                )

    total_tokens = conn.execute(
        "SELECT tokens_totales FROM sesiones WHERE session_id = ?", (session_id,)
    ).fetchone()
    total = total_tokens[0] if total_tokens else tokens_acum
    return total


def cerrar_sesion(session_id: str) -> None:
    """Marca la sesión como cerrada con timestamp actual."""
    ahora = datetime.datetime.now().isoformat()
    with get_connection() as conn:
        conn.execute(
            "UPDATE sesiones SET estado = 'cerrada', cerrada_en = ? WHERE session_id = ?",
            (ahora, session_id)
        )
    print(f"[memoria] Sesión cerrada: {session_id}")
