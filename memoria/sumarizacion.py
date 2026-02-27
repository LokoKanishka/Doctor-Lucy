"""
sumarizacion.py — Compresión de sesiones largas para evitar saturación de contexto.

Función principal:
  - comprimir_sesion(session_id, limite_tokens, fn_resumir)
    → Si la sesión supera el límite, genera un resumen ejecutivo y libera la memoria activa.
"""
import json
from typing import Callable, Optional

from .db import get_connection


# Límite por defecto: ~100k tokens (configurable)
LIMITE_TOKENS_DEFAULT = 100_000


def comprimir_sesion(
    session_id: str,
    limite_tokens: int = LIMITE_TOKENS_DEFAULT,
    fn_resumir: Optional[Callable[[list[dict]], str]] = None
) -> dict:
    """
    Comprime la sesión si supera el límite de tokens.
    
    Mecánica:
    1. Consulta el total de tokens de la sesión.
    2. Si supera el límite, recupera todos los mensajes.
    3. Genera un resumen ejecutivo (via fn_resumir o resumen automático).
    4. Guarda el resumen en la tabla sesiones.
    5. Elimina los mensajes viejos de la tabla mensajes (libera espacio).
    6. Inserta el resumen como un único mensaje de sistema al inicio.
    
    Parámetros:
        session_id    : ID de la sesión a comprimir.
        limite_tokens : Umbral de tokens para activar la compresión.
        fn_resumir    : Función opcional que recibe lista de mensajes y retorna string resumen.
                        Si es None, usa el resumen automático interno.
    
    Retorna:
        {
          'comprimida': bool,
          'tokens_antes': int,
          'tokens_despues': int,
          'resumen': str,
        }
    """
    with get_connection() as conn:
        # 1. Verificar estado actual
        sesion = conn.execute(
            "SELECT tokens_totales, resumen FROM sesiones WHERE session_id = ?",
            (session_id,)
        ).fetchone()

        if sesion is None:
            raise ValueError(f"session_id '{session_id}' no existe.")

        tokens_antes = sesion["tokens_totales"]

        if tokens_antes < limite_tokens:
            return {
                "comprimida": False,
                "tokens_antes": tokens_antes,
                "tokens_despues": tokens_antes,
                "resumen": sesion["resumen"] or "",
            }

        # 2. Recuperar todos los mensajes
        mensajes = [
            dict(m) for m in conn.execute(
                "SELECT rol, contenido_json FROM mensajes "
                "WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            ).fetchall()
        ]

        # 3. Generar resumen
        if fn_resumir is not None:
            resumen = fn_resumir(mensajes)
        else:
            resumen = _resumir_automatico(mensajes)

        # 4. Actualizar resumen en sesiones
        conn.execute(
            "UPDATE sesiones SET resumen = ?, estado = 'comprimida', tokens_totales = ? "
            "WHERE session_id = ?",
            (resumen, len(resumen) // 4, session_id)
        )

        # 5. Eliminar mensajes viejos
        conn.execute(
            "DELETE FROM mensajes WHERE session_id = ?", (session_id,)
        )

        # 6. Insertar el resumen como mensaje de sistema inaugural
        resumen_json = json.dumps(
            {"tipo": "resumen_comprimido", "contenido": resumen},
            ensure_ascii=False
        )
        conn.execute(
            "INSERT INTO mensajes (session_id, rol, contenido_json, tokens_est) VALUES (?, ?, ?, ?)",
            (session_id, "system", resumen_json, len(resumen) // 4)
        )

        tokens_despues = len(resumen) // 4
        print(
            f"[memoria] Sesión comprimida: {session_id} | "
            f"{tokens_antes} → {tokens_despues} tokens"
        )

        return {
            "comprimida": True,
            "tokens_antes": tokens_antes,
            "tokens_despues": tokens_despues,
            "resumen": resumen,
        }


def _resumir_automatico(mensajes: list[dict]) -> str:
    """
    Resumen automático sin LLM: extrae los primeros y últimos mensajes
    + todos los mensajes de rol 'tool' o 'system' (decisiones importantes).
    
    Para un resumen LLM-powered, pasá tu propia fn_resumir a comprimir_sesion().
    """
    partes = []

    # Contexto inicial (primeros 3 mensajes)
    partes.append("=== CONTEXTO INICIAL ===")
    for m in mensajes[:3]:
        try:
            contenido = json.loads(m["contenido_json"])
        except Exception:
            contenido = m["contenido_json"]
        partes.append(f"[{m['rol']}]: {str(contenido)[:300]}")

    # Decisiones y herramientas (mensajes con metadatos)
    partes.append("\n=== DECISIONES Y ARTEFACTOS ===")
    for m in mensajes:
        if m["rol"] in ("tool", "system"):
            try:
                contenido = json.loads(m["contenido_json"])
            except Exception:
                contenido = m["contenido_json"]
            partes.append(f"[{m['rol']}]: {str(contenido)[:400]}")

    # Cierre (últimos 5 mensajes)
    partes.append("\n=== ESTADO FINAL ===")
    for m in mensajes[-5:]:
        try:
            contenido = json.loads(m["contenido_json"])
        except Exception:
            contenido = m["contenido_json"]
        partes.append(f"[{m['rol']}]: {str(contenido)[:300]}")

    return "\n".join(partes)


def necesita_compresion(session_id: str, limite_tokens: int = LIMITE_TOKENS_DEFAULT) -> bool:
    """Retorna True si la sesión supera el límite de tokens."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT tokens_totales FROM sesiones WHERE session_id = ?", (session_id,)
        ).fetchone()
    return row is not None and row["tokens_totales"] >= limite_tokens
