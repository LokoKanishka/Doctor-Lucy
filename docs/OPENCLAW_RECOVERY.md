# Recuperación de OpenClaw/Clawbot

## Causa encontrada
El puente de Lucy a OpenClaw falló de forma combinada por dos problemas independientes:
1. **Fallo de PATH:** El binario CLI `openclaw` no está en el `$PATH` del entorno de ejecución (se encuentra en `~/.npm-global/bin/openclaw`), por lo que el fallback CLI fallaba con `FileNotFoundError`.
2. **Fallo de Token y Scopes:** El gateway HTTP rechaza los tokens disponibles. El token en `~/.openclaw/lucy-bridge-token` recibe `401 Unauthorized`. El token interno de configuración (`~/.openclaw/openclaw.json`) recibe `403 Forbidden` indicando `missing scope: operator.read`.

## Reparación Aplicada
- Se ha detectado la ruta correcta del binario CLI: `~/.npm-global/bin/openclaw`.
- **No se modificó el token** debido a la falta de documentación local segura para regenerarlo sin romper el entorno.

## Qué Backup se hizo
No se modificaron archivos críticos, por lo que no fue necesario rotar backups en este tramo de diagnóstico.

## Cómo Validar
Cuando se repare el token, se podrá validar la ejecución forzando el binario correcto:
```bash
OPENCLAW_BIN=~/.npm-global/bin/openclaw OPENCLAW_BRIDGE_MODE=http python3 scripts/lucy_openclaw_bridge.py "ping"
```

## Qué NO Tocar
- **No reinstalar OpenClaw** desde internet; el gateway está vivo y el binario existe. El problema es netamente de autorización.
- **No tocar skills** ni el daemon v2 hasta resolver la autenticación del gateway.

## Relación con Auditoría Anterior
La auditoría `diagnostics/openclaw_audit_20260426.md` mencionaba un token exitoso con scopes de `operator.read` y `operator.write`. La situación actual indica que dicho token fue revocado o sobrescrito en `lucy-bridge-token`, perdiendo el acceso al gateway activo.
