#!/usr/bin/env python3
import requests
import json
import sys
import argparse

# Configuración del Gateway de OpenClaw
OPENCLAW_URL = "http://127.0.0.1:18789/v1/chat/completions"
# El token se recuperó de ~/.openclaw/openclaw.json
OPENCLAW_TOKEN = "e738fcb4688672333267a7339d4bbd8fe8fefb94c9eb0ce0"
DEFAULT_AGENT = "lucy"

def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):
    """
    Delega una misión autónoma al Gateway de OpenClaw.
    """
    headers = {
        "Authorization": f"Bearer {OPENCLAW_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": agent,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": stream
    }
    
    try:
        response = requests.post(OPENCLAW_URL, headers=headers, json=payload, timeout=300)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error en OpenClaw Gateway (Status {response.status_code}): {response.text}"
    except Exception as e:
        return f"Error de comunicación con el puente: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Puente de comunicación Doctora Lucy -> OpenClaw")
    parser.add_argument("mision", help="La misión o prompt para OpenClaw")
    parser.add_argument("--agent", default=DEFAULT_AGENT, help="ID del agente en OpenClaw")
    
    args = parser.parse_args()
    
    result = delegate_mission(args.mision, args.agent)
    print(result)
