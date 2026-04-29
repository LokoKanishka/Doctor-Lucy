# Telegram Native Smoke R22

Fecha: 2026-04-29

## Alcance

- Prueba real minima del canal Telegram nativo de OpenClaw.
- No se ejecuto `lucy_daemon_v2_cloud.py`.
- No se ejecuto `lucy_telegram_listener.py`.
- No se llamo `getUpdates` desde scripts legacy.
- No se reinicio el gateway.
- No se modifico `~/.openclaw`.
- No se tocaron tokens ni `.env`.
- No se instalaron dependencias.

## Preflight

- Rama: `memoria/bunker`.
- HEAD previo: `a65217b docs(lucy): record legacy daemon pid cleanup`.
- Sincronizacion previa con `origin/memoria/bunker`: `0/0`.
- Procesos legacy Telegram/daemon detectados: ninguno.
- `openclaw-gateway.service`: activo, `running`.
- Puerto `18789`: escuchando en loopback.
- `channels.telegram.enabled`: `True`.
- Config Telegram contiene clave tipo token: si, sin imprimir valor.
- Gateway auth mode: `token`.

## Prueba real

Diego envio al bot de Telegram el mensaje exacto:

```text
R22 prueba controlada: responde solo OK
```

Resultado informado por Diego:

- Respuesta recibida: si.
- Latencia aproximada: 2 segundos.
- Texto recibido: `ok`.

Logs relevantes:

- El journal de `openclaw-gateway.service` mostro actividad del agente al momento
  de la prueba con sesion Telegram directa.
- No se observaron procesos legacy activos luego de la prueba.
- `/health` del gateway respondio `200 {"ok":true,"status":"live"}`.

No se imprimieron tokens. No se modifico configuracion. No se reiniciaron servicios.

## Diagnostico

El canal Telegram nativo de OpenClaw queda validado como operativo para una
prueba minima real.

El runtime recomendado sigue siendo:

- Principal: OpenClaw Telegram nativo.
- Legacy/fallback: `lucy_daemon_v2_cloud.py`, solo con fuerza explicita y luego
  de verificar que no haya otro runtime Telegram sobre el mismo bot.

## Proximo paso

Mantener daemons legacy apagados. Para el siguiente tramo, probar una consigna
un poco mas representativa por Telegram nativo, sin activar polling paralelo.
