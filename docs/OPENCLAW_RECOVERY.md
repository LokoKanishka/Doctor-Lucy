# Recuperación de OpenClaw/Clawbot

## Causa encontrada
El puente de Lucy a OpenClaw falló de forma combinada por dos problemas independientes:
1. **Fallo de PATH:** El binario CLI `openclaw` no está en el `$PATH` del entorno de ejecución (se encuentra en `~/.npm-global/bin/openclaw`), por lo que el fallback CLI fallaba con `FileNotFoundError`.
2. **Fallo de Token y Scopes:** El gateway HTTP rechaza los tokens disponibles. El token en `~/.openclaw/lucy-bridge-token` recibe `401 Unauthorized`. El token interno de configuración (`~/.openclaw/openclaw.json`) recibe `403 Forbidden` indicando `missing scope: operator.read`.

## Reparación Aplicada
- Se ha detectado la ruta correcta del binario CLI: `~/.npm-global/bin/openclaw`.
- **Intento de regeneración de Token:** Se intentó rotar el token de acceso para el rol de `operator` con los permisos `operator.read` y `operator.write` mediante el comando `~/.openclaw/lib/node_modules/openclaw/openclaw.mjs devices rotate`, pero los nuevos tokens emitidos siguen careciendo de los scopes adecuados (`403 Forbidden: missing scope: operator.read`). El sistema local parece no permitir agregar scopes superiores mediante el CLI de esta versión (v2026.3.28).
- **Restauración:** Se restauró la configuración de `openclaw.json` y `lucy-bridge-token` a su estado original previo al intento de reparación para no causar problemas secundarios.

## Qué Backup se hizo
Se realizaron backups previos a cualquier modificación:
- `~/.openclaw/backups-tramo9/openclaw.json.pre-token-repair-*.bak`
- `~/.openclaw/backups-tramo9/lucy-bridge-token.pre-token-repair-*.bak`

## Cómo Validar
Cuando se repare el token, se podrá validar la ejecución forzando el binario correcto:
```bash
OPENCLAW_BIN=~/.npm-global/bin/openclaw OPENCLAW_BRIDGE_MODE=http python3 scripts/lucy_openclaw_bridge.py "ping"
```

## Próximos Pasos (Bloqueado)
**Se necesita la intervención directa de Diego.** No se encontró un comando o ruta en la CLI local que otorgue exitosamente un Service Token con los permisos de lectura y escritura reales, o existe un mecanismo de autorización no documentado/GUI para esto.

## Qué NO Tocar
- **No reinstalar OpenClaw** desde internet; el gateway está vivo y el binario existe. El problema es netamente de autorización.
- **No tocar skills** ni el daemon v2 hasta resolver la autenticación del gateway.
