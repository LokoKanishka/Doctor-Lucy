# LucyClaw Rollback Plan Command (R64)

## 1. Objetivo
El comando `/rollback_plan` permite generar planes de reversión seguros y estandarizados a partir del historial registrado en el **Run Registry** (R62) y siguiendo las directrices del **Rollback Runbook** (R63).

- **Qué hace**: Consulta el registro para proponer inspecciones y pasos de rollback.
- **Qué NO hace**: No ejecuta ninguna mutación (git revert, git reset, rm) de forma automática. Es un comando de **Solo Lectura (Read-Only)**.
- **Por qué existe**: Para convertir el runbook documental (R63) en una herramienta operativa que el Daemon v3 pueda usar para proponer autocuración.

## 2. Diseño y Seguridad
- **Capa Verde**: Es un comando read-only.
- **Sanitización**: Los argumentos (`tranche_id`, `run_id`, `commit`) son sanitizados estrictamente.
- **Sin Efectos Secundarios**: No invoca a Git ni toca el runtime.
- **Aislamiento**: No lee .env ni zonas sensibles.

## 3. Uso y Argumentos

### `/rollback_plan` (Sin argumentos)
Genera un plan genérico basado en el **Last Healthy Run** detectado en el registry.

### `/rollback_plan <target>`
Busca un tramo específico (ej: `AG-Y3`, `R63`) o un commit hash en el registry y genera un plan de reversión para ese punto.

## 4. Estructura de Salida (JSON)

### Éxito (latest)
```json
{
  "ok": true,
  "command": "rollback_plan",
  "target": "latest",
  "last_healthy_run": {
    "run_id": "R63",
    "target_commit": "6810a99",
    "risk_level": "DOCS_ONLY"
  },
  "plan": {
    "decision": "PLAN_ONLY",
    "rollback_allowed_now": false,
    "requires_approval": true,
    "suggested_rollback_type": "INSPECTION_ONLY",
    "safe_inspection_commands": [...]
  }
}
```

### Fallo (target inexistente)
```json
{
  "ok": false,
  "command": "rollback_plan",
  "error": "target not found in registry",
  "decision": "NEEDS_REVIEW"
}
```

## 5. Criterios de Selección (Safe Harbor)
El comando identifica el **Safe Harbor** buscando el registro más reciente que cumpla:
- `final_decision == "CLOSED"`
- `qa1_post == "ok"`
- `sec1_post == "ok"`
- `lucy_next_step_post != "BLOCK"`
- `sensitive_clean == true`
- `envelope_validated == true`

## 6. Próximos Pasos
- **R65**: Validador de planes de rollback generados por este comando.
- **Daemon v3 Loop**: Integración de `/rollback_plan` en el ciclo de monitoreo continuo para proponer correcciones ante fallos de QA1.
