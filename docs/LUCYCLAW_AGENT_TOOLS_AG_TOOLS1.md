# LucyClaw Agent Tools (AG-TOOLS1)

## Objetivo
Exponer las capacidades `machine_*` como agent tools reales de OpenClaw para que el modelo pueda invocarlas desde lenguaje natural sin depender de slash commands ni de routers por frases.

## Por qué se abandona el router por frases
- El router NL local de `AG-HOST-NL2` sirvió como diagnóstico, pero no resolvía el flujo real de Telegram.
- `AG-HOST-NL3` intentó interceptar runtime y fue rollbackeado por romper mensajes normales.
- OpenClaw ya soporta `api.registerTool(...)`, que es el camino correcto para function calling general.

## Diferencia entre slash command y agent tool
- Slash command: lo dispara el usuario explícitamente con `/machine_status`.
- Agent tool: el LLM decide invocarla durante un run cuando entiende una intención compatible.

## Tools registradas
- `lucy_machine_downloads`
- `lucy_machine_ls`
- `lucy_machine_stat`
- `lucy_machine_status`
- `lucy_machine_processes`
- `lucy_machine_ram`
- `lucy_machine_gpu`
- `lucy_machine_disk`
- `lucy_machine_read`
- `lucy_machine_doc_brief`

## Cómo se habilitan
- Plugin separado: `openclaw_plugins/lucy-machine-agent-tools/`
- Registro mediante `api.registerTool(...)`
- Reutiliza wrappers Python existentes; no duplica lógica de máquina
- En esta instalación no fue necesario agregar `tools.allow`; solo `tools.deny` global ya existente

## Modelo y proveedor requeridos
- Agente principal: `openai-codex/gpt-5.4`
- Fallbacks configurados: Ollama (`qwen3-coder`, `devstral-small-2`) y Gemini
- Ollama local está configurado con API nativa (`api=ollama`, `baseUrl=http://127.0.0.1:11434`) y no con `/v1`

## Pruebas locales
- `node --check` del plugin nuevo
- `verify_lucyclaw_green_commands.py` con smoke específico de `registerTool`
- `verify_lucyclaw_security_policy.py`
- `verify_run_registry.py`
- Wrappers `machine_access`, `machine_status` y `machine_read` preservados

## Límites
- Las tools no resuelven nombres ambiguos de archivos por sí solas; si el modelo no puede inferir un path exacto, debe pedir más precisión o encadenar otra tool
- `lucy_machine_doc_brief` devuelve extracto literal, no resumen semántico profundo
- El cierre funcional depende de prueba real por Telegram

## Rollback
- `openclaw plugins uninstall lucy-machine-agent-tools`
- remover la entrada vinculada en `~/.openclaw/openclaw.json` si quedara persistida
- reiniciar `openclaw-gateway.service`
- revertir el commit `feat(lucyclaw): expose machine capabilities as agent tools`
