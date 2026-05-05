# LucyClaw Evidence Envelope / Run Registry (R61)

## 1. Objetivo
- **Qué es un Evidence Envelope**: Es un reporte estructurado y obligatorio que documenta técnicamente cada "tramo" (tranche) operativo ejecutado en el ecosistema LucyClaw.
- **Por qué existe**: Garantiza la trazabilidad y la responsabilidad técnica (accountability). Permite a los supervisores auditar exactamente qué pasó, sin tener que reconstruir la ejecución a partir de logs dispersos o memoria volátil.
- **Relación con R60**: Es la materialización de la fase "REPORT" del protocolo de acciones amarillas. R60 define las reglas de mutación; R61 define cómo se evidencia que esas reglas se cumplieron.
- **Relación con Daemon v3**: Constituye la base de datos de corridas sobre la cual el Daemon futuro tomará decisiones de rollback, escalamiento o continuación de tramos.
- **Qué NO implementa todavía**: En esta fase (R61), el registro es puramente documental (markdown o local) y no incluye una base de datos activa, backend, o sistema de indexación autónomo.

## 2. Principio Central
- **Ningún tramo se considera cerrado sin evidencia**. Si un operador realiza una mutación y no entrega un Evidence Envelope válido, el tramo debe considerarse sospechoso o fallido (needs review).
- La evidencia debe permitir auditar de un vistazo:
  - Qué se pidió originalmente.
  - Quién lo ejecutó (operador).
  - Qué archivos tocó (alcance).
  - Qué comandos exactos corrió en la shell.
  - Qué tests pasaron antes y después (QA1/SEC1).
  - Qué partes del ticket quedaron pendientes.
  - Qué riesgos de seguridad hubo (ej: mutaciones no previstas).

## 3. Tipos de Evidencia
Se clasifica según la naturaleza de la ejecución:
- **GREEN_READONLY**: Diagnóstico o análisis sin mutación (opcional salvo que se exija por ticket).
- **YELLOW_CODE_CHANGE**: Modificaciones de código, documentos o configuración en el repositorio.
- **YELLOW_RUNTIME_ACTION**: Acciones que afectan el estado vivo de la máquina (ej: reinicio de servicios, instalación de dependencias, comandos de infraestructura).
- **DOCS_ONLY**: Tramo limitado estrictamente a escritura/edición de documentación sin impacto funcional.
- **BLOCKED**: Tramo que se detuvo antes de finalizar debido a un *Hard Stop* del protocolo R60.
- **FAILED**: Tramo donde la ejecución de la mutación falló, rompió tests, o no logró el objetivo esperado.
- **REPEATED_AFTER_FIX**: Un intento secundario después de una corrección manual o replanificación tras un bloqueo previo.
- **RECOVERY_AUDIT**: Tramos manuales excepcionales destinados a restaurar el sistema tras una corrupción severa.

## 4. Campos Obligatorios
Todo Evidence Envelope válido debe estructurarse con la siguiente metadata e información:

- `envelope_version`: Versión del estándar (ej: "1.0").
- `tranche_id`: Identificador o ticket asociado (ej: "AG-Y1").
- `tranche_title`: Título corto y descriptivo del objetivo.
- `date`: Fecha de ejecución (formato ISO 8601).
- `operator`: Identidad o tipo de agente ejecutando el tramo (ej: "Antigravity", "Gemini CLI", "Diego").
- `supervisor`: Quién revisa o autorizó (ej: "ChatGPT Supervisor").
- `base_commit`: Commit SHA antes de aplicar las modificaciones.
- `target_commit`: Commit SHA resultante tras la mutación, previo al push, o post-commit.
- `branch`: Rama git sobre la que se operó (ej: "memoria/bunker").
- `repo_path`: Ruta raíz operada (ej: `/home/lucy-ubuntu/Escritorio/doctora-lucy`).
- `risk_level`: Clasificación (GREEN, YELLOW, RED) derivada de `/risk_check`.
- `approval_mode`: Cómo se autorizó (ej: "Grouped Permission", "Explicit user override").
- `ticket_summary`: Resumen de 1-2 líneas del objetivo.
- `allowed_scope`: Archivos, servicios y acciones específicamente permitidas.
- `forbidden_scope`: Límites restrictivos (qué NO tocar en particular para este ticket).
- `files_changed`: Lista de archivos modificados (diffs o nombres).
- `files_created`: Archivos nuevos.
- `files_deleted`: Archivos eliminados.
- `commands_run`: Registro exacto de comandos ejecutados en shell con `run_command` o equivalente.
- `prechecks`: Verificaciones realizadas antes de la ejecución.
- `action_summary`: Breve descripción de los pasos seguidos.
- `postchecks`: Verificaciones realizadas al concluir.
- `qa1_pre`: Resultado pre de `verify_lucyclaw_green_commands.py`.
- `sec1_pre`: Resultado pre de `verify_lucyclaw_security_policy.py`.
- `qa1_post`: Resultado post de `verify_lucyclaw_green_commands.py`.
- `sec1_post`: Resultado post de `verify_lucyclaw_security_policy.py`.
- `lucy_next_step_pre`: Estado de la compuerta antes del tramo.
- `lucy_next_step_post`: Estado de la compuerta después del tramo.
- `git_status_initial`: Estado del repo al arrancar (ej: "Clean").
- `git_status_final`: Estado del repo al cerrar (ej: "Clean", "Dirty with uncommitted changes").
- `runtime_touched`: Booleano que indica si se alteró el estado en tiempo de ejecución (ej: plugins instalados, gateway reiniciado).
- `restart_count`: Número de veces que se reinició un servicio.
- `sensitive_confirmations`: Declaración explícita de no mutación de secretos, memoria, `.env`, etc.
- `voice_report_status`: Si se ejecutó o se suspendió (ej: "Suspendido por ticket").
- `deviations`: Registro de cualquier paso que se desvió del plan original, o anomalías encontradas.
- `rollback_available`: Booleano. Si no es posible un rollback fácil, debe documentarse aquí.
- `final_decision`: Estado final del envelope (CLOSED, BLOCKED, FAILED_SAFE, etc.).
- `next_recommendation`: El paso lógico que sigue después del tramo (ej: R62).

## 5. Campos Prohibidos
Por motivos de seguridad (Hard Security), un Evidence Envelope **nunca** debe incluir o guardar lo siguiente, aunque haya formado parte de la ejecución u output accidental de un comando:
- **Tokens**, contraseñas, API keys (ej: OPENAI_API_KEY).
- Contenido parcial o total del archivo `.env`.
- Secretos expuestos en código base en claro.
- Volcados completos (dumps) de la base de datos de n8n o memoria core (SQLite Bóveda).
- Información de sesión sensible, cookies, o logs crudos no filtrados (sanitizados).

## 6. Estados Finales Permitidos
El campo `final_decision` restringe el resultado a un vocabulario finito:
- **CLOSED**: Tramo operado con éxito, `git status` final limpio, QA1/SEC1 válidos. Se puede proceder.
- **NOT_CLOSED**: Tramo parcialmente operado que carece de resolución final.
- **BLOCKED**: Detenido por un *Hard Stop* de la regla R60, o por un `lucy_next_step` en BLOCK antes/durante.
- **FAILED_SAFE**: El tramo falló en lograr su objetivo pero se detuvo o revirtió de forma segura (repo limpio, sistema sano).
- **NEEDS_REVIEW**: Terminado, pero con anomalías significativas o warnings severos de QA1/SEC1/Salud.
- **REPEAT_REQUIRED**: Fallo técnico o de red que requiere volver a intentar la ejecución en un nuevo tramo.

## 7. Reglas de Validez
Un Evidence Envelope es **VÁLIDO** únicamente si:
- Declara explícitamente el `base_commit`.
- Documenta el `git status` inicial y final.
- Incluye el estado de QA1/SEC1 (cuando el alcance lo requiera, e.g., cambios de código).
- Contiene el resultado del `lucy_next_step` post ejecución.
- Contiene una declaración explícita de si tocó zonas sensibles (sensitive mutations).
- Declara el estado del reporte de voz (ej: ejecutado, o suspendido).
- Declara fehacientemente si tocó componentes de `runtime` o fue puramente documental.
- Declara una `final_decision`.

Un Evidence Envelope es **INVÁLIDO** si:
- Omite el estado de git final.
- No declara las zonas sensibles tocadas/no-tocadas.
- Se marca como "CLOSED" pero QA1 o SEC1 muestran fallos/violaciones post-ejecución.
- Se marca como "CLOSED" pero `lucy_next_step` quedó en BLOCK.
- Falla en documentar desviaciones u omitir comandos crudos críticos.
- Contiene tokens o variables de entorno expuestas (sec leak).

## 8. Run Registry Futuro
En su diseño futuro para la Arquitectura V3, el "Run Registry" (Registro de corridas):
- **Ubicación futura sugerida**: Deberá estar estructurado dentro de `.agents/registry/` o un subdirectorio aislado del código fuente en `data/registry/`.
- **Formato sugerido**: Se recomienda un formato mixto de un archivo JSONL centralizado (índice append-only) y archivos Markdown detallados (un archivo por tramo).
- **Indexación y búsqueda**: El Daemon futuro podrá leer el JSONL para conocer rápidamente el "último tramo sano" consultando `final_decision == CLOSED` y el timestamp, y así saber a qué base commit hacer rollback.
- **Por qué todavía no base de datos**: En la fase actual priorizamos la **auditabilidad documental**. Introducir un gestor de BBDD añadiría complejidad operativa y de infraestructura innecesaria para el nivel de madurez actual del protocolo amarillo.

## 9. Relación con Operadores
- **Antigravity**: Si es el encargado del tramo, DEBE generar el envelope como entregable final (sea en el chat o en un archivo persistente, según instruya el supervisor).
- **Gemini CLI**: Como operador alternativo, está sujeto a la misma obligación de entregar este formato estricto tras cada ejecución.
- **ChatGPT Supervisor**: Se encarga de auditar (revisar) la validez del envelope suministrado, asegurándose que las condiciones de cierre se cumplen estrictamente.
- **Diego (Usuario)**: Autoridad humana que dicta si el tramo (y el envelope) son correctos, aprobando o exigiendo correcciones.

## 10. Relación con Voz (TTS)
- El estado del sistema de voz (si se reportó por audio o no) debe figurar siempre en `voice_report_status`.
- Si el ticket tiene precedencia ("VOZ/TTS SUSPENDIDA"), el envelope debe confirmar: "Suspendido por ticket".
- Si existió reporte vocal, el operador debe testificar en los campos *sensitive_confirmations* si esto implicó escritura temporal en `n8n_data/voice_payload.txt` autorizada.

## 11. Relación con Rollback
- El campo `rollback_available` indica si los cambios pueden deshacerse (típicamente `true` si fue solo documentación o si se comiteó sin side-effects de red).
- Si `rollback_available` es falso, el sobre debe justificar por qué (ej: "Migración destructiva en base de datos externa ejecutada y sin backup provisto").
- Bajo ningún concepto la existencia de un Evidence Envelope autoriza al operador a lanzar un rollback destructivo automático (ej: `rm -rf`) si falla; el rollback debe ser controlado y preferiblemente mediante revert de versionado de código.

## 12. Ejemplo Mínimo (JSON Compacto DOCS-ONLY)
```json
{
  "envelope_version": "1.0",
  "tranche_id": "R61",
  "operator": "Antigravity",
  "base_commit": "fc1fd3f",
  "target_commit": "c4d3e2b",
  "risk_level": "DOCS_ONLY",
  "approval_mode": "Grouped Permission",
  "action_summary": "Creación del estándar Evidence Envelope.",
  "qa1_post": "ok",
  "sec1_post": "ok",
  "lucy_next_step_post": "READY",
  "git_status_final": "Clean",
  "runtime_touched": false,
  "final_decision": "CLOSED"
}
```

## 13. Próximos Pasos
- **R62**: Documentación o script (mínimo, sin BBDD) para guardar localmente en formato JSONL este registro (opcional).
- **AG-Y2**: Primer tramo real amarillo de código. El operador (Antigravity) deberá crear un archivo de Evidence Envelope obligatorio en `docs/examples/` o `data/registry/` para demostrar cumplimiento con el R60/R61.
- **R63**: Runbook de rollbacks documentados.
- **Sucesivos**: Implementación gradual de Daemon v3 de reparación.
