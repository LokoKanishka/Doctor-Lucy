# Ejemplo Hipotético de Rollback — AG-Y3 (R63)

## Escenario
Supongamos que tras instalar el plugin `lucy-run-registry-command` en el tramo **AG-Y3**, el gateway de OpenClaw deja de responder o entra en un ciclo de reinicio debido a un error en `index.js`.

## 1. Detección
- El operador corre `curl http://127.0.0.1:18789/health` y recibe Connection Refused.
- `python3 scripts/verify_lucyclaw_green_commands.py` (QA1) falla porque no puede conectar con el gateway.
- `lucy_next_step` devuelve `BLOCK` debido a `gateway: down`.

## 2. Identificación del Last Healthy Run
El operador consulta `data/run_registry/lucyclaw_runs.jsonl` (o mediante `/run_registry` si funcionara parcialmente) y encuentra:
- El tramo previo sano fue **AG-Y2**.
- `last_healthy_commit`: `e3f2c1a` (el commit antes de empezar AG-Y3).
- `base_commit` de AG-Y3: `502f5ed`.

## 3. Plan de Rollback (Conceptual)
Para volver a la estabilidad de AG-Y2:

### Alcance
- **Revertir commit**: El commit `b306602` (el generado en AG-Y3).
- **Plugins**: Eliminar `openclaw_plugins/lucy-run-registry-command/`.
- **Runtime**: Realizar un (1) reinicio del gateway tras la limpieza.

### Comandos Aplicables (Hipotéticos)
1. `git revert b306602 --no-edit`
2. `rm -rf openclaw_plugins/lucy-run-registry-command/` (si el revert no lo borró)
3. `systemctl --user restart openclaw-gateway.service`
4. `curl ... /health` (validación)

## 4. Registro del Fallo
Se debe añadir una línea al Run Registry para cerrar el tramo AG-Y3 como fallido:
```json
{
  "run_id": "AG-Y3-FAIL",
  "tranche_id": "AG-Y3",
  "final_decision": "FAILED_SAFE",
  "notes": "Plugin caused gateway crash. Rollback to AG-Y2 executed."
}
```

## 5. Por qué no se ejecuta ahora
Este documento es un **ejemplo de diseño**. AG-Y3 fue exitoso en la realidad. Este runbook sirve para entrenar al Daemon v3 y al operador en cómo reaccionar ante fallas futuras.

## 6. Próximo paso tras un Rollback real
Una vez restaurado el sistema a la "Tierra Firme" del commit base, se debe:
1. Analizar el error en un ambiente de scratch aislado.
2. Corregir el código.
3. Iniciar un tramo nuevo (ej: `AG-Y3-RETRY`) con el fix.
