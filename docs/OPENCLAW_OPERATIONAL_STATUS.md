# OpenClaw — Estado operativo post scope fix

Fecha: 2026-04-29

## 1. Commits de cierre

- Fix bridge: `93fb55c fix(openclaw): send gateway scope headers from bridge`
- Cierre documental: `3d00d60 docs(openclaw): document scope header recovery`

## 2. Estado operativo

- Gateway principal `18789` operativo.
- `/v1/models` responde `200` cuando se envía `X-OpenClaw-Scopes`.
- Modelos confirmados:
  - `openclaw`
  - `openclaw/default`
  - `openclaw/main`
  - `openclaw/fusion-research`
- Bridge HTTP responde `OK`.
- El bridge usa por defecto `OPENCLAW_SCOPES=operator.read,operator.write`.

## 3. Rebuild paralelo

El rebuild paralelo queda pausado. Fue útil como entorno de aislamiento, pero no es la vía principal mientras el gateway viejo siga operativo después del fix.

No continuar:
- `doctor --force`;
- `devices rotate`;
- parches de tokens;
- parches de `identity/device-auth.json`;
- migraciones de auth hacia el perfil paralelo.

## 4. Diagnóstico futuro

Si vuelve `500` o `No response from OpenClaw`, el foco ya no debe ser auth/scopes. Investigar:
- provider/modelo;
- sesión del agente;
- fallback chain;
- contenedor sandbox/agent.

## 5. Regla práctica

Para llamadas HTTP OpenAI-compatible al gateway, enviar siempre:

```text
Authorization: Bearer <gateway.auth.token>
X-OpenClaw-Scopes: operator.read,operator.write
```
