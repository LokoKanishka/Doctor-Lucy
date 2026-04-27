# Auditoria OpenClaw / Lucy / Telegram - 2026-04-26

## Estado final

- `openclaw-gateway.service`: activo y habilitado.
- Telegram nativo de OpenClaw: activo, en `polling`, bot `LucyCunningham_bot`, probe OK.
- Modelo primario: `ollama/qwen2.5-coder:14b`.
- Fallbacks: `ollama/qwen3-coder:30b-a3b-q8_0`, `ollama/devstral-small-2:latest`, `google/gemini-2.5-flash`.
- Modelos invalidos `google-2` a `google-6`: retirados del set permitido.
- Sandbox: `agents.defaults.sandbox.mode = all`.
- Web/browser para modelos locales chicos: deshabilitado via `tools.deny`.
- Seguridad OpenClaw: `critical=0`, queda `warn=1` por trusted proxies no configurados; aceptable mientras el gateway siga en loopback/local.

## Fallas encontradas

- Codex `gpt-5.4` estaba configurado como motor principal pero la cuenta tenia limite de uso activo.
- Gemini caia por rate limit y por aliases invalidos (`google-2/gemini-2.0-flash` etc.).
- Ollama no estaba registrado de forma persistente para el gateway.
- La sesion directa `agent:main:main` acumulaba contexto viejo hasta 32k tokens y contaminaba pruebas nuevas.
- Habia 916 entradas de sesiones; la limpieza oficial redujo el store a 99 entradas, incluyendo 42 transcripts faltantes.
- El puente HTTP de Lucy usaba el modelo incorrecto (`main`) y un token sin `operator.write`, generando `403 missing scope`.
- El daemon legacy de Telegram podia competir con Telegram nativo; ahora evita arrancar si OpenClaw ya maneja el bot.

## Cambios aplicados

- Se agrego un drop-in systemd para `OLLAMA_API_KEY=ollama-local`.
- Se configuro Ollama como proveedor local persistente en OpenClaw.
- Se bajo el contexto local a 16k y el bootstrap a limites mas razonables.
- Se redujo la inyeccion de skills en prompt sin eliminar las skills instaladas.
- Se cambio `session.dmScope` a `per-peer` para que Telegram no use una unica sesion global.
- Se limpio el store de sesiones y se retiro la sesion global contaminada.
- Se genero un token operator local para Lucy con scopes `operator.read/operator.write`, guardado fuera del repo con permisos `600`.
- `scripts/lucy_openclaw_bridge.py` ahora usa modo `auto`: HTTP si funciona, fallback al CLI oficial `openclaw agent`.
- `scripts/test_openclaw_gateway.py` prueba por defecto el bridge operativo; el probe HTTP crudo queda opt-in con `OPENCLAW_TEST_HTTP=1`.

## Validaciones

- `openclaw agent --agent main ...`: `OK_AGENT_OPENCLAW_CLEAN`, 3.8s, modelo `ollama/qwen2.5-coder:14b`, 7.9k tokens.
- `OPENCLAW_BRIDGE_MODE=cli scripts/lucy_openclaw_bridge.py`: `OK_LUCY_BRIDGE_CLI`.
- `scripts/lucy_openclaw_bridge.py` en modo auto: `OK_LUCY_BRIDGE_AUTO`.
- `scripts/test_openclaw_gateway.py`: `OK_LUCY_OPENCLAW_BRIDGE`.
- `python3 -m py_compile` paso para bridge, test y daemon legacy.

## Riesgo residual

- Si Fusion/Antigravity carga simultaneamente un modelo Ollama pesado, la latencia de OpenClaw puede subir porque compiten por GPU/CPU. No se modificaron los puertos ni servicios TTS de Fusion.

## Backups relevantes

- `~/.openclaw/openclaw.json.audit-pre-sandbox-202604262233.bak`
- `~/.openclaw/openclaw.json.audit-pre-fastlocal-202604262241.bak`
- `~/.openclaw/openclaw.json.bak`
- `~/.openclaw/agents/main/sessions/sessions.json.audit-pre-cleanup-202604262254.bak`
- Transcripts retirados de `agent:main:main` conservados como archivos `.audit-*`.
