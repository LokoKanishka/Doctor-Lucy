# LucyClaw Machine NL Router (AG-HOST-NL2)

## Objetivo
Agregar una capa determinística de lenguaje natural para consultas de máquina frecuentes sin crear herramientas nuevas de máquina.

## Arquitectura real encontrada
- El mensaje natural de Telegram entra por `openclaw-gateway.service`.
- El gateway corre `openclaw ... gateway --port 18789`.
- `~/.openclaw/openclaw.json` carga los plugins `/machine_*` existentes desde `openclaw_plugins/`.
- `scripts/lucy_telegram_listener.py` existe, pero no es el runtime activo de Telegram.
- `scripts/lucy_openclaw_bridge.py` es un puente local hacia OpenClaw, pero no es el punto real de entrada de Telegram.

## Diagnóstico de hooks
- OpenClaw sí expone los hook names `message_received`, `before_prompt_build` y `before_agent_start`.
- `message_received` corre en modo fire-and-forget y no permite cancelar ni reemplazar el turno.
- `before_prompt_build` y `before_agent_start` solo permiten mutar prompt/modelo.
- El contexto del hook `message_received` expone `channelId`, `accountId` y `conversationId`, pero no un API de respuesta directa por canal.

## Estrategia elegida
Se implementó la parte segura y verificable:
- router local determinístico en `scripts/lucy_machine_nl_router.py`
- QA mínimo del matching
- documentación y evidencia del bloqueo runtime real
- preservación explícita de los wrappers `machine_*` ya activos

No se integró el runtime de Telegram porque las dos rutas aceptables quedaron descartadas por arquitectura:
- Opción A, plugin OpenClaw limpio: no ofrece short-circuit pre-modelo estable con respuesta por canal.
- Opción B, listener/bridge propio: no está en el camino real del mensaje de Telegram hoy.

## Estado de integración
- AG-HOST-NL2 no está integrado a Telegram.
- AG-HOST-NL2 no modifica runtime de OpenClaw.
- AG-HOST-NL2 no tocó `~/.openclaw/openclaw.json`.
- AG-HOST-NL2 no requirió restart del gateway.
- AG-HOST-NL2 queda como diagnóstico local y preparación técnica, no como función runtime cerrada.

## Frases soportadas
- `qué carpetas hay en el escritorio`
- `qué hay en descargas`
- `qué fue lo último que descargué`
- `qué hay activo en la pc`
- `cuánta ram estoy usando`
- `cómo está la gpu`
- `cuánta vram estoy usando`
- `qué procesos están corriendo`
- `cuánto disco tengo`

## Comandos destino
- escritorio -> `machine_ls /home/lucy-ubuntu/Escritorio`
- descargas -> `machine_downloads`
- estado pc -> `machine_status`
- ram -> `machine_ram`
- gpu/vram -> `machine_gpu`
- procesos -> `machine_processes`
- disco -> `machine_disk`

## Qué no hace
- No ejecuta comandos.
- No usa red.
- No usa `subprocess`.
- No lee documentos.
- No toca `~/.openclaw/openclaw.json`.
- No toca TTS, memoria, bóveda, personalidad, `.env`, tokens ni n8n.
- No resuelve todavía el despacho real desde Telegram al wrapper de máquina.

## Cómo probar
```bash
python3 scripts/lucy_machine_nl_router.py "qué carpetas hay en el escritorio"
python3 scripts/lucy_machine_nl_router.py "qué fue lo último que descargué"
python3 scripts/lucy_machine_nl_router.py "qué hay activo en la pc"
python3 scripts/lucy_machine_nl_router.py "cuánta ram estoy usando"
python3 scripts/lucy_machine_nl_router.py "cómo está la gpu"
python3 scripts/lucy_machine_nl_router.py "hola cómo estás"
```

## Rollback
- Eliminar `scripts/lucy_machine_nl_router.py`
- revertir cambios en `scripts/verify_lucyclaw_green_commands.py`
- revertir documentación y registro de corrida AG-HOST-NL2

## Estado final
- Router local: implementado y validado.
- Wrappers `/machine_*`: preservados.
- Runtime Telegram/OpenClaw: no modificado.
- Estado AG-HOST-NL2: `NEEDS_REVIEW`.
- Cierre técnico AG-HOST-NL2: no.
- Cierre funcional AG-HOST-NL2: no.
- Próximo paso recomendado: `AG-HOST-NL3`, resolver un intercepto pre-modelo real o una alternativa de bridge controlada antes de intentar cierre funcional.
