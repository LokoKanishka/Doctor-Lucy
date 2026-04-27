import sys
import asyncio
import time
import os
import json

sys.path.append("/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts")
import lucy_daemon_v2_cloud

async def run_stress_test():
    report_file = "STRESS_TEST_REPORT.md"
    lucy_daemon_v2_cloud.log("🚀 Iniciando Suite de Estrés v2 (8 Motores de Respaldo)")
    
    tests = [
        "Busca noticias sobre el clima en Buenos Aires hoy.",
        "Busca el precio del Bitcoin y guardalo en 'bitcoin.txt' en el Escritorio.",
        "Listame los archivos de la carpeta Documentos.",
        "Escribí un poema sobre la inteligencia artificial y envíalo por chat.",
        "Busca quién ganó el último mundial de fútbol y hacé un resumen corto."
    ]

    results = []
    
    with open(report_file, "w") as f:
        f.write("# 🩺 Reporte de Prueba de Estrés - Doctora Lucy\n\n")
        f.write(f"**Fecha**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Motores configurados**: 8 (Gemini + OpenAI + Codex)\n\n")
        f.write("| ID | Tarea | Resultado | Tiempo (s) | Notas |\n")
        f.write("|---|---|---|---|---|\n")

    for i, task in enumerate(tests):
        start_time = time.time()
        lucy_daemon_v2_cloud.log(f"--- Ejecutando Tarea {i+1}: {task} ---")
        
        try:
            # Capturamos la respuesta del loop
            # Nota: agent_loop de lucy_daemon_v2_cloud no retorna el texto, 
            # así que vamos a modificarlo o usar el bridge directamente para el reporte.
            response = lucy_daemon_v2_cloud.delegate_mission(task)
            duration = round(time.time() - start_time, 2)
            
            status = "✅ Éxito" if response and "error" not in response.lower() else "❌ Fallo/Fallback"
            results.append({"id": i+1, "task": task, "status": status, "duration": duration, "notes": response[:50] + "..."})
            
            with open(report_file, "a") as f:
                f.write(f"| {i+1} | {task} | {status} | {duration} | {status} |\n")
            
            # También lo mandamos por el loop real para que Diego lo vea en Telegram
            await lucy_daemon_v2_cloud.agent_loop(task, lucy_daemon_v2_cloud.DIEGO_ID)
            
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            results.append({"id": i+1, "task": task, "status": "❌ Error", "duration": duration, "notes": str(e)})
            with open(report_file, "a") as f:
                f.write(f"| {i+1} | {task} | ❌ Error | {duration} | {str(e)[:30]} |\n")

        await asyncio.sleep(1)

    lucy_daemon_v2_cloud.log("✅ Suite de Estrés v2 finalizada.")
    
    # Reporte final por voz
    voice_msg = f"Diego, finalicé la prueba de estrés. Procesé {len(tests)} tareas. Mirá el archivo STRESS_TEST_REPORT.md para ver el detalle de cada motor."
    with open("/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/voice_payload.txt", "w") as f:
        f.write(voice_msg)
    os.system("bash /home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_announcer.sh")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
