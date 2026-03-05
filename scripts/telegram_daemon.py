import sys
import json
import urllib.request
import urllib.parse
import time
import os
from datetime import datetime

# Credenciales oficiales de @DocLucyBot
TG_TOKEN = "8547120935:AAFIQvH5-HTYLIvVMBUxxCjg_TC7AZAMwu0"
DIEGO_ID = 5154360597

# Directorio para persistencia de estado
STATE_FILE = "/home/lucy-ubuntu/Escritorio/doctor de lucy/data/telegram_daemon_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_update_id": 0}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def call_telegram(method, payload=None):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/{method}"
    data = None
    if payload:
        data = json.dumps(payload).encode('utf-8')
    
    headers = {'Content-Type': 'application/json'} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"⚠️ Error en API Telegram ({method}): {e}")
        return None

def send_reply(chat_id, text):
    call_telegram("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    })

def handle_command(text, chat_id):
    cmd = text.lower().strip()
    
    if cmd == "/start":
        send_reply(chat_id, "🦾 *Doctora Lucy Escuchando:* Hola Diego. Ahora mi canal de comunicación es bidireccional. ¿En qué puedo ayudarte?")
    elif cmd == "/status":
        ts = datetime.now().strftime("%H:%M:%S")
        send_reply(chat_id, f"🩺 *Reporte de Signos Vitales ({ts}):*\n- Conciencia: Operativa\n- Bóveda: Sincronizada\n- DJ Lucy: 🎵 Lista\n- n8n: Online")
    elif cmd == "/help":
        help_text = (
            "📖 *Comandos Disponibles:*\n"
            "- `/status`: Mi estado actual.\n"
            "- `/help`: Esta guía.\n"
            "- `poné [cancion]`: Reproduce música de YouTube.\n"
            "- `pará`: Detiene la música."
        )
        send_reply(chat_id, help_text)
    elif any(x in cmd for x in ["poné", "reproducí", "pone", "reproduci", "play"]):
        query = text.lower().replace("poné", "").replace("reproducí", "").replace("pone", "").replace("reproduci", "").replace("play", "").strip()
        if query:
            send_reply(chat_id, f"🔍 Buscando '{query}' en la colmena musical...")
            res = os.popen(f"python3 '/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/nin_dj.py' play '{query}'").read()
            send_reply(chat_id, res)
        else:
            send_reply(chat_id, "❓ ¿Qué canción querés que ponga?")
    elif any(x in cmd for x in ["pará", "detener", "stop", "para"]):
        res = os.popen(f"python3 '/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/nin_dj.py' stop").read()
        send_reply(chat_id, res)
    else:
        send_reply(chat_id, f"🧬 *Doctora Lucy:* Recibido, Diego. Me pediste: '{text}'. (IA Local en progreso).")

def poll_updates():
    state = load_state()
    last_id = state.get("last_update_id", 0)
    
    print(f"👹 Daemon de Doctora Lucy iniciado (@DocLucyBot)")
    print(f"👂 Escuchando a Diego (ID: {DIEGO_ID})...")
    
    while True:
        try:
            updates = call_telegram("getUpdates", {"offset": last_id + 1, "timeout": 30})
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    last_id = update["update_id"]
                    msg = update.get("message", {})
                    user_id = msg.get("from", {}).get("id")
                    text = msg.get("text")
                    
                    if user_id == DIEGO_ID and text:
                        print(f"📩 Mensaje de Diego: {text}")
                        handle_command(text, DIEGO_ID)
                    
                    # Actualizar estado para no repetir mensajes
                    state["last_update_id"] = last_id
                    save_state(state)
            
        except KeyboardInterrupt:
            print("\n🛑 Daemon detenido.")
            break
        except Exception as e:
            print(f"💥 Error en el loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    poll_updates()
