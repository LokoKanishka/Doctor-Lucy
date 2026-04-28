#!/usr/bin/env python3
"""
LUCY DAEMON v1 — Operativo OpenClaw
Núcleo autónomo de Lucy Cunningham. Escucha Telegram y ejecuta el bucle de razonamiento ReAct local.
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
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuración Core
WORKSPACE = os.environ.get("WORKSPACE_ROOT", "/home/lucy-ubuntu/Escritorio/doctor de lucy")

def load_env(filepath):
    if not os.path.exists(filepath): return
    with open(filepath) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                try:
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val
                except: pass

load_env(f"{WORKSPACE}/.env")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DIEGO_ID = int(os.environ.get("DIEGO_TELEGRAM_ID", 5154360597))
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:14b")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
SOUL_FILE = f"{WORKSPACE}/SOUL.md"
HEARTBEAT_FILE = f"{WORKSPACE}/HEARTBEAT.md"
LOG_FILE = f"{WORKSPACE}/n8n_data/lucy_daemon.log"
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

async def get_ollama_response(messages, tools=None):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }
    if tools:
        payload["tools"] = tools

    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            return await resp.json()

async def agent_loop(user_input, chat_id):
    global conversation_history
    
    # Cargar SOUL
    with open(SOUL_FILE, "r") as f:
        soul_content = f.read()

    system_prompt = f"{soul_content}\n\nContexto actual: Estás operando en modo DAEMON fuera del IDE. Tenés acceso a herramientas del sistema."
    
    # Preparar mensajes
    messages = [{"role": "system", "content": system_prompt}]
    for h in conversation_history:
        messages.append(h)
    messages.append({"role": "user", "content": user_input})

    # Levantar MCP Básico (Sequential Thinking)
    server_params = StdioServerParameters(command="node", args=[f"{WORKSPACE}/.agents/mcps/servers/src/sequentialthinking/dist/index.js"])
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as mcp_session:
                await mcp_session.initialize()
                
                # Exponer herramientas MCP a Ollama (Fase 1: Pensamiento)
                tools_response = await mcp_session.list_tools()
                ollama_tools = [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.inputSchema}} for t in tools_response.tools]

                for loop in range(8): # Bucle ReAct
                    resp_data = await get_ollama_response(messages, tools=ollama_tools)
                    msg = resp_data.get("message", {})
                    
                    if not msg.get("tool_calls"):
                        final_text = msg.get("content", "").strip()
                        # Limpiar <think> si el modelo lo incluyó
                        import re
                        final_text = re.sub(r"<think>.*?</think>", "", final_text, flags=re.DOTALL).strip()
                        
                        conversation_history.append({"role": "user", "content": user_input})
                        conversation_history.append({"role": "assistant", "content": final_text})
                        if len(conversation_history) > MAX_HISTORY:
                            conversation_history = conversation_history[-MAX_HISTORY:]
                            
                        telegram_send(chat_id, final_text)
                        return

                    messages.append(msg)
                    for tc in msg.get("tool_calls", []):
                        t_name = tc["function"]["name"]
                        t_args = tc["function"]["arguments"]
                        
                        log(f"Ejecutando tool: {t_name}")
                        if t_name == "sequentialthinking":
                            res = await mcp_session.call_tool(t_name, arguments=t_args)
                            messages.append({"role": "tool", "name": t_name, "content": res.content[0].text})
                            # Opcional: Mandar "pensamiento" a Diego si es relevante
                            # telegram_send(chat_id, f"🧠 {t_args.get('thought')}")
                        else:
                            messages.append({"role": "tool", "name": t_name, "content": "Error: Herramienta no conectada en modo daemon todavía."})

    except Exception as e:
        log(f"Error en Agent Loop: {e}")
        telegram_send(chat_id, f"🩺 Diego, tuve un error en mi núcleo de pensamiento: {e}")

async def run_heartbeat():
    """Ejecuta las tareas definidas en HEARTBEAT.md"""
    log("💓 Iniciando latido proactivo...")
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

    # Tarea 2: Memoria
    if "Memoria" in tasks:
        try:
            res = subprocess.run(['free'], capture_output=True, text=True, timeout=10)
            lines = res.stdout.splitlines()
            mem = lines[1].split()
            used_pct = (int(mem[2]) / int(mem[1])) * 100
            if used_pct > 90:
                report.append(f"🔥 ¡Alerta de Memoria! Uso al {used_pct:.1f}%")
        except: pass

    if report:
        summary = "🩺 Reporte Proactivo:\n\n" + "\n".join(report)
        telegram_send(DIEGO_ID, summary)
        log("Reporte proactivo enviado a Telegram.")
    else:
        log("Latido saludable. No se requiere reporte.")

async def main():
    log("LUCY DAEMON v1 Iniciado.")
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

            # 2. Latido Proactivo (Heartbeat)
            if time.time() - last_heartbeat > 3600: # Cada 60 min para no saturar Ollama
                await run_heartbeat()
                last_heartbeat = time.time()

            await asyncio.sleep(2)
        except Exception as e:
            log(f"Error en Loop Principal: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
