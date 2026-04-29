# OpenClaw — Smoke de integración post scope fix

Fecha: 2026-04-29

## 1. Base

- Rama: `memoria/bunker`
- Commit base: `33eead9 docs(openclaw): record operational status after scope fix`
- Fix de scopes: `93fb55c fix(openclaw): send gateway scope headers from bridge`

## 2. Gateway y bridge

- Gateway principal `18789`: activo.
- `/health`: `200`.
- `/v1/models` con `X-OpenClaw-Scopes: operator.read,operator.write`: `200`.
- Modelos listados:
  - `openclaw`
  - `openclaw/default`
  - `openclaw/main`
  - `openclaw/fusion-research`
- Bridge CLI HTTP: `OK`.

## 3. Smoke por import Python

Se importó `delegate_mission` desde `scripts/lucy_openclaw_bridge.py` con:

```text
OPENCLAW_BRIDGE_MODE=http
OPENCLAW_CHAT_COMPLETIONS_URL=http://127.0.0.1:18789/v1/chat/completions
```

Resultado:

```text
OK
```

## 4. Integración detectada

Scripts que usan OpenClaw o el bridge:

- `scripts/lucy_openclaw_bridge.py`
- `scripts/lucy_daemon_v2_cloud.py`
- `scripts/lucy_stress_test_v2.py`
- `scripts/test_openclaw_gateway.py`
- `scripts/test_stress.py`

Daemon/listener implicados:

- `scripts/lucy_daemon_v2_cloud.py` importa `delegate_mission` y delega a OpenClaw.
- `scripts/lucy_telegram_listener.py` es un listener legacy con Ollama local; no usa el bridge OpenClaw.
- `scripts/lucy_daemon_v1.py` es daemon legacy local/ReAct; no usa el bridge OpenClaw.

## 5. Telegram y daemons

No se enviaron mensajes reales por Telegram.

No se reiniciaron daemons.

No se reinició el gateway.

## 6. Logs observados

Los logs recientes muestran respuestas `OK` del gateway. Persisten señales históricas/transitorias que, si reaparecen, deben diagnosticarse como runtime/provider/sesión:

- `getUpdates conflict` de Telegram.
- `xai-auth bootstrap config fallback`.
- `low context window` en modelos Ollama.
- conflictos previos de contenedor sandbox/agent.
- `No reply from agent` previo.

No reapareció `missing scope` durante el smoke.

## 7. Próximo paso

La integración base Doctora Lucy -> bridge -> OpenClaw está funcional.

El próximo tramo puede ser una validación controlada de `lucy_daemon_v2_cloud.py` sin envío externo, o una prueba Telegram/daemon cuidadosamente aislada. Si vuelve `500` o `No response from OpenClaw`, no volver a diagnosticar scopes si el header está presente; revisar provider/modelo/sesión/contenedor.
