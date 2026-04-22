#!/usr/bin/env python3
"""
LUCY DAEMON v2 — Cloud Brain (Cero VRAM)
Núcleo autónomo de Lucy Cunningham. Escucha Telegram y delega el razonamiento a Gemini API,
emulando 100% el comportamiento ligero de OpenClaw. VRAM consumida: 0 MB.
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
import subprocess
import urllib.request
import urllib.parse

def load_env(filepath):
    if not os.path.exists(filepath): return
    with open(filepath) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

load_env("/home/lucy-ubuntu/Escritorio/doctor de lucy/.env")

# Configuración Core
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DIEGO_ID = int(os.environ.get("DIEGO_TELEGRAM_ID", 5154360597))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WORKSPACE = "/home/lucy-ubuntu/Escritorio/doctor de lucy"
SOUL_FILE = f"{WORKSPACE}/SOUL.md"
HEARTBEAT_FILE = f"{WORKSPACE}/HEARTBEAT.md"
LOG_FILE = f"{WORKSPACE}/n8n_data/lucy_daemon_v2.log"
OFFSET_FILE = f"{WORKSPACE}/n8n_data/telegram_offset.txt"

# Historial de conversación
conversation_history = []
MAX_HISTORY = 12

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def telegram_send(chat_id, text):
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        log(f"Error enviando Telegram: {e}")

async def get_gemini_response(system_prompt, messages):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    contents = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
        
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": contents
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            try:
                text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                return text_response.strip()
            except Exception as e:
                log(f"Error parseando respuesta de Gemini: {data}")
                return "Error comunicando con el cerebro Cloud."

async def agent_loop(user_input, chat_id):
    global conversation_history
    
    if not GEMINI_API_KEY:
        telegram_send(chat_id, "⚠️ No tengo configurada una GEMINI_API_KEY en el environment.")
        return

    # Cargar SOUL
    soul_content = ""
    if os.path.exists(SOUL_FILE):
        with open(SOUL_FILE, "r") as f:
            soul_content = f.read()

    system_prompt = f"{soul_content}\n\nContexto actual: Estás operando en modo DAEMON fuera del IDE. Tenés acceso a internet usando tu cerebro Cloud. Tu VRAM consumida es CERO."
    
    # Añadir input del usuario al historial temporal
    temp_hist = conversation_history.copy()
    temp_hist.append({"role": "user", "content": user_input})

    try:
        final_text = await get_gemini_response(system_prompt, temp_hist)
        
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": final_text})
        if len(conversation_history) > MAX_HISTORY:
            conversation_history = conversation_history[-MAX_HISTORY:]
            
        telegram_send(chat_id, final_text)

    except Exception as e:
        log(f"Error en Agent Loop (Cloud): {e}")
        telegram_send(chat_id, f"🩺 Diego, tuve un error en mi conexión a la nube: {e}")

async def run_heartbeat():
    """Ejecuta las tareas definidas en HEARTBEAT.md"""
    log("💓 Iniciando latido proactivo (Cloud)...")
    if not os.path.exists(HEARTBEAT_FILE):
        return
        
    with open(HEARTBEAT_FILE, "r") as f:
        tasks = f.read()
    
    report = []
    
    # Tarea 1: Salud Docker
    if "Salud Docker" in tasks:
        try:
            res = subprocess.run(['docker', 'ps', '--filter', 'name=doctor_lucy_n8n', '--format', '{{.Status}}'], 
                                   capture_output=True, text=True, timeout=10)
            status = res.stdout.strip()
            if not status or "Up" not in status:
                report.append("⚠️ ¡Alerta! El contenedor doctor_lucy_n8n no parece estar corriendo.")
        except Exception as e:
            report.append(f"❌ Error monitoreando Docker: {e}")

    # Tarea 2: Memoria RAM
    if "Memoria" in tasks:
        try:
            res = subprocess.run(['free'], capture_output=True, text=True, timeout=10)
            lines = res.stdout.splitlines()
            mem = lines[1].split()
            used_pct = (int(mem[2]) / int(mem[1])) * 100
            if used_pct > 90:
                report.append(f"🔥 ¡Alerta de RAM (PC)! Uso al {used_pct:.1f}%")
        except: pass

    if report:
        summary = "🩺 Reporte Proactivo (Modo Cloud Daemon):\n\n" + "\n".join(report)
        telegram_send(DIEGO_ID, summary)
        log("Reporte proactivo enviado a Telegram.")

async def main():
    log("LUCY DAEMON v2 (Cloud) Iniciado.")
    telegram_send(DIEGO_ID, "☁️ *Lucy Daemon v2 (Cloud Mode)* Iniciado.\nMi consumo de VRAM es actualmente de: 0 MB.\nTodo el cerebro ha sido delegado a la API externa (igual que OpenClaw).")
    
    offset = 0
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE, "r") as f:
                offset = int(f.read().strip())
        except: pass

    last_heartbeat = time.time()

    while True:
        try:
            # 1. Escuchar Telegram
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=10"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        updates_data = await resp.json()
                        for update in updates_data.get("result", []):
                            offset = update["update_id"] + 1
                            with open(OFFSET_FILE, "w") as f: f.write(str(offset))
                            
                            msg = update.get("message", {})
                            if msg.get("from", {}).get("id") == DIEGO_ID:
                                text = msg.get("text", "")
                                if text:
                                    log(f"Mensaje de Diego: {text}")
                                    await agent_loop(text, DIEGO_ID)

            # 2. Latido Proactivo (Heartbeat) - Cada hora
            if time.time() - last_heartbeat > 3600: 
                await run_heartbeat()
                last_heartbeat = time.time()

            await asyncio.sleep(2)
        except asyncio.TimeoutError:
            pass # Timeout normal del long polling
        except Exception as e:
            log(f"Error en Loop Principal: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        log("ERROR CRÍTICO: No se encontró GEMINI_API_KEY en /.env")
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Lucy Daemon v2 detenido manualmente.")
