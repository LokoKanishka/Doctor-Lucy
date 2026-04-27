#!/usr/bin/env python3
import requests
import json
import sys
import argparse
import os
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

# Configuración del Gateway de OpenClaw
OPENCLAW_URL = os.getenv("OPENCLAW_CHAT_COMPLETIONS_URL", "http://127.0.0.1:18789/v1/chat/completions")
OPENCLAW_CONFIG_PATH = os.getenv("OPENCLAW_CONFIG_PATH", os.path.expanduser("~/.openclaw/openclaw.json"))
OPENCLAW_TOKEN_FILE = os.getenv("OPENCLAW_TOKEN_FILE", os.path.expanduser("~/.openclaw/lucy-bridge-token"))
OPENCLAW_BIN = os.getenv("OPENCLAW_BIN", "openclaw")
DEFAULT_AGENT = "main"
REQUEST_TIMEOUT_S = int(os.getenv("OPENCLAW_BRIDGE_TIMEOUT_S", "180"))
BRIDGE_MODE = os.getenv("OPENCLAW_BRIDGE_MODE", "auto").strip().lower()


def _load_gateway_token():
    token = os.getenv("OPENCLAW_GATEWAY_TOKEN")
    if token:
        return token

    try:
        with open(OPENCLAW_TOKEN_FILE, "r", encoding="utf-8") as f:
            token = f.read().strip()
        if token:
            return token
    except Exception:
        pass

    try:
        with open(OPENCLAW_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("gateway", {}).get("auth", {}).get("token")
    except Exception:
        return None


def _today_context():
    now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    return now.strftime("Hoy es %A %d de %B de %Y y son las %H:%M en Buenos Aires.")


def _http_model_name(agent):
    if agent.startswith("openclaw/"):
        return agent
    return f"openclaw/{agent}"


def _parse_cli_json(raw_output):
    raw_output = raw_output.strip()
    start = raw_output.find("{")
    if start == -1:
        raise ValueError("la salida de openclaw no contiene JSON")
    return json.loads(raw_output[start:])


def _call_openclaw_cli(prompt, agent=DEFAULT_AGENT):
    command = [
        OPENCLAW_BIN,
        "agent",
        "--agent",
        agent,
        "--message",
        prompt,
        "--thinking",
        "off",
        "--json",
        "--timeout",
        str(REQUEST_TIMEOUT_S),
    ]

    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        timeout=REQUEST_TIMEOUT_S + 10,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        return f"Error en OpenClaw CLI (exit {completed.returncode}): {detail[-1200:]}"

    try:
        data = _parse_cli_json(completed.stdout)
        payloads = data.get("result", {}).get("payloads", [])
        texts = [item.get("text", "") for item in payloads if item.get("text")]
        return "\n".join(texts).strip() or "Error: OpenClaw CLI no devolvió texto."
    except Exception as exc:
        return f"Error: no pude interpretar la salida de OpenClaw CLI: {type(exc).__name__}: {exc}"


def _call_openclaw_http(prompt, agent=DEFAULT_AGENT, stream=False):
    soul_path = "/home/lucy-ubuntu/Escritorio/doctor de lucy/SOUL.md"
    if os.path.exists(soul_path):
        with open(soul_path, "r") as f:
            soul = f.read()
    else:
        soul = "Sos Lucy, asistente técnica de Diego."

    soul = f"{_today_context()}\n{soul}"

    token = _load_gateway_token()
    if not token:
        return f"Error: no encontré token de OpenClaw en {OPENCLAW_CONFIG_PATH} ni en OPENCLAW_GATEWAY_TOKEN."

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": _http_model_name(agent),
        "messages": [
            {"role": "system", "content": soul},
            {"role": "user", "content": prompt}
        ],
        "stream": stream
    }
    
    try:
        response = requests.post(OPENCLAW_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_S)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        return f"Error en OpenClaw Gateway (Status {response.status_code}): {response.text}"
    except Exception as e:
        return f"Error: Excepcion en el puente: {type(e).__name__}: {e}"


def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):
    """
    Delega una misión autónoma a OpenClaw.

    Modo por defecto:
    - intenta HTTP si hay token de gateway;
    - si HTTP falla por permisos/scope o disponibilidad, usa el CLI oficial.
    """
    mission = f"{_today_context()}\n\nMisión recibida desde Doctora Lucy:\n{prompt}"

    if BRIDGE_MODE == "cli":
        return _call_openclaw_cli(mission, agent)

    if BRIDGE_MODE in ("auto", "http"):
        http_result = _call_openclaw_http(mission, agent, stream)
        if BRIDGE_MODE == "http":
            return http_result
        if not http_result.startswith("Error"):
            return http_result

    return _call_openclaw_cli(mission, agent)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Puente de comunicación Doctora Lucy -> OpenClaw")
    parser.add_argument("mision", help="La misión o prompt para OpenClaw")
    parser.add_argument("--agent", default=DEFAULT_AGENT, help="ID del agente en OpenClaw")
    
    args = parser.parse_args()
    
    result = delegate_mission(args.mision, args.agent)
    print(result)
