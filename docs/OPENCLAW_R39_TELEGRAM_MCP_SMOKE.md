# OpenClaw R39 Telegram MCP Smoke

Fecha: 2026-04-30

## Objetivo

Validar de forma minima si el Telegram nativo del OpenClaw principal ve y puede usar el MCP read-only `lucy-fs-readonly`.

La prueba se corto antes de pedir lectura por Telegram porque `/tools` no mostro las tools MCP.

## Estado inicial

- Rama: `memoria/bunker`
- HEAD inicial: `29d899f docs(openclaw): document readonly MCP integration`
- Ahead/behind: `0/0`
- Estado de trabajo: solo no trackeados previos:
  - `.agents/archive_openclaw_scope_fix_20260429_153235/`
  - `docs/OPENCLAW_REBUILD_1A_PROFILE.md`

## Preflight local

- Gateway health: `200 {"ok":true,"status":"live"}`
- Modelo default/resuelto: `openai-codex/gpt-5.4`
- MCP principal: `lucy-fs-readonly` registrado
- Helper directa:
  - path: `scripts/lucy_openclaw_bridge.py`
  - line: `138`
  - text: `def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):`

## Telegram

Diego ejecuto manualmente en Telegram:

```text
/model status
```

Resultado relevante:

- Current: `openai-codex/gpt-5.4`
- Default: `openai-codex/gpt-5.4`
- Agent: `main`
- OAuth Codex presente

Luego ejecuto:

```text
/tools compact
```

Resultado:

- Mostro solo herramientas built-in.
- No mostro `lucy_read_lines`.
- No mostro `lucy_grep_text`.
- No mostro `lucy_find_files`.

Tambien ejecuto:

```text
/tools verbose
```

Resultado:

- Confirmo perfil `full` y herramientas built-in.
- No mostro tools MCP `lucy_*`.

## Decision de corte

Como `/tools` no mostro `lucy_read_lines`, no se envio la prueba de lectura MCP por Telegram.

Esto cumple el criterio de corte de R39: no insistir con prompts si la sesion real no expone la herramienta.

## Verificacion post-smoke

- `git status --short`: sin cambios nuevos de ejecucion, solo no trackeados previos.
- Gateway health post-smoke: `200 {"ok":true,"status":"live"}`
- Logs relevantes:
  - Telegram respondio `/model status` y `/tools`.
  - No hubo evidencia de uso de `lucy_read_lines` por Telegram.
  - No hubo errores graves MCP durante la prueba.
  - Se observaron mensajes historicos de fallback WebSocket a HTTP y fallback IPv4 de Telegram.
  - Se observo que el cambio previo de `mcp` disparo reload/restart automatico del gateway por OpenClaw; no fue reiniciado manualmente en R39.

## Rollback

- Necesario: no
- Aplicado: no
- Backup disponible para rollback MCP:
  - `~/.openclaw/backups-mcp-20260430_003026/openclaw.json.bak`
- Instrucciones:
  - `docs/backup-instrucciones.md`

## Proteccion de Doctora Lucy

No se tocaron:

- memoria
- n8n
- boveda
- personalidad
- `.env`
- tokens
- Telegram legacy
- scripts ajenos a OpenClaw

No se uso:

- `/mcp`
- `/bash`
- `/exec`
- permisos elevados
- lectura fuera del repo
- escritura

## Diagnostico

- MCP principal registrado: si
- MCP usable localmente por OpenClaw principal: si, validado en R39 previo con `openclaw agent --local`
- Telegram ve tools MCP: no
- Telegram MCP operativo: no determinado, porque la sesion no expuso las tools

La limitacion actual no parece estar en el wrapper ni en el registro `openclaw mcp`. La sesion Telegram actual lista solo herramientas built-in, por lo que el runtime/adaptador Telegram no esta exponiendo las tools MCP registradas.

## Proximo paso recomendado

No insistir con prompts.

Disenar R40 para investigar o implementar una via deterministica, por ejemplo:

- skill o slash command controlado tipo `/fs_read`
- `command-dispatch: tool` si OpenClaw lo soporta para este caso
- verificacion de runtime adapter para que consuma MCP registrado

Cualquier siguiente paso debe mantener rollback abierto y no tocar memoria, n8n, boveda ni personalidad.
