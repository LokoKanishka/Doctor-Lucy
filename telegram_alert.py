#!/usr/bin/env python3
import urllib.request
import json
import ssl
import sys

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales desde el entorno
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_DIEGO_ID")

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        payload = json.dumps({
            "chat_id": CHAT_ID,
            "text": f"\ud83e\ude7a **Doctora Lucy**:\n{message}",
            "parse_mode": "Markdown"
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, context=ctx) as response:
            res_data = json.loads(response.read().decode())
            if res_data.get("ok"):
                return {"success": True, "message": "Alerta enviada correctamente."}
            else:
                return {"success": False, "error": str(res_data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Se requiere un mensaje como argumento."}))
        sys.exit(1)
    
    msg = sys.argv[1]
    result = send_telegram_message(msg)
    print(json.dumps(result))
