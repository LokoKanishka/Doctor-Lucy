#!/usr/bin/env python3
"""
LUCY DAEMON v4.0 — Simplificación Total
- Motor Primario: OpenClaw/Codex vía gateway local.
- Telegram nativo de OpenClaw es el canal recomendado.
- Este daemon queda como compatibilidad y evita arrancar si competiría por el
  mismo bot de Telegram.
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
import urllib.parse
import urllib.request
import base64
import re
import requests

# IMPORTACIÓN: Puente con OpenClaw
sys.path.append("/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts")
try:
    from lucy_openclaw_bridge import delegate_mission
except ImportError:
    def delegate_mission(p): return "Error: Puente no encontrado."

def load_env(filepath):
    if not os.path.exists(filepath): return
    with open(filepath) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                try:
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val
                except: pass

load_env("/home/lucy-ubuntu/Escritorio/doctor de lucy/.env")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DIEGO_ID = int(os.environ.get("DIEGO_TELEGRAM_ID", 5154360597))
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") # Una sola llave para transcripción

WORKSPACE = "/home/lucy-ubuntu/Escritorio/doctor de lucy"
LOG_FILE = f"{WORKSPACE}/n8n_data/lucy_daemon_v2.log"
OFFSET_FILE = f"{WORKSPACE}/n8n_data/telegram_offset.txt"
PID_FILE = f"{WORKSPACE}/n8n_data/daemon.pid"
OPENCLAW_CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    with open(LOG_FILE, "a") as f: f.write(line + "\n")
    print(line)

def telegram_send(chat_id, text):
    if len(text) > 4000:
        for i in range(0, len(text), 4000): telegram_send(chat_id, text[i:i+4000])
        return
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)
    try: urllib.request.urlopen(req, timeout=15)
    except Exception as e: log(f"⚠️ Error Telegram: {e}")

async def transcribe_audio(audio_bytes):
    log("🎙️ Transcribiendo audio vía Gemini (Motor Auxiliar)...")
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{
            "parts": [
                {"text": "Transcribí exactamente lo que dice este audio. Solo devolvé el texto."},
                {"inline_data": {"mime_type": "audio/ogg", "data": audio_b64}}
            ]
        }]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
    except: pass
    return None

async def agent_loop(user_input, chat_id):
    log(f"📩 Diego: {user_input}")
    log("Delegando a OpenClaw (Motor Primario: Codex/gateway)...")
    
    # Intento directo vía OpenClaw
    response = delegate_mission(user_input)
    
    if not response or "error" in response.lower():
        log(f"⚠️ OpenClaw falló: {response}")
        response = "Diego, hubo un error de comunicación con OpenClaw. Intentá de nuevo en unos segundos."

    log(f"📤 Lucy: {response[:50]}...")
    telegram_send(chat_id, response)

def openclaw_native_telegram_enabled():
    if os.getenv("LUCY_DAEMON_FORCE_TELEGRAM") == "1":
        return False
    try:
        with open(OPENCLAW_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return bool(config.get("channels", {}).get("telegram", {}).get("enabled"))
    except Exception:
        return False

async def main():
    if openclaw_native_telegram_enabled():
        log("OpenClaw ya maneja Telegram nativamente. No arranco lucy_daemon_v2_cloud para evitar doble polling del mismo bot.")
        log("Si necesitás forzar este daemon legacy: LUCY_DAEMON_FORCE_TELEGRAM=1 python3 scripts/lucy_daemon_v2_cloud.py")
        return

    log(f"LUCY DAEMON v4.0 (Estabilidad Total) Iniciado. PID {os.getpid()}")
    telegram_send(DIEGO_ID, "Lucy Daemon v4.0 iniciado.\nMotor Primario: OpenClaw/Codex\nResiliencia: Activada")
    
    offset = 0
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE, "r") as f: offset = int(f.read().strip())
        except: pass

    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=10"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=20) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for update in data.get("result", []):
                            offset = update["update_id"] + 1
                            with open(OFFSET_FILE, "w") as f: f.write(str(offset))
                            msg = update.get("message", {})
                            if msg.get("from", {}).get("id") == DIEGO_ID:
                                text = msg.get("text")
                                if msg.get("voice"):
                                    log("🎤 Audio recibido.")
                                    file_id = msg["voice"]["file_id"]
                                    # Descarga simplificada
                                    f_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
                                    async with session.get(f_url) as f_resp:
                                        f_data = await f_resp.json()
                                        d_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{f_data['result']['file_path']}"
                                        async with session.get(d_url) as d_resp:
                                            text = await transcribe_audio(await d_resp.read())
                                
                                if text: await agent_loop(text, DIEGO_ID)
            await asyncio.sleep(1)
        except: await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
