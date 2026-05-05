# LucyClaw Run Registry (R62)

## 1. Objetivo
- **Qué es Run Registry**: Un índice append-only en formato JSONL que registra los metadatos clave de cada tramo operativo ejecutado (Run).
- **Por qué existe**: Actúa como un *ledger* (libro mayor) centralizado. En lugar de escanear el repositorio buscando archivos Markdown de evidencia, el sistema puede leer un único archivo para saber qué tramos ocurrieron, cuándo, y si fueron exitosos.
- **Relación con R59/R60/R61/AG-Y2**:
  - **R59 (Arquitectura)**: Es la base de datos de corridas del futuro Daemon v3.
  - **R60 (Acciones Amarillas)**: Registra los tramos autorizados que mutan código o runtime.
  - **R61 (Evidence Envelope)**: Cada registro del Registry *apunta* a un Envelope detallado.
  - **AG-Y2 (Validador)**: Validó el contenido de los envelopes que ahora son indexados aquí.
- **Qué NO implementa todavía**: No implementa una base de datos real (SQL/NoSQL) ni el Daemon automatizado que lee y escribe estos registros por su cuenta. Sigue siendo mantenido y escrito por el operador (Antigravity).

## 2. Principio Central
- **El registry es un índice, no reemplaza el Evidence Envelope.** El detalle de qué comandos se ejecutaron y qué diferencias de código ocurrieron vive en el Envelope. El Registry solo tiene la metadata direccional.
- Cada línea JSONL apunta a un envelope o documento de evidencia (mediante `evidence_path`).
- El registry permite encontrar rápidamente el **último tramo sano** (Last Healthy Run).

## 3. Formato JSONL Mínimo
Cada línea del archivo `data/run_registry/lucyclaw_runs.jsonl` debe ser un objeto JSON válido.
Campos obligatorios:
- `registry_version`: Versión del esquema (ej: "1.0").
- `run_id`: Identificador único de corrida (ej: "run-AG-Y2-1"). Por simplicidad, puede ser el mismo `tranche_id` si es único.
- `tranche_id`: ID del ticket/tramo (ej: "AG-Y2").
- `title`: Título corto.
- `date`: Fecha ISO 8601.
- `operator`: Agente ejecutante (ej: "Antigravity").
- `risk_level`: Nivel de riesgo (ej: "YELLOW_CODE_CHANGE").
- `final_decision`: Estado de cierre ("CLOSED", "FAILED_SAFE", etc.).
- `base_commit`: SHA de inicio.
- `target_commit`: SHA final tras la mutación.
- `branch`: Rama operada (ej: "memoria/bunker").
- `repo_path`: Ruta del workspace operado.
- `evidence_path`: Ruta relativa al Evidence Envelope en Markdown.
- `envelope_validated`: Booleano, si el envelope pasó la validación de `verify_evidence_envelope.py`.
- `qa1_post`: Resultado ("ok" o "failed").
- `sec1_post`: Resultado ("ok" o "failed").
- `lucy_next_step_post`: Compuerta final ("READY", "WARN", "BLOCK").
- `runtime_touched`: Booleano.
- `restart_count`: Número entero.
- `sensitive_clean`: Booleano que certifica que no se filtraron secretos.
- `voice_report_status`: Estado del TTS.
- `notes`: Notas adicionales opcionales.

## 4. Estados Permitidos (`final_decision`)
- **CLOSED**: El tramo terminó exitosamente, repo limpio, compuertas en verde/amarillo, validado.
- **BLOCKED**: Detenido tempranamente.
- **FAILED_SAFE**: Falló pero sin corromper el sistema.
- **NEEDS_REVIEW**: Terminado con anomalías.
- **REPEAT_REQUIRED**: Error logístico/red, requiere re-intentar en otro run.

## 5. Reglas de Seguridad
- **No guardar secretos** ni en texto claro ni ofuscado.
- **No guardar logs crudos** dentro del JSONL.
- **No guardar contenido de `.env`**.
- **No guardar dumps de n8n** ni volcados de base de datos.
- **No guardar memoria/bóveda** entera.
- **Registry seguro para commit**: El archivo JSONL resultante debe ser 100% seguro para hacer commit y push a un repositorio público/privado sin riesgo de fuga.

## 6. Relación con Evidence Envelope
- El Registry apunta al `evidence_path`.
- El Envelope tiene el detalle fino (diffs, strings de comandos); el registry es solo índice.
- **Invalidez**: Si un envelope no pasa `verify_evidence_envelope.py` (es decir, le faltan campos), el registro en el JSONL **no debe marcar `envelope_validated: true`** y teóricamente no debería marcar `final_decision: CLOSED` si era un requisito estricto.

## 7. Relación con Daemon v3
- El futuro Daemon v3 leerá este JSONL hacia atrás (tail) para encontrar rápidamente la posición estable del sistema antes de aplicar o revertir cambios.
- Por ahora, su mantenimiento es manual/documental ejecutado por el operador.
- No se debe usar el registry actual para inyectar reparación automática *todavía*.

## 8. Regla de Último Tramo Sano (Last Healthy Run)
Se define al **Last Healthy Run** como la línea de registro más reciente (leída desde el final del JSONL hacia arriba) que cumpla **todas** estas condiciones simultáneamente:
1. `final_decision == "CLOSED"`
2. `qa1_post == "ok"`
3. `sec1_post == "ok"`
4. `lucy_next_step_post != "BLOCK"`
5. `sensitive_clean == true`
6. `envelope_validated == true`

El `target_commit` de ese tramo es considerado la "Tierra Firme" (Safe Harbor) para cualquier rollback de emergencia.

## 9. Ejemplo de Línea JSONL
```json
{"registry_version":"1.0","run_id":"AG-Y2","tranche_id":"AG-Y2","title":"Evidence Envelope Validator","date":"2026-05-05T16:35:00Z","operator":"Antigravity","risk_level":"YELLOW_CODE_CHANGE","final_decision":"CLOSED","base_commit":"c1aab87","target_commit":"e3f2c1a","branch":"memoria/bunker","repo_path":"/home/lucy-ubuntu/Escritorio/doctora-lucy","evidence_path":"docs/examples/EVIDENCE_ENVELOPE_EXAMPLE_AG_Y2_VALIDATOR.md","envelope_validated":true,"qa1_post":"ok","sec1_post":"ok","lucy_next_step_post":"WARN","runtime_touched":false,"restart_count":0,"sensitive_clean":true,"voice_report_status":"suspended_by_ticket","notes":""}
```

## 10. Próximos Pasos
- **AG-Y3**: Primer cambio amarillo con plugin (openclaw_plugins), con registro obligatorio en Registry y Evidence Envelope.
- **R63**: Runbook de rollback estandarizado, usando la definición del *Last Healthy Run*.
- **Daemon v3**: Eventual integración del parser del registry dentro de los módulos del Daemon de supervisión.
