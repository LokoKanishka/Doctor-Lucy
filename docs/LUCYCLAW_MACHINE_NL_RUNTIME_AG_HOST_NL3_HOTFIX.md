# LucyClaw Machine NL Runtime Hotfix (AG-HOST-NL3-HOTFIX)

Date: 2026-05-06

## What Failed

El patch runtime de AG-HOST-NL3 rompió el camino completo de mensajes Telegram, incluyendo mensajes no relacionados con máquina.

Error encontrado en logs:
- `ReferenceError: spawnSync is not defined`
- origen: runtime externo en `reply-DeXK9BLT.js`
- síntoma visible: `Something went wrong while processing your message.`

## Decision

Se eligió rollback seguro del runtime externo, no fix mínimo in-place.

Razón:
- el fallo afectaba tanto consultas naturales de máquina como conversación normal
- el backup ya existía
- la prioridad del ticket era restaurar conversación normal y preservar `/machine_*`

## Runtime Action

Archivo runtime restaurado:
- `/home/lucy-ubuntu/.npm-global/lib/node_modules/openclaw/dist/reply-DeXK9BLT.js`

Backup usado:
- `/home/lucy-ubuntu/.openclaw/backups/AG_HOST_NL3/reply-DeXK9BLT.js.bak`

Acción aplicada:
```bash
cp -p /home/lucy-ubuntu/.openclaw/backups/AG_HOST_NL3/reply-DeXK9BLT.js.bak /home/lucy-ubuntu/.npm-global/lib/node_modules/openclaw/dist/reply-DeXK9BLT.js
systemctl --user restart openclaw-gateway.service
```

## Final State

- gateway: vivo
- NL natural de AG-HOST-NL3: desactivado
- conversación normal: restaurada a nivel runtime
- comandos directos `/machine_*`: preservados

## Verification

Validado localmente:
- `curl http://127.0.0.1:18789/health` -> `live`
- `python3 scripts/lucy_machine_access_command.py downloads` -> `ok:true`
- `python3 scripts/lucy_machine_status_command.py status` -> `ok:true`
- `python3 scripts/verify_lucyclaw_security_policy.py` -> ok
- `python3 scripts/verify_run_registry.py data/run_registry/lucyclaw_runs.jsonl` -> valid

Pendiente operador:
- `hola cómo estás` por Telegram debe volver a responder conversacionalmente
- `/machine_downloads` debe seguir funcionando
- `/machine_status` debe seguir funcionando
