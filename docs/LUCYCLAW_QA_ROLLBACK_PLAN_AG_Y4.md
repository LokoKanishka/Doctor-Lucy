# AG-Y4 — Integrar verify_rollback_plan en QA1

## Objetivo
Integrar la herramienta de validación de planes de rollback (`scripts/verify_rollback_plan.py`) dentro del conjunto de pruebas de humo automatizadas (QA1).

## Por qué integrar verify_rollback_plan en QA1
La seguridad de las operaciones de rollback es crítica. Integrar este validador en QA1 garantiza que:
1. El script validador (`scripts/verify_rollback_plan.py`) esté presente y operativo.
2. Los planes de rollback generados por el sistema sigan cumpliendo con las políticas de seguridad.
3. Se detecten regresiones que puedan permitir comandos peligrosos en un plan de rollback antes de que este se intente ejecutar.

## Qué valida
- Existencia del script `scripts/verify_rollback_plan.py`.
- Existencia de un plan de ejemplo válido `docs/examples/ROLLBACK_PLAN_EXAMPLE_AG_Y3_R65.json`.
- Que la ejecución del validador sobre el ejemplo devuelva `ok: true`.
- Que la decisión sea `VALID`.
- Que no se detecten `dangerous_hits`.

## Qué no valida
- No ejecuta el rollback real.
- No valida la efectividad del rollback en el runtime (es una validación estática/lógica).
- No genera planes nuevos durante la ejecución de QA1.

## Relación con R63/R64/R65
- **R63**: Definió el Runbook de Rollback.
- **R64**: Implementó `/rollback_plan` como comando read-only.
- **R65**: Creó el script `verify_rollback_plan.py`.
- **AG-Y4**: Automatiza la verificación de este ciclo en QA1.

## Seguridad
- El chequeo es read-only.
- No toca el runtime ni reinicia servicios.
- Se basa en un archivo JSON de ejemplo ya auditado.

## Salida esperada en QA1
```json
{
  "command": "rollback_plan_validator",
  "status": "ok"
}
```

## Criterios de aceptación
- QA1 pasa completamente incluyendo el nuevo check.
- `scripts/verify_lucyclaw_green_commands.py` no tiene errores de sintaxis.
- El registro de corridas (registry) y el sobre de evidencia (envelope) son válidos.

## Rollback
En caso de falla en QA1 por este check, se debe revisar si el plan de ejemplo ha sido corrompido o si las reglas de validación en `scripts/verify_rollback_plan.py` se han vuelto demasiado estrictas/erróneas.

## Próximos pasos
1. Implementar `/yellow_preflight` (AG-Y5 o R66).
2. Avanzar hacia el loop conceptual de Daemon v3.
