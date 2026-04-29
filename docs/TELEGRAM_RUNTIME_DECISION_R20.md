# Telegram Runtime Decision R20

Fecha: 2026-04-29

## Alcance

- No se envio Telegram real.
- No se ejecuto `main()` de `lucy_daemon_v2_cloud.py`.
- No se llamo `getUpdates`.
- No se reiniciaron servicios.
- No se modifico configuracion.
- No se instalaron dependencias.
- No se imprimieron tokens ni secretos.

## Evidencia

Documentos revisados:

- `docs/ARCHITECTURE.md`
- `docs/OPENCLAW_INTEGRATION_SMOKE.md`
- `docs/LUCY_DAEMON_V2_DRY_RUN.md`

Configuracion segura de OpenClaw:

- `~/.openclaw/openclaw.json` existe.
- `channels.telegram.enabled`: `True`.
- `channels.telegram.botToken`: presente, redactado.
- Politica DM: `pairing`.
- Politica grupos: `allowlist`.
- Historial Telegram: `4`.
- Streaming Telegram: `partial`.
- Gateway presente: si.
- Gateway mode: `local`.
- Gateway auth mode: `token`; token presente, redactado.
- Agent `main`: existe como entrada por `id`.
- Modelo default primario: `ollama/qwen2.5-coder:14b`.
- Agent `fusion-research`: `google/gemini-2.5-flash`.

Runtime observado:

- `openclaw-gateway.service`: activo, `running`, PID `29940`.
- Proceso `openclaw-gateway`: activo.
- `lucy_daemon_v2_cloud.py`: sin proceso vivo detectado.
- `lucy_telegram_listener.py`: sin proceso vivo detectado.
- `n8n_data/daemon.pid`: existe, pero el PID registrado no corresponde a un proceso vivo.

## Decision

El camino operativo principal recomendado es Telegram nativo de OpenClaw.

Motivos:

- OpenClaw ya tiene `channels.telegram.enabled=True`.
- El gateway OpenClaw esta activo como servicio de usuario.
- `lucy_daemon_v2_cloud.py` ya contiene una guarda para no arrancar si OpenClaw maneja Telegram nativamente.
- R19 confirmo que `lucy_daemon_v2_cloud.py` carga `.env`, detecta `DIEGO_TELEGRAM_ID`, usa `delegate_mission` y responde con `telegram_send` mockeado.
- Mantener ambos runtimes escuchando el mismo bot elevaria el riesgo de doble polling y conflictos `getUpdates`.

## Politica recomendada

- Principal: OpenClaw Telegram nativo.
- Legacy/fallback: `lucy_daemon_v2_cloud.py` solo con fuerza explicita, por ejemplo `LUCY_DAEMON_FORCE_TELEGRAM=1`, y nunca junto con otro runtime de Telegram sobre el mismo bot.
- Dependencia `aiohttp`: no instalar ni resolver ahora; posponer hasta que se decida usar el daemon legacy en runtime real.

## Proximo paso

Hacer una prueba controlada del camino nativo OpenClaw Telegram cuando Diego autorice envio real, verificando antes que no haya ningun listener/daemon legacy activo sobre el mismo bot.
