import sys
import asyncio

sys.path.append("/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts")
import lucy_daemon_v2_cloud

async def run_tests():
    lucy_daemon_v2_cloud.log("🚀 Iniciando suite de pruebas de estrés (Simulando 5 mensajes de Diego)")
    
    tests = [
        "Prueba de estrés 1 (Búsqueda): Buscá en internet las últimas noticias sobre la misión Artemis de la NASA.",
        "Prueba de estrés 2 (Búsqueda y Archivo): Buscá en internet información sobre la misión a Marte, hacé un resumen y dejalo guardado en un archivo en mi escritorio llamado 'mision_marte.txt'.",
        "Prueba de estrés 3 (Lectura de Sistema): Decime exactamente qué carpetas y archivos hay en mi Escritorio en este momento.",
        "Prueba de estrés 4 (Lectura de Sistema): Decime qué archivos de audio (ogg, mp3, wav, etc.) hay en mi carpeta Descargas en este momento.",
        "Prueba de estrés 5 (Generación y Envío): Escribí un cuento corto de ciencia ficción, guardalo en un archivo de texto y envíamelo por este chat."
    ]

    for i, test in enumerate(tests):
        lucy_daemon_v2_cloud.log(f"--- Ejecutando Prueba {i+1} ---")
        await lucy_daemon_v2_cloud.agent_loop(test, lucy_daemon_v2_cloud.DIEGO_ID)
        await asyncio.sleep(2) # Pequeña pausa entre mensajes

if __name__ == "__main__":
    asyncio.run(run_tests())
