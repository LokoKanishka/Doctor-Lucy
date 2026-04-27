import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv("/home/lucy-ubuntu/Escritorio/doctor de lucy/.env")

KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
    os.getenv("GEMINI_API_KEY_5"),
    os.getenv("GEMINI_API_KEY_6")
]

MODEL = "gemini-1.5-flash" # Use flash for quota test

async def test_key(index, key):
    if not key: return f"Key {index}: Missing"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"
    payload = {"contents": [{"parts": [{"text": "ping"}]}]}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    return f"Key {index}: ✅ OK"
                else:
                    data = await resp.json()
                    error_msg = data.get("error", {}).get("message", "Unknown error")
                    return f"Key {index}: ❌ {resp.status} - {error_msg}"
    except Exception as e:
        return f"Key {index}: ❌ Exception - {str(e)}"

async def audit():
    print("🩺 Auditing Gemini Quotas...")
    tasks = [test_key(i+1, k) for i, k in enumerate(KEYS)]
    results = await asyncio.gather(*tasks)
    for res in results:
        print(res)

if __name__ == "__main__":
    asyncio.run(audit())
