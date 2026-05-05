# LucyClaw Yellow Actions Protocol (R60)

## 1. Objetivo del Protocolo
Este protocolo regula la ejecución de **acciones amarillas** (mutaciones controladas) en el ecosistema LucyClaw/Daemon v3. Su existencia garantiza que cualquier cambio en el código, configuración o estado de los servicios se realice bajo un marco de seguridad auditable, minimizando el riesgo de regresiones o compromisos de seguridad.

- **Relación con Daemon v3**: Es el conjunto de reglas operativas que el Daemon v3 debe obedecer y validar.
- **Sin reparación automática**: No habilita la reparación autónoma sin supervisión; prioriza el diagnóstico y la aprobación humana.

## 2. Definición de Acción Amarilla
Son acciones que modifican el estado del repositorio o de los servicios autorizados, pero que no comprometen zonas sensibles (rojas).
Ejemplos:
- Editar código fuente del repositorio (`scripts/`, `docs/`, etc.).
- Crear o modificar plugins de LucyClaw en `openclaw_plugins/`.
- Instalar un plugin específico autorizado.
- Reiniciar el gateway de OpenClaw (máximo una vez por tramo).
- Realizar operaciones de `git commit` y `git push`.
- Modificar archivos de configuración no sensibles.
- Preparar y ejecutar rollbacks documentales o de código acotados.

## 3. Acciones que NO son Amarillas (Rojo/Prohibido)
Cualquier acción en esta categoría está estrictamente prohibida salvo autorización excepcional:
- Acceso o modificación de archivos `.env`.
- Exposición o manejo de tokens, llaves API o credenciales.
- Edición de la memoria core o la bóveda SQLite.
- Acceso a workflows o base de datos interna de n8n.
- Modificación de la personalidad o directivas base del agente.
- Uso del comando `sudo` o escalada de privilegios.
- Ejecución de shell libre destructiva (`rm -rf /`, etc.).
- Borrado o movimiento masivo de archivos fuera del alcance del ticket.
- Reparación automática sin plan técnico aprobado.
- Cambios en archivos fuera del repositorio canónico (`doctora-lucy`).

## 4. Precondiciones Obligatorias
Antes de iniciar cualquier acción amarilla, se debe validar:
1. **Entorno**: Repo canónico, rama `memoria/bunker` y remote correctos.
2. **Estado Git**: Status limpio (salvo suciedad declarada del tramo) y base commit identificado.
3. **Análisis**: Riesgo clasificado (`/risk_check`) y permisos calculados (`/permission_brief`).
4. **Plan**: Contrato técnico generado (`/change_plan`) o ticket explícito aprobado.
5. **Compuerta**: `/lucy_next_step` debe devolver `READY` o `WARN` (nunca `BLOCK`).
6. **Validación Pre**: Ejecución exitosa de **SEC1** y **QA1** inicial.
7. **Alcance**: Lista explícita de archivos a intervenir.
8. **Rollback**: Definición conceptual de cómo revertir los cambios si fallan los post-checks.

## 5. Permiso Agrupado
El permiso agrupado (Grouped Permission) se otorga mediante un ticket explícito y permite al operador:
- Modificar los archivos listados en el alcance.
- Instalar/registrar los plugins indicados.
- Realizar un (1) reinicio del gateway para aplicar cambios.
- Ejecutar el flujo de commit y push tras validación exitosa.
- **Límite**: El permiso expira al cerrar el ticket o al encontrar un **Hard Stop**.

## 6. Hard Stops Obligatorios (Parada de Emergencia)
El operador DEBE detenerse y pedir intervención humana si:
- El repositorio, rama o remote no coinciden con lo esperado.
- Se detectan archivos inesperados o modificados fuera del alcance.
- Falla cualquier validación de **QA1** o **SEC1** (pre o post).
- `/lucy_next_step` se encuentra en estado `BLOCK`.
- Se requiere `sudo` o acceso a zonas rojas (`.env`, n8n, memoria).
- Se necesita más de un reinicio del gateway.
- El proceso de `git push` falla por conflictos de red o permisos.
- Se detecta el uso de rutas legacy activas en lugar de las canónicas.

## 7. Fases de Ejecución Amarilla
| Fase | Acción Permitida | Salida Esperada |
| :--- | :--- | :--- |
| **INTAKE** | Lectura de ticket y contexto. | Requisitos claros. |
| **CLASSIFY** | `/risk_check` y `/permission_brief`. | Riesgo identificado. |
| **PLAN** | `/change_plan`. | Contrato técnico. |
| **PRECHECK** | QA1 / SEC1 / `lucy_next_step`. | Luz verde operativa. |
| **EXECUTE** | Edición de archivos / Registro de plugins. | Cambios realizados. |
| **VERIFY** | QA1 / SEC1 / Smoke test. | Validación de éxito. |
| **REPORT** | Generación de Evidence Envelope. | Reporte auditable. |
| **CLOSE** | `git commit` y `git push`. | Repositorio actualizado. |
| **BLOCKED** | Ninguna (solo lectura de diagnóstico). | Ticket en pausa. |

## 8. Matriz de Permisos
| Acción | Nivel | Requiere Permiso | QA1/SEC1 | Rollback | Agrupado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Editar Documentación | GREEN/YELLOW | Sí (agrupado) | Sí | Sí (Git) | Sí |
| Editar Script Operativo | YELLOW | Sí (explícito) | Sí | Sí (Git) | Sí |
| Crear/Modificar Plugin | YELLOW | Sí (agrupado) | Sí | Sí (Doc) | Sí |
| Instalar Plugin Lucy | YELLOW | Sí (agrupado) | Sí | Sí (Reg) | Sí |
| Restart Gateway | YELLOW | Sí (1 vez) | Sí | N/A | Sí |
| Commit / Push | YELLOW | Sí (agrupado) | Sí | N/A | Sí |
| Leer Logs Sanitizados | GREEN | No | No | N/A | Sí |
| Tocar `.env` / Secretos | RED | PROHIBIDO | N/A | N/A | No |
| Tocar n8n Workflows | RED | PROHIBIDO | N/A | N/A | No |
| Usar `sudo` | RED | PROHIBIDO | N/A | N/A | No |

## 9. Gates Técnicos (Compuertas)
- **SEC1 (Security Policy)**: Obligatorio antes y después de cada tramo para asegurar que no se introdujeron vulnerabilidades (ej. `shell:true`).
- **QA1 (Green Commands)**: Obligatorio antes y después para asegurar que las capacidades de lectura no se rompieron.
- **Git Hygiene**: El tramo no se considera cerrado si `git status` no queda limpio.
- **Integridad**: No se permite el cierre si hubo mutación accidental en zonas sensibles.

## 10. Evidence Envelope (Sobre de Evidencia)
Cada reporte de acción amarilla debe incluir:
- `tranche_id`: ID del ticket.
- `operator`: Agente responsable (Antigravity/GeminiCLI).
- `base_commit`: SHA antes de los cambios.
- `target_commit`: SHA después del push.
- `risk`: Clasificación de riesgo operada.
- `files_changed`: Lista de archivos modificados.
- `commands_run`: Registro de comandos de terminal usados.
- `prechecks / postchecks`: Resultado de QA1/SEC1.
- `voice_report_status`: Si se emitió o no reporte vocal.
- `final_decision`: Éxito, Fallo o Bloqueo.

## 11. Política de Rollback
- **Documental/Código**: Se realiza mediante `git revert` o restauración de archivo desde commit base.
- **Plugin**: Des-registro o borrado del directorio del plugin en `openclaw_plugins/`.
- **Prohibición**: No se permite rollback automático destructivo (ej. `rm -rf`) en zonas no listadas.
- **Regla**: Ante la duda, detener el Daemon y solicitar intervención manual de Diego.

## 12. Relación con Operadores
- **Antigravity**: Operador inteligente primario para tramos amarillos complejos.
- **Gemini CLI**: Operador para tramos amarillos mecánicos o de sincronización masiva.
- **Supervisor**: Auditor que valida el Evidence Envelope.
- **Diego**: Única autoridad para autorizar tramos RED o excepciones de seguridad.

## 13. Relación con Voz (TTS)
- La voz está permitida para el reporte final si el ticket no la prohíbe.
- **Suspensión**: Si el ticket prohíbe tocar `n8n_data`, la voz queda automáticamente suspendida (ya que requiere escritura de payload en dicha carpeta).

## 14. Relación con Daemon v3
R60 es el contrato que rige el comportamiento del Daemon v3. Ninguna instancia del Daemon puede realizar una mutación si no puede cumplir con los pasos de este protocolo.

## 15. Ejemplo de Acción Amarilla Válida
1. Request: "Crear comando /hello_world".
2. `/risk_check` -> YELLOW.
3. `/permission_brief` -> Agrupado (edit + register + commit).
4. `/change_plan` -> Crea plugin en `openclaw_plugins/`.
5. QA1/SEC1 Pre -> OK.
6. Ejecución: Crear archivos y registrar.
7. Smoke Test: `/hello_world` responde OK.
8. QA1/SEC1 Post -> OK.
9. Commit y Push -> OK.

## 16. Ejemplo de Acción Bloqueada
1. Request: "Arreglar error en n8n_data/voice_payload.txt".
2. `/risk_check` -> RED (Zona restringida).
3. **BLOCK**: El operador informa que no puede tocar `n8n_data` por política de aislamiento.

## 17. Roadmap Recomendado
- **R61**: Implementación del registro de evidencia (*Evidence Envelope*).
- **AG-Y2**: Primer tramo de cambio de código bajo protocolo R60.
- **R62**: Documentación de procedimientos de Rollback avanzados.
