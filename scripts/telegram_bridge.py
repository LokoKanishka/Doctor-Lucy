import sys
import json
import urllib.request
import urllib.parse
import os

if not os.getenv("DOCTOR_LUCY_ALLOW_LEGACY_TELEGRAM_BRIDGE"):
    print("LEGACY BLOCKED: telegram_bridge.py fue reemplazado por lucy_telegram_listener.py / lucy_telegram_send.sh.")
    sys.exit(2)

# Credenciales oficiales de @DocLucyBot
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales desde el entorno
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DIEGO_ID = os.getenv("TELEGRAM_DIEGO_ID")

def get_bot_info():
    url = f"https://api.telegram.org/bot{TG_TOKEN}/getMe"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def send_message(text):
    # Validar primero el bot
    info = get_bot_info()
    bot_username = info['result']['username']
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": DIEGO_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        return result, bot_username

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 telegram_bridge.py 'mensaje'")
        sys.exit(1)
    
    mensaje = sys.argv[1]
    try:
        resultado, username = send_message(mensaje)
        if resultado.get("ok"):
            print(f"✅ Mensaje enviado exitosamente desde @{username}")
        else:
            print(f"❌ Error reportado por Telegram: {resultado}")
    except Exception as e:
        print(f"💥 Error crítico: {e}")
