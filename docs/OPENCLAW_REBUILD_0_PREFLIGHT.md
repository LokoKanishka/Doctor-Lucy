# REBUILD-0 — Preflight perfil paralelo OpenClaw

## 1. Estado actual

Tras el fracaso de la reparación forzada (FORCE-GATE), el sistema se encuentra en un estado estable pero no autorizado (`403 missing scope: operator.read`). 
* **Backup de seguridad**: Confirmado e íntegro en `/home/lucy-ubuntu/OpenClaw_Backups/force_gate/20260429_125405`.
* **Instalación actual**: Reside en `~/.openclaw`. El gateway sigue corriendo con la configuración original.

## 2. Objetivo del perfil paralelo

El objetivo es desplegar una instancia limpia de OpenClaw/LucyClaw sin interferir con la producción actual. Esto permitirá verificar si una base de datos de identidad y tokens nueva resuelve el problema de los scopes.

## 3. Rutas propuestas

* **Raíz de trabajo**: `$HOME/OpenClaw_Parallel`
* **Perfil paralelo**: Se utilizará la opción `--profile rebuild-test`.
* **Ubicación del estado**: El CLI aislará automáticamente el estado en `~/.openclaw-rebuild-test`.

## 4. Restricciones (HARD BLOCK)

Queda prohibido tocar o migrar los siguientes elementos de `~/.openclaw` hasta que el nuevo perfil sea validado:
* **`~/.openclaw/lucy-bridge-token`** (Token corrupto).
* **`~/.openclaw/identity/device-auth.json`** (Identidad corrupta).
* **`~/.openclaw/devices/paired.json`** (Emparejamientos corruptos).
* **`~/.openclaw/openclaw.json`** -> campo `gateway.auth`.

## 5. Opciones técnicas evaluadas

| Opción | Viabilidad | Riesgo | Decisión |
|---|---|---|---|
| **`--profile <name>`** | Alta | Bajo | **RECOMENDADA**. El CLI soporta nativamente el aislamiento de perfiles. |
| **`OPENCLAW_STATE_DIR`** | Media | Bajo | Útil si `--profile` no aísla lo suficiente. |
| **Usuario Linux separado** | Alta | Medio | Plan de fallback si el aislamiento por perfil falla. |
| **Contenedor** | Media | Bajo | Complejo para acceso a periféricos/puertos locales. |

## 6. Próximos pasos (Fase REBUILD-1)

1. Ejecutar el primer arranque con `--profile rebuild-test`.
2. Verificar que la carpeta `~/.openclaw-rebuild-test` se cree correctamente.
3. Validar `/v1/models` con el nuevo Service Token generado.
4. Si el acceso es 200 OK, proceder a la migración selectiva de `auth-profiles.json`.
