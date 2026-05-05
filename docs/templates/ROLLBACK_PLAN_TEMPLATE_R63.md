# Rollback Plan — <ID>

## 1. Metadata
- **rollback_id**: (ej: RB-R63-001)
- **related_tranche**: (ID del tramo que falló)
- **detected_at**: (Timestamp ISO)
- **operator**: Antigravity
- **supervisor**: ChatGPT / Diego
- **base_commit**: (Commit antes del tramo fallido)
- **bad_commit**: (Commit con el error)
- **last_healthy_run**: (ID del último run CLOSED/OK)
- **last_healthy_commit**: (SHA del último run sano)

## 2. Trigger (Gatillo)
- **symptom**: (Qué falló: QA1, SEC1, Health, etc.)
- **detected_by**: (Agente o script de validación)
- **severity**: (YELLOW / RED)
- **current_lucy_next_step**: (Estado de la compuerta)
- **current_git_status**: (Estado del árbol de trabajo)

## 3. Scope (Alcance de Reversión)
- **files_to_revert**: (Lista de archivos a restaurar/eliminar)
- **plugins_affected**: (Plugins a desinstalar/desactivar)
- **runtime_touched**: (Si requiere reiniciar gateway o servicios)
- **registry_entries_affected**: (Líneas del registry a marcar como FAILED)
- **forbidden_scope**: (Zonas que NO deben tocarse durante el rollback)

## 4. Proposed Action (Acción Propuesta)
- **rollback_type**: (DOCS_ONLY / CODE / PLUGIN / RUNTIME)
- **commands_to_inspect**: (Comandos de validación previa)
- **commands_to_apply**: (Comandos exactos de reversión)
- **restart_required**: (Sí/No)
- **approval_required**: (Sí/No - siempre Sí en fase R63)

## 5. Prechecks (Signos Vitales Actuales)
- **QA1**: (Resultado actual)
- **SEC1**: (Resultado actual)
- **health**: (Estado del gateway)
- **registry**: (Estado del archivo JSONL)
- **evidence**: (Si el envelope fallido existe)

## 6. Apply Plan (Pasos de Ejecución)
1. **Paso 1**: (ej: Revertir commit vía git)
2. **Paso 2**: (ej: Borrar archivos nuevos)
3. **Paso 3**: (ej: Actualizar registry)

## 7. Postchecks (Validación de Restauración)
- **QA1**: (Debe ser OK)
- **SEC1**: (Debe ser OK)
- **lucy_next_step**: (Debe ser READY o WARN)
- **git_status**: (Debe ser Clean)
- **registry_updated**: (Confirmación de nueva entrada)

## 8. Evidence
- **evidence_envelope_path**: (Ruta al nuevo sobre de evidencia del rollback)
- **registry_record_path**: (Ruta al registro del run de recuperación)

## 9. Decision
- **final_decision**: (CLOSED / FAILED)
- **next_recommendation**: (Pasos tras la restauración)
