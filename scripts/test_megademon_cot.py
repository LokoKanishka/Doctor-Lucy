import asyncio
import json
import aiohttp
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_MODEL = "qwen2.5-coder:14b-instruct-q8_0"
OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"

async def test_agentic_loop(user_text: str):
    print("Levantando MCP Sequential Thinking...")
    server_params = StdioServerParameters(command="npx", args=["-y", "@modelcontextprotocol/server-sequential-thinking"])
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()
            tools_response = await mcp_session.list_tools()
            
            # Preparar Tools
            ollama_tools = []
            for t in tools_response.tools:
                ollama_tools.append({"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.inputSchema}})
            
            ollama_tools.append({
                "type": "function", "function": {
                    "name": "create_mission", "description": "Crea una mision para accionar comandos complejos o herramientas externas al finalizar de pensar.",
                    "parameters": {"type": "object", "properties": {"tasks": {"type": "array"}}, "required": ["tasks"]}
                }
            })

            messages = [
                {"role": "system", "content": "Sos Doctora Lucy, el sistema de asistencia. Piensa paso a paso si es necesario."},
                {"role": "user", "content": user_text}
            ]

            print(f"\n[Usuario]: {user_text}")
            
            for loop_count in range(5):
                payload = {
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "tools": ollama_tools
                }
                
                async with aiohttp.ClientSession() as http_session:
                    async with http_session.post(OLLAMA_CHAT_URL, json=payload) as resp:
                        data = await resp.json()
                        msg = data.get("message", {})
                        
                        if not msg.get("tool_calls"):
                            print(f"\n🤖 [Doctora Lucy Respuesta Final]: {msg.get('content', '')}")
                            return
                            
                        messages.append(msg)
                        
                        for tc in msg.get("tool_calls", []):
                            t_name = tc["function"]["name"]
                            t_args = tc["function"]["arguments"]
                            
                            if t_name == "sequentialthinking":
                                print(f"🧠 [Pensamiento {t_args.get('thoughtNumber', '?')}]: {t_args.get('thought')}")
                                result = await mcp_session.call_tool(t_name, arguments=t_args)
                                messages.append({"role": "tool", "name": t_name, "content": result.content[0].text})
                            else:
                                print(f"🛠️ [Llamó Tool]: {t_name} -> {t_args}")
                                return

print("\n--- PRUEBA DIRECTA DE QWEN 14B + SECUENCIAL MCP ---")
asyncio.run(test_agentic_loop("hora"))
