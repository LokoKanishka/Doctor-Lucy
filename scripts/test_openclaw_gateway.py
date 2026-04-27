import json
import os
import requests

from lucy_openclaw_bridge import delegate_mission

URL = "http://127.0.0.1:18789/v1/chat/completions"


def load_gateway_token():
    token = os.getenv("OPENCLAW_GATEWAY_TOKEN")
    if token:
        return token

    token_path = os.getenv("OPENCLAW_TOKEN_FILE", os.path.expanduser("~/.openclaw/lucy-bridge-token"))
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            token = f.read().strip()
        if token:
            return token
    except Exception:
        pass

    config_path = os.getenv("OPENCLAW_CONFIG_PATH", os.path.expanduser("~/.openclaw/openclaw.json"))
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)["gateway"]["auth"]["token"]

def test_openclaw():
    token = load_gateway_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openclaw/main",
        "messages": [
            {"role": "user", "content": "Prueba corta: respondé exactamente OK_OPENCLAW_GATEWAY."}
        ],
        "stream": False,
        "max_tokens": 32
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=20)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_lucy_bridge():
    print("Bridge:")
    print(delegate_mission("Prueba corta: respondé exactamente OK_LUCY_OPENCLAW_BRIDGE."))

if __name__ == "__main__":
    if os.getenv("OPENCLAW_TEST_HTTP") == "1":
        test_openclaw()
    else:
        print("HTTP: skipped (set OPENCLAW_TEST_HTTP=1 to probe raw /v1/chat/completions)")
    test_lucy_bridge()
