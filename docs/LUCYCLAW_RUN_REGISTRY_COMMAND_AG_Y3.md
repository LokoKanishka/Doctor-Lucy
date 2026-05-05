# LucyClaw Run Registry Command (AG-Y3)

## 1. Objetivo
El objetivo de este tramo es exponer el Run Registry (creado en R62) a través de un comando seguro (`/run_registry`) dentro del ecosistema LucyClaw, permitiendo a los operadores e interfaces consultar el estado del registro de corridas sin acceder directamente al sistema de archivos ni vulnerar las políticas de seguridad.

## 2. Por qué es el primer plugin real bajo R60/R61/R62
- **R60 (Protocolo Amarillo)**: Este es el primer tramo que aplica las reglas completas de mutación (cambio de código) bajo la autorización agrupada.
- **R61 (Evidence Envelope)**: Se genera un sobre de evidencia estructurado demostrando cada paso.
- **R62 (Run Registry)**: Se registra la operación en el propio registry que este comando está exponiendo, creando el primer ciclo cerrado de operación y registro.

## 3. Diseño
El comando se implementa usando la arquitectura estándar de LucyClaw:
1. **Wrapper Python (`scripts/lucy_run_registry_command.py`)**: Script sin dependencias externas que lee de forma segura el archivo `lucyclaw_runs.jsonl` y extrae estadísticas clave (total de registros, válidos, y el Last Healthy Run).
2. **Plugin OpenClaw (`openclaw_plugins/lucy-run-registry-command/`)**: Extensión JS/Node.js que envuelve el wrapper, lo ejecuta vía `spawn` (sin shell), y expone la ruta al gateway.

## 4. Salida JSON
La salida es un JSON estructurado y determinístico:
```json
{
  "ok": true,
  "command": "run_registry",
  "stage": "AG-Y3",
  "registry": {
    "path": "data/run_registry/lucyclaw_runs.jsonl",
    "total_records": 5,
    "valid_records": 5,
    "last_healthy_run": {
      "run_id": "...",
      "tranche_id": "...",
      "target_commit": "...",
      "risk_level": "...",
      "final_decision": "CLOSED"
    }
  },
  "status": {
    "read_only": true,
    "runtime_touched": false,
    "sensitive_paths_excluded": true
  },
  "next": "Usar /lucy_next_step antes de iniciar un tramo amarillo."
}
```

## 5. Seguridad
- El wrapper Python no acepta argumentos, preveniendo inyecciones.
- El plugin OpenClaw usa `spawn` con `shell: false`.
- La lectura es estrictamente sobre `data/run_registry/lucyclaw_runs.jsonl`.
- No hay impresión de contenido sensible (como `.env`, `n8n_data`, etc.).

## 6. Qué NO hace
- No repara registros corruptos.
- No escribe ni muta el Registry.
- No realiza operaciones en el Daemon v3 activo.

## 7. Relación con Run Registry
Este comando convierte el Run Registry estático de R62 en una interfaz viva consultable en tiempo de ejecución. Permite saber rápidamente cuál es el último estado seguro para rollback.

## 8. Relación con Daemon v3
El Daemon v3 utilizará `/run_registry` (o su equivalente lógico) como primer paso en su loop de control para orientarse sobre la historia operativa del sistema antes de tomar decisiones de reparación.

## 9. Tests
- Validación del script con `py_compile`.
- Validación del plugin Node con `node --check`.
- Ejecución de `verify_lucyclaw_green_commands.py` (QA1) incluyendo el nuevo test local.
- Ejecución de `verify_lucyclaw_security_policy.py` (SEC1).

## 10. Rollback
El rollback consiste en revertir los commits asociados a este tramo, eliminar el directorio `openclaw_plugins/lucy-run-registry-command/`, remover las entradas del registry y reiniciar el gateway.

## 11. Próximos pasos
- **R63**: Diseño del Runbook de rollback estandarizado usando el Last Healthy Run.
- **AG-Y4**: Ejecución de un comando o tramo de mayor complejidad y nivel de mutación.
