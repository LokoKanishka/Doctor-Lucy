"""
demo.py — Prueba completa del sistema de memoria persistente.
Ejecutar: python3 memoria/demo.py
"""
import sys
import os
import pathlib

# Añadir la ruta padre al path para imports relativos
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from memoria import iniciar_sesion, auto_save_back, consultar_historial, cerrar_sesion, comprimir_sesion

SEP = "=" * 60

def test_crear_sesion():
    print(f"\n{SEP}")
    print("TEST 1: Crear sesión nueva")
    ctx = iniciar_sesion()
    assert ctx["nueva"] == True
    assert ctx["mensajes"] == []
    print(f"  ✅ session_id: {ctx['session_id']}")
    return ctx["session_id"]

def test_guardar_mensajes(session_id):
    print(f"\n{SEP}")
    print("TEST 2: Guardar mensajes (auto_save_back)")
    eventos = [
        {"rol": "user", "contenido": "Hola, necesito verificar la frontera de voz Lucy/Fusion."},
        {"rol": "assistant", "contenido": "Doctora Lucy usa 7854; Fusion Reader v2 usa 7853 con owner=fusion_reader_v2; 7852 es historico y 7851 legacy."},
        {"rol": "tool", "contenido": "scripts/verify_voice_port_isolation.sh → frontera de voz OK"},
        {"rol": "user", "contenido": "También necesito revisar el esquema de la base de datos SQLite."},
        {"rol": "assistant", "contenido": "El esquema tiene tablas: sesiones, mensajes, metadatos, cache_global."},
    ]
    tokens = auto_save_back(session_id, eventos, metadatos={
        "proyecto": "Doctor Lucy",
        "servicio_activo": "AllTalk TTS Lucy puerto 7854",
        "ultima_accion": "Demo de memoria SQLite",
    })
    print(f"  ✅ {len(eventos)} mensajes guardados. Tokens estimados: {tokens}")

def test_recuperar_sesion(session_id):
    print(f"\n{SEP}")
    print("TEST 3: Recuperar sesión existente")
    ctx = iniciar_sesion(session_id)
    assert ctx["nueva"] == False
    assert len(ctx["mensajes"]) == 5
    print(f"  ✅ Sesión recuperada con {len(ctx['mensajes'])} mensajes")
    print(f"  ✅ Metadatos: {ctx['metadatos']}")

def test_busqueda_keywords(session_id):
    print(f"\n{SEP}")
    print("TEST 4: consultar_historial (búsqueda por keywords)")
    resultados = consultar_historial("AllTalk frontera", session_id=session_id)
    assert len(resultados) > 0
    print(f"  ✅ Encontrados {len(resultados)} fragmentos para 'AllTalk frontera'")
    for r in resultados:
        print(f"    [{r['rol']}] {r['fragmento'][:80]}... (match: '{r['keyword_match']}')")

def test_busqueda_global():
    print(f"\n{SEP}")
    print("TEST 5: consultar_historial (búsqueda global, sin session_id)")
    resultados = consultar_historial("SQLite esquema")
    print(f"  ✅ Encontrados {len(resultados)} fragmentos para 'SQLite esquema' en todas las sesiones")

def test_comprimir(session_id):
    print(f"\n{SEP}")
    print("TEST 6: comprimir_sesion (con limite artificial bajo)")
    resultado = comprimir_sesion(session_id, limite_tokens=10)  # límite muy bajo para forzar compresión
    if resultado["comprimida"]:
        print(f"  ✅ Comprimida: {resultado['tokens_antes']} → {resultado['tokens_despues']} tokens")
        print(f"  ✅ Resumen ({len(resultado['resumen'])} chars):")
        print(f"    {resultado['resumen'][:200]}...")
    else:
        print(f"  ℹ️  No se necesitó compresión (tokens: {resultado['tokens_antes']} < {10})")

def test_cerrar(session_id):
    print(f"\n{SEP}")
    print("TEST 7: cerrar_sesion")
    cerrar_sesion(session_id)
    print(f"  ✅ Sesión cerrada correctamente")

if __name__ == "__main__":
    print(f"\n{'🧠 DEMO — Sistema de Memoria Persistente SQLite':^60}")
    print(SEP)

    try:
        sid = test_crear_sesion()
        test_guardar_mensajes(sid)
        test_recuperar_sesion(sid)
        test_busqueda_keywords(sid)
        test_busqueda_global()
        test_comprimir(sid)
        test_cerrar(sid)

        print(f"\n{SEP}")
        print("🎉 TODOS LOS TESTS PASARON")
        print(f"   Base de datos: {pathlib.Path(__file__).parent / 'agente_memoria.db'}")

    except Exception as e:
        print(f"\n❌ ERROR en el test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
