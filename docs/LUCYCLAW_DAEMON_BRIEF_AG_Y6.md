# AG-Y6 — /daemon_brief

## Objetivo
Crear un comando read-only (`/daemon_brief`) que resuma el estado de preparación de Daemon v3 sin ejecutar ninguna acción.

## Por qué existe
El ecosistema LucyClaw ha construido incrementalmente una pila de seguridad completa (R59-R65, AG-Y4, AG-Y5). Antes de activar Daemon v3 como loop autónomo, necesitamos una vista compacta que confirme:
1. Que toda la infraestructura de seguridad está disponible.
2. Que Daemon v3 **no** está activo.
3. Que la reparación automática **no** está habilitada.
4. Cuál es el último tramo sano registrado.
5. Si el sistema está listo para un tramo amarillo controlado.

## Relación con Daemon v3
- **R59** diseñó la arquitectura de Daemon v3.
- `/daemon_brief` NO activa Daemon v3.
- `/daemon_brief` solo reporta el estado de preparación.
- Daemon v3 activo requiere un tramo futuro específico con autorización explícita.

## Relación con R59-R65 / AG-Y5
- **R60**: Protocolo amarillo — `/daemon_brief` confirma que el protocolo existe.
- **R61**: Evidence Envelope — `/daemon_brief` confirma disponibilidad.
- **R62**: Run Registry — `/daemon_brief` lee el registro para encontrar el último tramo sano.
- **R63**: Rollback Runbook — `/daemon_brief` confirma disponibilidad.
- **R64**: `/rollback_plan` — `/daemon_brief` confirma disponibilidad.
- **R65**: `verify_rollback_plan.py` — `/daemon_brief` confirma disponibilidad.
- **AG-Y5**: `/yellow_preflight` — `/daemon_brief` ejecuta el preflight y reporta su decisión.

## Diseño
El comando es un wrapper Python (`scripts/lucy_daemon_brief_command.py`) que:
1. Valida el Run Registry.
2. Ejecuta `/run_registry`, `/yellow_preflight` y `/lucy_next_step`.
3. Lee el último tramo sano del registro local.
4. Consolida todo en un JSON determinístico.

## Seguridad
- Es **read-only**.
- No ejecuta mutaciones ni reparaciones.
- No activa Daemon v3.
- No ejecuta rollback real.
- No accede a zonas rojas (.env, n8n, memoria).
- No crea procesos persistentes.
- No usa shell=True.
- No acepta argumentos.

## Qué no hace
- No activa el loop de Daemon v3.
- No habilita reparación automática.
- No ejecuta rollback.
- No muta el estado del sistema.
- No reemplaza `/yellow_preflight` (lo complementa).

## Relación con /yellow_preflight
- `/yellow_preflight` evalúa si es seguro iniciar un tramo amarillo.
- `/daemon_brief` resume el estado general de preparación de Daemon v3.
- `/daemon_brief` incluye el resultado de `/yellow_preflight` en su reporte.

## Relación con /run_registry
- `/daemon_brief` lee el registro para obtener el último tramo sano.
- No modifica el registro.

## Relación con /rollback_plan
- `/daemon_brief` confirma que la herramienta de rollback está disponible.
- No genera ni ejecuta planes de rollback.

## Próximos pasos
1. **R66**: Daemon loop conceptual documentado (diseño del loop sin ejecución).
2. **AG-Y7**: Primer tramo amarillo usando `/yellow_preflight` + `/daemon_brief` como precondición.
3. No reparación automática todavía.
