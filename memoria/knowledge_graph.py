"""
knowledge_graph.py — Knowledge Graph para memoria a largo plazo de Doctora Lucy.

Estructura:
  - entidades:      Nodos del grafo (personas, conceptos, herramientas, preferencias...)
  - relaciones:     Aristas entre entidades (tipo + metadata)
  - observaciones:  Notas textuales asociadas a una entidad

API principal:
  - crear_entidad(nombre, tipo, metadata)
  - crear_relacion(origen, destino, tipo_relacion, metadata)
  - agregar_observacion(entidad_nombre, contenido)
  - buscar_entidades(query, tipo)
  - obtener_grafo_entidad(nombre, profundidad)
  - listar_entidades(tipo, limite)
  - eliminar_entidad(nombre)
"""
import json
import datetime
from typing import Optional

from .db import get_connection


# ─────────────────────────────────────────────
# CRUD de Entidades
# ─────────────────────────────────────────────

def crear_entidad(nombre: str, tipo: str, metadata: Optional[dict] = None) -> dict:
    """
    Crea o actualiza una entidad en el Knowledge Graph.
    
    Tipos sugeridos: persona, preferencia, concepto, herramienta, proyecto,
                     servicio, modelo_ia, hardware, configuracion, decisión.
    
    Si la entidad ya existe (por nombre), actualiza su tipo y metadata.
    """
    meta_json = json.dumps(metadata or {}, ensure_ascii=False)
    ahora = datetime.datetime.now().isoformat()

    with get_connection() as conn:
        existente = conn.execute(
            "SELECT id FROM kg_entidades WHERE nombre = ?", (nombre,)
        ).fetchone()

        if existente:
            conn.execute(
                "UPDATE kg_entidades SET tipo = ?, metadata = ?, actualizado_en = ? "
                "WHERE nombre = ?",
                (tipo, meta_json, ahora, nombre)
            )
            return {"accion": "actualizada", "nombre": nombre, "tipo": tipo}
        else:
            conn.execute(
                "INSERT INTO kg_entidades (nombre, tipo, metadata, creado_en, actualizado_en) "
                "VALUES (?, ?, ?, ?, ?)",
                (nombre, tipo, meta_json, ahora, ahora)
            )
            return {"accion": "creada", "nombre": nombre, "tipo": tipo}


def crear_relacion(
    origen: str, destino: str, tipo_relacion: str, metadata: Optional[dict] = None
) -> dict:
    """
    Crea una relación dirigida entre dos entidades.
    
    Ejemplos de tipo_relacion:
      - "usa", "prefiere", "contiene", "depende_de", "ejecuta_en",
        "configurado_como", "creado_por", "conectado_a"
    
    Las entidades se crean automáticamente si no existen (tipo='auto').
    """
    meta_json = json.dumps(metadata or {}, ensure_ascii=False)
    ahora = datetime.datetime.now().isoformat()

    with get_connection() as conn:
        # Auto-crear entidades si no existen
        for nombre_ent in (origen, destino):
            existe = conn.execute(
                "SELECT 1 FROM kg_entidades WHERE nombre = ?", (nombre_ent,)
            ).fetchone()
            if not existe:
                conn.execute(
                    "INSERT INTO kg_entidades (nombre, tipo, metadata, creado_en, actualizado_en) "
                    "VALUES (?, 'auto', '{}', ?, ?)",
                    (nombre_ent, ahora, ahora)
                )

        # Verificar si la relación ya existe
        existente = conn.execute(
            "SELECT id FROM kg_relaciones WHERE origen = ? AND destino = ? AND tipo = ?",
            (origen, destino, tipo_relacion)
        ).fetchone()

        if existente:
            conn.execute(
                "UPDATE kg_relaciones SET metadata = ?, actualizado_en = ? WHERE id = ?",
                (meta_json, ahora, existente["id"])
            )
            return {"accion": "actualizada", "origen": origen, "destino": destino, "tipo": tipo_relacion}
        else:
            conn.execute(
                "INSERT INTO kg_relaciones (origen, destino, tipo, metadata, creado_en, actualizado_en) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (origen, destino, tipo_relacion, meta_json, ahora, ahora)
            )
            return {"accion": "creada", "origen": origen, "destino": destino, "tipo": tipo_relacion}


def agregar_observacion(entidad_nombre: str, contenido: str) -> dict:
    """
    Agrega una observación/nota textual a una entidad existente.
    
    Ejemplos:
      - agregar_observacion("Diego", "Prefiere trabajar de noche")
      - agregar_observacion("RTX 5090", "32GB VRAM, driver 570.211")
    """
    ahora = datetime.datetime.now().isoformat()

    with get_connection() as conn:
        # Verificar que la entidad existe
        existe = conn.execute(
            "SELECT 1 FROM kg_entidades WHERE nombre = ?", (entidad_nombre,)
        ).fetchone()
        if not existe:
            # Auto-crear la entidad
            conn.execute(
                "INSERT INTO kg_entidades (nombre, tipo, metadata, creado_en, actualizado_en) "
                "VALUES (?, 'auto', '{}', ?, ?)",
                (entidad_nombre, ahora, ahora)
            )

        conn.execute(
            "INSERT INTO kg_observaciones (entidad_nombre, contenido, creado_en) "
            "VALUES (?, ?, ?)",
            (entidad_nombre, contenido, ahora)
        )
        return {"entidad": entidad_nombre, "observacion": contenido[:100] + "..."}


# ─────────────────────────────────────────────
# Consultas
# ─────────────────────────────────────────────

def buscar_entidades(query: str, tipo: Optional[str] = None, limite: int = 20) -> list[dict]:
    """
    Busca entidades por nombre (LIKE) y opcionalmente filtra por tipo.
    También busca en observaciones asociadas.
    """
    patron = f"%{query}%"

    with get_connection() as conn:
        if tipo:
            entidades = conn.execute(
                "SELECT nombre, tipo, metadata, creado_en FROM kg_entidades "
                "WHERE (nombre LIKE ? OR tipo LIKE ?) AND tipo = ? "
                "ORDER BY actualizado_en DESC LIMIT ?",
                (patron, patron, tipo, limite)
            ).fetchall()
        else:
            entidades = conn.execute(
                "SELECT nombre, tipo, metadata, creado_en FROM kg_entidades "
                "WHERE nombre LIKE ? OR tipo LIKE ? "
                "ORDER BY actualizado_en DESC LIMIT ?",
                (patron, patron, limite)
            ).fetchall()

        # También buscar en observaciones
        obs_matches = conn.execute(
            "SELECT DISTINCT entidad_nombre FROM kg_observaciones "
            "WHERE contenido LIKE ? LIMIT ?",
            (patron, limite)
        ).fetchall()

        # Combinar resultados
        nombres_encontrados = {e["nombre"] for e in entidades}
        for obs in obs_matches:
            if obs["entidad_nombre"] not in nombres_encontrados:
                ent = conn.execute(
                    "SELECT nombre, tipo, metadata, creado_en FROM kg_entidades "
                    "WHERE nombre = ?", (obs["entidad_nombre"],)
                ).fetchone()
                if ent:
                    entidades.append(ent)

    return [
        {
            "nombre": e["nombre"],
            "tipo": e["tipo"],
            "metadata": json.loads(e["metadata"]) if e["metadata"] else {},
            "creado_en": e["creado_en"],
        }
        for e in entidades
    ][:limite]


def obtener_grafo_entidad(nombre: str, profundidad: int = 1) -> dict:
    """
    Obtiene una entidad y todas sus relaciones + observaciones.
    Con profundidad > 1, también trae las entidades conectadas (BFS).
    """
    with get_connection() as conn:
        entidad = conn.execute(
            "SELECT * FROM kg_entidades WHERE nombre = ?", (nombre,)
        ).fetchone()

        if not entidad:
            return {"error": f"Entidad '{nombre}' no encontrada"}

        # Observaciones
        observaciones = conn.execute(
            "SELECT contenido, creado_en FROM kg_observaciones "
            "WHERE entidad_nombre = ? ORDER BY creado_en DESC",
            (nombre,)
        ).fetchall()

        # Relaciones salientes
        rel_salientes = conn.execute(
            "SELECT destino, tipo, metadata FROM kg_relaciones WHERE origen = ?",
            (nombre,)
        ).fetchall()

        # Relaciones entrantes
        rel_entrantes = conn.execute(
            "SELECT origen, tipo, metadata FROM kg_relaciones WHERE destino = ?",
            (nombre,)
        ).fetchall()

        resultado = {
            "entidad": {
                "nombre": entidad["nombre"],
                "tipo": entidad["tipo"],
                "metadata": json.loads(entidad["metadata"]) if entidad["metadata"] else {},
            },
            "observaciones": [
                {"contenido": o["contenido"], "fecha": o["creado_en"]}
                for o in observaciones
            ],
            "relaciones_salientes": [
                {"destino": r["destino"], "tipo": r["tipo"],
                 "metadata": json.loads(r["metadata"]) if r["metadata"] else {}}
                for r in rel_salientes
            ],
            "relaciones_entrantes": [
                {"origen": r["origen"], "tipo": r["tipo"],
                 "metadata": json.loads(r["metadata"]) if r["metadata"] else {}}
                for r in rel_entrantes
            ],
        }

        # BFS para profundidad > 1
        if profundidad > 1:
            vecinos = {}
            nombres_vecinos = set()
            for r in rel_salientes:
                nombres_vecinos.add(r["destino"])
            for r in rel_entrantes:
                nombres_vecinos.add(r["origen"])

            for vecino_nombre in nombres_vecinos:
                if vecino_nombre != nombre:
                    vecinos[vecino_nombre] = obtener_grafo_entidad(
                        vecino_nombre, profundidad - 1
                    )
            resultado["vecinos"] = vecinos

        return resultado


def listar_entidades(tipo: Optional[str] = None, limite: int = 50) -> list[dict]:
    """Lista todas las entidades, opcionalmente filtradas por tipo."""
    with get_connection() as conn:
        if tipo:
            rows = conn.execute(
                "SELECT nombre, tipo, metadata, creado_en, actualizado_en "
                "FROM kg_entidades WHERE tipo = ? ORDER BY actualizado_en DESC LIMIT ?",
                (tipo, limite)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT nombre, tipo, metadata, creado_en, actualizado_en "
                "FROM kg_entidades ORDER BY actualizado_en DESC LIMIT ?",
                (limite,)
            ).fetchall()

    return [
        {
            "nombre": r["nombre"],
            "tipo": r["tipo"],
            "metadata": json.loads(r["metadata"]) if r["metadata"] else {},
            "creado_en": r["creado_en"],
        }
        for r in rows
    ]


def eliminar_entidad(nombre: str) -> dict:
    """Elimina una entidad y todas sus relaciones y observaciones."""
    with get_connection() as conn:
        conn.execute("DELETE FROM kg_observaciones WHERE entidad_nombre = ?", (nombre,))
        conn.execute("DELETE FROM kg_relaciones WHERE origen = ? OR destino = ?", (nombre, nombre))
        conn.execute("DELETE FROM kg_entidades WHERE nombre = ?", (nombre,))
    return {"eliminada": nombre}


def exportar_grafo_completo() -> dict:
    """Exporta el grafo completo para backup o visualización."""
    with get_connection() as conn:
        entidades = conn.execute("SELECT * FROM kg_entidades").fetchall()
        relaciones = conn.execute("SELECT * FROM kg_relaciones").fetchall()
        observaciones = conn.execute("SELECT * FROM kg_observaciones").fetchall()

    return {
        "entidades": [
            {"nombre": e["nombre"], "tipo": e["tipo"],
             "metadata": json.loads(e["metadata"]) if e["metadata"] else {}}
            for e in entidades
        ],
        "relaciones": [
            {"origen": r["origen"], "destino": r["destino"], "tipo": r["tipo"],
             "metadata": json.loads(r["metadata"]) if r["metadata"] else {}}
            for r in relaciones
        ],
        "observaciones": [
            {"entidad": o["entidad_nombre"], "contenido": o["contenido"],
             "fecha": o["creado_en"]}
            for o in observaciones
        ],
        "stats": {
            "total_entidades": len(entidades),
            "total_relaciones": len(relaciones),
            "total_observaciones": len(observaciones),
        }
    }
