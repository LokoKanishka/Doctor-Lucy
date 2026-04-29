# Legacy Daemon PID Cleanup R21

Fecha: 2026-04-29

## Alcance

- No se envio Telegram.
- No se ejecuto `main()` de `lucy_daemon_v2_cloud.py`.
- No se llamo `getUpdates`.
- No se reiniciaron servicios.
- No se modifico `~/.openclaw`.
- No se tocaron tokens.
- No se instalaron dependencias.

## Estado previo

- Rama: `memoria/bunker`.
- HEAD previo: `90f319f docs(lucy): decide telegram runtime`.
- Sincronizacion previa con `origin/memoria/bunker`: `0/0`.
- No habia procesos vivos de:
  - `lucy_daemon_v2_cloud.py`
  - `lucy_telegram_listener.py`
  - `telegram_daemon.py`
  - `telegram_bridge.py`
- `n8n_data/daemon.pid` existia.
- PID registrado: `382321`.
- Proceso para ese PID: no vivo.
- `openclaw-gateway.service` seguia activo y running, sin reinicios.

## Limpieza realizada

Se retiro el PID muerto del path activo con backup previo:

- Backup: `n8n_data/daemon.pid.dead.20260429_185731.bak`
- Archivo retirado: `n8n_data/daemon.pid.removed.20260429_185731`
- `n8n_data/daemon.pid` activo despues de la limpieza: no existe.
- SHA-256 del backup: `708c1fe346c62b4494cae149dd91a07aa35dc7f49f220421c5ab6eb65b8f76ba`

Los archivos de `n8n_data/` son runtime local e ignorados por Git; este documento
es la evidencia versionada de la limpieza.

## Decision operativa

El runtime principal de Telegram sigue siendo OpenClaw nativo.

`lucy_daemon_v2_cloud.py` queda como legacy/fallback y solo debe arrancarse con
fuerza explicita despues de verificar que no haya otro runtime Telegram usando el
mismo bot.

No hace falta instalar `aiohttp` ahora.
