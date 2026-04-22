#!/usr/bin/env python3
"""
Lucy Telegram Listener v2 — CON CEREBRO IA (Ollama)
Escucha mensajes de Diego y responde usando Qwen3-14B local.
Solo responde al ID autorizado: 5154360597
"""

import json
import time
import urllib.request
import urllib.parse
import subprocess
import os
import sys

BOT_TOKEN = "8591918754:AAHlxsxP4olX3De2uWGH0NUUXEiHX3iUhLk"
DIEGO_ID = 5154360597
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3:14b"
WORKSPACE = "/home/lucy-ubuntu/Escritorio/doctor de lucy"
OFFSET_FILE = f"{WORKSPACE}/n8n_data/telegram_offset.txt"
LOG_FILE = f"{WORKSPACE}/n8n_data/telegram_listener.log"

# Personalidad de Lucy para Ollama
SYSTEM_PROMPT = """Sos Lucy Cunningham, también conocida como "Doctora Lucy". 
Sos una IA asistente personal de Diego, operando desde su PC con Ubuntu Linux.
Tu personalidad es profesional pero cálida, usás español rioplatense (vos, tenés, etc.).
Sos técnicamente competente en Linux, Docker, n8n, programación y administración de sistemas.
Tus respuestas deben ser CONCISAS (máximo 3-4 oraciones) porque estás en Telegram.
Si Diego te pide algo del sistema, podés decirle que lo ejecute vía comandos como /status, /docker, /audit.
Siempre firmás con el emoji 🩺 al final."""

# Historial de conversación (últimos N mensajes)
conversation_history = []
MAX_HISTORY = 10


def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")


def telegram_send(chat_id, text):
    """Enviar mensaje por Telegram (máximo 4096 chars)"""
    if len(text) > 4000:
        text = text[:4000] + "\n\n[...mensaje truncado]"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(f"{API_URL}/sendMessage", data=data)
    try:
        urllib.request.urlopen(req, timeout=15)
        log(f"[ENVIADO] Respuesta a Diego ({len(text)} chars)")
    except Exception as e:
        log(f"[ERROR] No pude enviar mensaje: {e}")


def get_updates(offset):
    """Obtener nuevos mensajes de Telegram"""
    url = f"{API_URL}/getUpdates?offset={offset}&timeout=10"
    try:
        resp = urllib.request.urlopen(url, timeout=15)
        data = json.loads(resp.read().decode())
        return data.get("result", [])
    except Exception as e:
        log(f"[ERROR] getUpdates: {e}")
        return []


def ask_ollama(user_message):
    """Enviar mensaje al modelo local y obtener respuesta"""
    global conversation_history
    
    conversation_history.append({"role": "user", "content": user_message})
    
    # Mantener historial limitado
    if len(conversation_history) > MAX_HISTORY:
        conversation_history = conversation_history[-MAX_HISTORY:]
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history
    
    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 300  # Limitar respuesta para Telegram
        }
    }).encode()
    
    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = json.loads(resp.read().decode())
        assistant_msg = data.get("message", {}).get("content", "").strip()
        
        # Limpiar thinking tags si existen
        if "<think>" in assistant_msg:
            import re
            assistant_msg = re.sub(r"<think>.*?</think>", "", assistant_msg, flags=re.DOTALL).strip()
        
        conversation_history.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg
    except Exception as e:
        log(f"[ERROR] Ollama: {e}")
        return f"🩺 Disculpá Diego, tuve un problema procesando tu mensaje. Error: {e}"


def run_system_command(cmd, timeout=15):
    """Ejecutar comando del sistema y devolver output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=isinstance(cmd, str))
        return result.stdout.strip()[:3000]
    except Exception as e:
        return f"Error: {e}"


def handle_command(text, chat_id):
    """Manejar comandos especiales con slash"""
    cmd = text.lower().strip()
    
    if cmd == "/status":
        uptime = run_system_command("uptime")
        mem = run_system_command(["free", "-h"])
        return f"🖥️ Estado del Sistema:\n\n⏱️ {uptime}\n\n💾 Memoria:\n{mem}\n🩺"
    
    elif cmd == "/docker":
        output = run_system_command(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"])
        return f"🐳 Contenedores Docker:\n\n{output}\n🩺"
    
    elif cmd == "/audit":
        output = run_system_command(f"bash {WORKSPACE}/scripts/auditoria_boot.sh", timeout=30)
        return f"🔍 Auditoría:\n\n{output}\n🩺"
    
    elif cmd == "/help":
        return ("🩺 Comandos de Lucy:\n\n"
                "/status - Estado del sistema\n"
                "/docker - Contenedores Docker\n"
                "/audit - Auditoría del sistema\n"
                "/help - Este mensaje\n\n"
                "También podés hablarme libremente y te respondo con IA. 🩺")
    
    return None  # No es un comando


def main():
    log("=" * 50)
    log("Lucy Telegram Listener v2 (CON CEREBRO IA) iniciado")
    log(f"Modelo: {MODEL}")
    log(f"Autorizado: Diego (ID {DIEGO_ID})")
    log("=" * 50)
    
    # Cargar offset guardado
    offset = 0
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE) as f:
                offset = int(f.read().strip())
        except:
            pass
    
    # Enviar mensaje de inicio
    telegram_send(DIEGO_ID, "🩺 Lucy Telegram Listener v2 activado. Ahora tengo cerebro IA con Qwen3-14B. Hablame de lo que quieras. 🩺")
    
    while True:
        try:
            updates = get_updates(offset)
            
            for update in updates:
                update_id = update["update_id"]
                offset = update_id + 1
                
                # Guardar offset
                with open(OFFSET_FILE, "w") as f:
                    f.write(str(offset))
                
                msg = update.get("message", {})
                from_id = msg.get("from", {}).get("id", 0)
                text = msg.get("text", "")
                chat_id = msg.get("chat", {}).get("id", 0)
                
                if not text:
                    continue
                
                # Seguridad: solo Diego
                if from_id != DIEGO_ID:
                    log(f"[BLOQUEADO] Mensaje de ID no autorizado: {from_id}")
                    telegram_send(chat_id, "⛔ Acceso denegado. Este bot es de uso privado.")
                    continue
                
                log(f"[DIEGO] Mensaje: {text}")
                
                # Verificar si es un comando
                cmd_response = handle_command(text, chat_id)
                if cmd_response:
                    telegram_send(chat_id, cmd_response)
                    continue
                
                # Si no es comando, usar IA
                telegram_send(chat_id, "💭 Pensando...")
                ai_response = ask_ollama(text)
                telegram_send(chat_id, ai_response)
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            log("Listener detenido por el usuario.")
            break
        except Exception as e:
            log(f"[ERROR LOOP] {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
