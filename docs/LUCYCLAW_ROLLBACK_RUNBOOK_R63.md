# LucyClaw Rollback Runbook (R63)

## 1. Objetivo
Este runbook establece el procedimiento estandarizado para revertir tramos (tranches) operativos que hayan fallado en el ecosistema LucyClaw / Daemon v3. Su fin es devolver el sistema a un estado conocido y validado ("Safe Harbor") minimizando la intervención manual improvisada.

- **Qué es este runbook**: Una guía técnica de pasos obligatorios para el rollback.
- **Por qué existe**: Para evitar que una falla en un tramo amarillo (mutación) se convierta en una corrupción permanente del sistema.
- **Relación con R59/R60/R61/R62/AG-Y3**: Utiliza el **Run Registry** (R62) y el **Evidence Envelope** (R61) para identificar el **Last Healthy Run** y ejecutar la reversión de las mutaciones autorizadas en R60 y demostradas en AG-Y3.
- **Qué NO autoriza**: No autoriza la reparación automática autónoma sin supervisión ni el acceso a zonas rojas (.env, tokens, n8n internals).

## 2. Principio Central
- **Rollback no es reparación automática**: El rollback busca "deshacer" para volver a la estabilidad, no "arreglar" el error hacia adelante (forward fix) de forma autónoma.
- **Trazabilidad total**: Todo rollback debe generar su propio Evidence Envelope y registro en el Run Registry.
- **Preferencia por Git**: La reversión de código y documentos debe realizarse prioritariamente mediante `git revert` o restauración desde el commit base.
- **Aislamiento**: El rollback nunca debe tocar zonas rojas sin autorización excepcional y ticket específico.

## 3. Cuándo considerar rollback
Se debe evaluar un rollback si, tras ejecutar un tramo:
1. **QA1 falla**: Las capacidades de lectura verde se rompen.
2. **SEC1 falla**: Se detecta una violación de la política de seguridad (ej: leak de secretos, shell:true).
3. **lucy_next_step queda BLOCK**: El oráculo detecta una inconsistencia crítica.
4. **Plugin nuevo rompe la carga**: El gateway de OpenClaw no inicia o rechaza el plugin.
5. **Git status sucio inesperadamente**: Mutaciones fuera del alcance (scope) autorizado.
6. **Runtime inestable**: Errores 500, timeouts o procesos colgantes tras el tramo.
7. **Evidencia inválida**: El Evidence Envelope no pasa la validación de integridad.

## 4. Cuándo NO hacer rollback automático
- Si hay **.env, tokens o secretos** involucrados (requiere limpieza manual experta).
- Si afecta **n8n workflows** o bases de datos internas (riesgo de pérdida de datos).
- Si requiere **sudo** o privilegios de root.
- Si requiere borrar o mover archivos fuera del repositorio `doctora-lucy`.
- Si el operador detecta que el rollback puede empeorar la situación (ej: inconsistencia de estados externos).
- Ante la duda, realizar un **Hard Stop** y pedir intervención de Diego.

## 5. Last Healthy Run
El **Last Healthy Run** es el punto de retorno seguro. Se localiza consultando el Run Registry.

**Regla de Localización**:
Es el registro más reciente en `data/run_registry/lucyclaw_runs.jsonl` que cumple simultáneamente:
- `final_decision == "CLOSED"`
- `qa1_post == "ok"`
- `sec1_post == "ok"`
- `lucy_next_step_post != "BLOCK"`
- `sensitive_clean == true`
- `envelope_validated == true`

El `target_commit` de este registro es el **SHA de Tierra Firme**.

## 6. Tipos de rollback
- **DOCS_ONLY**: Reversión de archivos Markdown. Bajo riesgo.
- **CODE**: Reversión de scripts Python o lógica de negocio. Riesgo medio.
- **PLUGIN**: Eliminación o des-registro de una extensión en `openclaw_plugins/`. Riesgo medio-alto.
- **RUNTIME**: Reversión de cambios en servicios o configuración viva (requiere restart). Riesgo alto.
- **REGISTRY**: Corrección de una entrada fallida en el Run Registry.
- **NEEDS_REVIEW**: Situación compleja que requiere intervención humana.

## 7. Rollback Documental
1. Identificar archivos modificados en el Evidence Envelope del tramo fallido.
2. Inspeccionar diferencias con `git diff`.
3. Si no se ha commiteado: `git restore <file>`.
4. Si se commiteó: `git revert <commit_hash>`.
5. Actualizar el Run Registry con un registro tipo `FAILED_SAFE`.

## 8. Rollback de Código
1. Priorizar `git revert` del commit que introdujo el error.
2. **Prohibido**: `git reset --hard` masivo sin ticket que lo autorice explícitamente (riesgo de pérdida de trabajo paralelo).
3. Ejecutar QA1/SEC1 inmediatamente después de la reversión.
4. Generar un nuevo Evidence Envelope que documente la reversión.

## 9. Rollback de Plugin
1. Si el plugin no carga: revertir el registro en el sistema de plugins y borrar su directorio en `openclaw_plugins/`.
2. Si el gateway falla: detenerse. No intentar reinicios infinitos.
3. Máximo **un (1) restart** autorizado para volver al estado anterior.
4. Validar `/health_brief` post-reversión.

## 10. Rollback de Runtime
1. No se realiza de forma automática en esta fase (R63).
2. Requiere un ticket de "Tramo de Recuperación".
3. Debe seguir el ciclo: Precheck -> Reversión -> Restart (1 vez) -> Postcheck.

## 11. Registro Obligatorio
Todo rollback, por pequeño que sea, debe dejar rastro:
1. **Evidence Envelope**: Documentando por qué se hizo el rollback y qué se revirtió.
2. **Run Registry record**: Con `final_decision: CLOSED` (si el rollback fue exitoso) o `FAILED` (si el sistema sigue roto).
3. **Git status final**: Debe quedar limpio.
4. **Comprobación de Signos Vitales**: QA1 + SEC1 + lucy_next_step.

## 12. Matriz de Decisión (Resumen)

| Síntoma | Nivel | Acción Permitida | Requiere Autorización | Hard Stop |
| :--- | :--- | :--- | :--- | :--- |
| Error tipográfico en MD | Verde | git restore / edit | No (Agrupado) | No |
| Script rompe py_compile | Amarillo | git revert | Sí (Ticket) | Sí |
| Plugin rompe Gateway | Naranja | Borrar plugin + 1 restart | Sí (Ticket) | Sí |
| Se toca .env accidental | Rojo | Informar y BLOQUEAR | Sí (Humana) | **SÍ** |
| SEC1 falla (leak) | Rojo | Informar y BLOQUEAR | Sí (Humana) | **SÍ** |
| QA1 falla post-tramo | Amarillo | Rollback de código | Sí (Ticket) | Sí |

## 13. Protocolo de 10 Fases
1. **DETECT**: Notar la falla en post-checks.
2. **FREEZE**: No realizar más mutaciones hacia adelante.
3. **CLASSIFY**: Determinar el tipo de rollback necesario.
4. **FIND_LAST_HEALTHY**: Identificar el commit estable anterior.
5. **PLAN_ROLLBACK**: Escribir el plan (docs/templates/ROLLBACK_PLAN_TEMPLATE_R63.md).
6. **APPROVE**: Obtener autorización del supervisor/usuario.
7. **APPLY**: Ejecutar los comandos de reversión.
8. **VERIFY**: QA1/SEC1 post-rollback.
9. **RECORD**: Generar Evidence Envelope del rollback.
10. **CLOSE**: Commit y push del estado restaurado.

## 14. Comandos de Inspección Segura
Antes de aplicar, siempre inspeccionar:
- `git status --short --branch`
- `git log -n 5 --oneline`
- `git diff <base_commit> HEAD`
- `python3 scripts/verify_run_registry.py data/run_registry/lucyclaw_runs.jsonl`
- `python3 scripts/lucy_run_registry_command.py`

## 15. Relación con Daemon v3
Daemon v3 usará este runbook como su lógica interna de "Autocuración Pasiva". Ante una falla detectada por su loop de monitoreo, el Daemon generará un **Rollback Plan** basado en este documento y lo presentará para aprobación antes de tocar el sistema.

## 16. Próximos Pasos
- **AG-Y4**: Tramo amarillo que incluya obligatoriamente un plan de rollback preventivo.
- **R64**: Comando `/rollback_plan` read-only para automatizar la generación del plan.
- **R65**: Validador de planes de rollback.
