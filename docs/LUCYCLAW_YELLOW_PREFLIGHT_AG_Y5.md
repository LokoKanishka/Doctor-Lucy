# AG-Y5 — /yellow_preflight

## Objetivo
Crear un comando read-only (`/yellow_preflight`) que evalúe de forma integral si el sistema está en condiciones de iniciar un tramo amarillo (cambio de código, instalación de plugin, etc.).

## Por qué existe
Los tramos amarillos conllevan riesgos de mutación. Antes de iniciar uno, necesitamos asegurar que:
1. El registro de corridas (`Run Registry`) esté íntegro.
2. Exista un punto de restauración (`Last Healthy Run`).
3. El sistema de validación de rollback sea capaz de detectar planes peligrosos.
4. Las pruebas de seguridad (SEC1) y calidad (QA1) pasen.
5. El entorno de trabajo (git) esté limpio.

## Relación con R60-R65
- **R60/R61/R62/R63**: Definieron los protocolos de sobres de evidencia, registro de corridas y runbook de rollback.
- **R64/R65**: Implementaron la generación y validación de planes de rollback.
- **AG-Y4**: Automatizó la validación en QA1.
- **AG-Y5**: Consolida todos estos puntos en un único gate operativo.

## Diseño
El comando es un wrapper Python (`scripts/lucy_yellow_preflight_command.py`) que ejecuta secuencialmente los validadores existentes y emite una decisión:
- **READY**: Todo en orden.
- **WARN**: Problemas no críticos (ej. advertencias de hardware).
- **BLOCK**: Problemas críticos (git sucio, fallas en QA1/SEC1, registro corrupto).

## Checks incluidos
- `git_clean`: `git status` sin cambios pendientes.
- `registry`: `verify_run_registry.py` exitoso.
- `rollback_plan`: `/rollback_plan AG-Y3` genera un plan.
- `rollback_plan_validator`: `verify_rollback_plan.py` valida el plan anterior.
- `sec1`: `verify_lucyclaw_security_policy.py` sin violaciones.
- `qa1`: `verify_lucyclaw_green_commands.py` exitoso.
- `lucy_next_step`: gate de flujo operativo.
- `health`: signos vitales del sistema.

## Seguridad
- Es **read-only**.
- No ejecuta mutaciones ni reparaciones.
- No ejecuta rollback real.
- No accede a zonas rojas (.env, n8n, memoria).

## Qué no hace
- No garantiza que el cambio amarillo sea exitoso.
- No reemplaza la necesidad de un Evidence Envelope para el tramo amarillo.
- Solo verifica la infraestructura de seguridad.

## Próximos pasos
- **AG-Y6**: Primer tramo amarillo real (mutación controlada) precedido obligatoriamente por `/yellow_preflight`.
- **R66**: Integración en el loop de Daemon v3.
