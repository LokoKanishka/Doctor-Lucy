import sys
import asyncio

sys.path.append("/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts")
import lucy_daemon_v2_cloud

async def run_test():
    lucy_daemon_v2_cloud.log("🚀 Iniciando prueba de estrés interna (Simulando mensaje de Diego)")
    await lucy_daemon_v2_cloud.agent_loop("Hola Lucy. Prueba de estrés 2: chequeo del fallback de timeout de OpenClaw. Contestame.", lucy_daemon_v2_cloud.DIEGO_ID)

if __name__ == "__main__":
    asyncio.run(run_test())
