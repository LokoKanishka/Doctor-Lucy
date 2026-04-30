# OpenClaw MCP Integration

Fecha: 2026-04-30

## Objetivo

Integrar la herramienta read-only `lucy_fs_readonly` como MCP local del OpenClaw principal, para que el runtime pueda leer archivos del repo de forma controlada en fases futuras.

Esta integracion no activa Telegram para la herramienta. Solo registra el MCP en la configuracion principal y valida llamadas locales.

## Proteccion de Doctora Lucy

Durante esta integracion no se tocaron:

- memoria
- n8n
- boveda
- personalidad
- `.env`
- tokens
- Telegram legacy
- scripts ajenos a OpenClaw
- configuracion de MCP aislada previa

## Estado previo

- Modelo principal: `openai-codex/gpt-5.4`
- MCP principal antes del cambio: vacio
- Gateway health antes/despues: `/health 200 {"ok":true,"status":"live"}`

## Backup

Backup obligatorio previo:

- `~/.openclaw/backups-mcp-20260430_003026/openclaw.json.bak`
- `~/.openclaw/backups-mcp-20260430_003026/agents-auth-profiles.tgz`

Instrucciones de rollback:

- `docs/backup-instrucciones.md`

## Cambio aplicado

Se uso el comando oficial:

```bash
openclaw mcp set lucy-fs-readonly '{"command":"python3","args":["/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_fs_mcp_server.py"]}'
```

OpenClaw guardo la definicion en el formato real de esta version:

```json
{
  "mcp": {
    "servers": {
      "lucy-fs-readonly": {
        "command": "python3",
        "args": [
          "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_fs_mcp_server.py"
        ]
      }
    }
  }
}
```

No se modificaron `tools`, `commands.native`, `commands.nativeSkills`, sandbox, memoria ni agentes.

La comparacion estructural contra el backup mostro cambios de top-level solo en:

- `mcp`
- `meta`

## Verificacion MCP

Comandos ejecutados:

```bash
openclaw mcp list --json
openclaw mcp show --json
```

Resultado: ambos muestran `lucy-fs-readonly` con `command: python3` y el wrapper `scripts/lucy_fs_mcp_server.py`.

## Pruebas locales controladas

No se envio Telegram real y no se reinicio el gateway.

Prueba 1:

- comando: `openclaw agent --local --agent main --json --thinking off --timeout 90`
- prompt: llamar `lucy_read_lines` para `scripts/lucy_openclaw_bridge.py` linea `138`
- resultado: devolvio `def delegate_mission(prompt, agent=DEFAULT_AGENT, stream=False):`

Prueba 2:

- comando: `openclaw agent --local --agent main --json --thinking off --timeout 90`
- prompt: llamar `lucy_read_lines` para `docs/OPENCLAW_R38_CODEX_TELEGRAM_VALIDATION.md` linea `15`
- resultado: devolvio `- \`~/.openclaw/backups-r38-model-repair/20260429_223344\``

La segunda prueba usa una linea documental reciente para reducir el riesgo de respuesta por memoria.

## Observaciones

- El agente local corrio con provider `openai-codex` y modelo `gpt-5.4`.
- El `systemPromptReport` incluyo `lucy_find_files`, `lucy_grep_text` y `lucy_read_lines`.
- Aparecio fallback interno de WebSocket a HTTP con `401`, pero la ejecucion local finalizo correctamente.
- No hubo errores MCP relevantes.

## Estado final

- MCP principal registrado: si
- `lucy_read_lines` usable por OpenClaw local: si
- Telegram real para MCP: no probado
- Gateway reiniciado: no
- Servicios reiniciados: no

## Rollback

Para retirar el MCP y volver al estado previo:

```bash
cp -a ~/.openclaw/backups-mcp-20260430_003026/openclaw.json.bak ~/.openclaw/openclaw.json
```

Luego verificar:

```bash
openclaw mcp list --json
openclaw mcp show --json
```

## Recomendacion

No activar pruebas Telegram con MCP hasta que Diego lo autorice explicitamente. El siguiente paso razonable es una fase R39 de planificacion o smoke minimo, con rollback abierto y sin tocar memoria.
