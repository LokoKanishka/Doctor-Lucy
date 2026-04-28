# Recuperación de OpenClaw/Clawbot

> [!NOTE]
> **Nota terminológica:** LucyClaw es el nombre funcional de la personalidad/agente Lucy dentro de OpenClaw. El problema de token/scopes es un bloqueo técnico dentro de una arquitectura mayor: LucyClaw debe ser dual-host y API-first, no local-model-first. Ver [LUCYCLAW_ARCHITECTURE.md](file:///home/lucy-ubuntu/Escritorio/doctor%20de%20lucy/docs/LUCYCLAW_ARCHITECTURE.md) para más detalles.

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
**Se requiere intervención de Diego mediante la UI (Dashboard).**
Se intentó rotar tokens por CLI (`openclaw devices rotate`), pero la versión de OpenClaw (v2026.3.28) requiere el uso explícito de un token de dispositivo o de la UI para scopes completos cuando opera en `mode: token`. 

**Pasos a seguir por Diego (Opción B):**
1. Abrir la UI local de OpenClaw en `http://127.0.0.1:18789`
2. Generar un Service Token / Device Token que incluya expresamente los scopes `operator.read` y `operator.write`.
3. Ejecutar en terminal: `python3 scripts/openclaw_install_lucy_token.py`
4. Pegar el token de forma segura (entrada oculta) cuando el script lo solicite.

## Qué NO Tocar
- **No reinstalar OpenClaw** desde internet; el gateway está vivo y el binario existe. El problema es netamente de autorización.
- **No tocar skills** ni el daemon v2 hasta resolver la autenticación del gateway.

## Advertencia de seguridad — tokens expuestos en Tramo 9
- En Tramo 9 hubo exposición accidental de tokens en logs.
- Todo token impreso debe considerarse comprometido.
- No pegar tokens en ChatGPT ni en tickets.
- El Service Token debe ingresarse localmente mediante helper con entrada oculta.
- Luego debe validarse con `/v1/models` y bridge HTTP.
- Si Clawbot tiene UI de revocación, revocar tokens expuestos.

## Instalación segura de Service Token
Con comando:
```bash
python3 scripts/openclaw_install_lucy_token.py
```
Y validación:
```bash
systemctl --user restart openclaw-gateway.service

python3 - <<'PY'
import os, requests
p=os.path.expanduser("~/.openclaw/lucy-bridge-token")
t=open(p).read().strip()
base="http://127.0.0.1:18789"
for ep in ["/health","/v1/models"]:
    headers={"Authorization":f"Bearer {t}"} if ep != "/health" else {}
    r=requests.get(base+ep, headers=headers, timeout=8)
    print(ep, r.status_code, r.text[:500].replace("\n"," "))
PY

OPENCLAW_BRIDGE_MODE=http python3 scripts/lucy_openclaw_bridge.py "ping diagnóstico seguro: respondé solo OK" --agent main
```
