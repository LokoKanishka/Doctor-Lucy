# LucyClaw Machine NL Runtime (AG-HOST-NL3)

Date: 2026-05-06

## Objective

Resolver el intercepto real pre-modelo para que consultas naturales de máquina en Telegram activen herramientas `machine_*` ya existentes sin respuesta previa del modelo conversacional.

## Strategy

Estrategia elegida: `C` — patch mínimo controlado del gateway local.

Razón:
- OpenClaw sí tiene ejecución pre-LLM de plugin commands.
- Esa vía es slash-only: `matchPluginCommand()` y `registerPluginCommand()` requieren `/`.
- Los hooks auditados (`message_received`, `before_prompt_build`, `before_agent_start`) no ofrecen short-circuit limpio con reply directa por canal.
- El punto real de entrada de Telegram vive en el runtime local del gateway, dentro de `reply-DeXK9BLT.js`.

## Runtime Change

Archivo runtime externo modificado:
- `/home/lucy-ubuntu/.npm-global/lib/node_modules/openclaw/dist/reply-DeXK9BLT.js`

Backup creado:
- `/home/lucy-ubuntu/.openclaw/backups/AG_HOST_NL3/reply-DeXK9BLT.js.bak`

Cambio conceptual:
- En `resolveTelegramInboundBody()` se toma el texto natural entrante.
- Si no empieza con `/`, se invoca `scripts/lucy_machine_nl_router.py`.
- Si el router devuelve una intención reconocida y segura, se sintetiza un slash interno determinístico:
  - `/machine_downloads`
  - `/machine_ls /home/lucy-ubuntu/Escritorio`
  - `/machine_status`
  - `/machine_processes`
  - `/machine_ram`
  - `/machine_disk`
  - `/machine_gpu`
- Ese slash interno se inyecta como `BodyForCommands` y `CommandBody`.
- OpenClaw sigue su camino normal y `handlePluginCommand()` corta antes del modelo.

## Why This Avoids Double Reply

No se responde desde un hook paralelo.
El turno entra al mismo flujo interno que usan los slash commands/plugin commands.
Cuando `CommandBody` ya es `/machine_*`, OpenClaw resuelve `matchPluginCommand()` y devuelve `shouldContinue:false`, por lo que no entra al agente conversacional para ese turno.

## Supported Phrases

Soportadas por el router existente:
- `qué carpetas hay en el escritorio`
- `qué hay en descargas`
- `qué fue lo último que descargué`
- `qué hay activo en la pc`
- `cuánta ram estoy usando`
- `cómo está la gpu`
- `cuánta vram estoy usando`
- `qué procesos están corriendo`
- `cuánto disco tengo`

## Safety Limits

- No se creó nueva herramienta de máquina.
- No se duplicó lógica de lectura de máquina.
- No se tocaron `.env`, tokens, memoria, bóveda, personalidad ni `n8n_data`.
- No se tocó `~/.openclaw/openclaw.json`.
- No TTS.
- No `voice_payload`.
- No `sudo`.

## Validation

Validado localmente:
- router Python compila y reconoce frases esperadas
- wrappers `machine_access` y `machine_status` siguen devolviendo `ok:true`
- `SEC1` ok
- `QA1` ok
- `run_registry` valid
- gateway reiniciado una sola vez y `/health` volvió `live`

Pendiente:
- verificación funcional por Telegram con Diego

## Rollback

1. Restaurar backup:
   `cp -p /home/lucy-ubuntu/.openclaw/backups/AG_HOST_NL3/reply-DeXK9BLT.js.bak /home/lucy-ubuntu/.npm-global/lib/node_modules/openclaw/dist/reply-DeXK9BLT.js`
2. Reiniciar:
   `systemctl --user restart openclaw-gateway.service`

## Final State

- Runtime intercept implementado en el camino real de Telegram.
- Gateway vivo post-restart.
- Estado funcional todavía en `NEEDS_REVIEW` hasta prueba Telegram.
