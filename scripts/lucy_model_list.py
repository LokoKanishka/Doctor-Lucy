import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv("/home/lucy-ubuntu/Escritorio/doctor de lucy/.env")
KEYS = [os.getenv(f"GEMINI_API_KEY{'' if i==0 else '_'+str(i+1)}") for i in range(6)]

async def list_models(index, key):
    if not key: return f"Key {index}: Missing"
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m["name"].split("/")[-1] for m in data.get("models", [])]
                    return f"Key {index}: ✅ OK (Visible models: {len(models)})"
                else:
                    return f"Key {index}: ❌ {resp.status}"
    except Exception as e:
        return f"Key {index}: ❌ {str(e)}"

async def audit():
    tasks = [list_models(i+1, k) for i, k in enumerate(KEYS)]
    results = await asyncio.gather(*tasks)
    for res in results: print(res)

if __name__ == "__main__":
    asyncio.run(audit())
