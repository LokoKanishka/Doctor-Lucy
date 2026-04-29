# OpenClaw — Fix real de scopes HTTP

## 1. Hallazgo

El gateway OpenClaw no estaba definitivamente corrupto. El rechazo `403 missing scope: operator.read` se debía a que las llamadas HTTP OpenAI-compatible no enviaban el header `X-OpenClaw-Scopes`.

## 2. Evidencia

- Sin header de scopes: `/v1/models` devolvía `403`.
- Con `X-OpenClaw-Scopes: operator.read`: `/v1/models` devolvió `200`.
- Con `X-OpenClaw-Scopes: operator.read,operator.write`: `/v1/models` devolvió `200`.
- El bridge respondió `OK` con scopes explícitos y con scopes default.

## 3. Fix aplicado

Commit: `93fb55c fix(openclaw): send gateway scope headers from bridge`.

Archivo:
- `scripts/lucy_openclaw_bridge.py`

Cambio:
- `OPENCLAW_SCOPES`
- default: `operator.read,operator.write`
- header: `X-OpenClaw-Scopes`

## 4. Estado actual

- Gateway viejo 18789 operativo.
- Modelos listados:
  - `openclaw`
  - `openclaw/default`
  - `openclaw/main`
  - `openclaw/fusion-research`
- `openclaw/main` responde `OK`.
- Bridge HTTP responde `OK`.

## 5. Rebuild paralelo

El rebuild paralelo queda pausado. Fue útil para aislar el problema, pero ya no es la vía principal.

Mantener:
- `docs/OPENCLAW_REBUILD_PLAN.md`
- `docs/OPENCLAW_REBUILD_0_PREFLIGHT.md`
- backups Force-Gate

No continuar salvo que vuelva a fallar el gateway viejo después del fix.

## 6. Problemas restantes

Si vuelve `No response from OpenClaw` o `500`, el foco ya no es auth/scopes, sino:
- provider/modelo;
- sesión del agente;
- fallback chain;
- contenedor sandbox/agent.
