import requests
import json

URL = "http://127.0.0.1:18789/v1/chat/completions"
TOKEN = "e738fcb4688672333267a7339d4bbd8fe8fefb94c9eb0ce0"

def test_openclaw():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "lucy",
        "messages": [
            {"role": "user", "content": "Hola, ¿quién sos?"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_openclaw()
