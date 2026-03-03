import asyncio
import aiohttp
import json

async def test():
    OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
    messages = [{"role": "user", "content": "Hola, ¿cómo estás?"}]
    payload = {
        "model": "qwen2.5-coder:14b-instruct-q8_0",
        "messages": messages,
        "stream": False
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            data = await resp.json()
            print(json.dumps(data, indent=2))

asyncio.run(test())
