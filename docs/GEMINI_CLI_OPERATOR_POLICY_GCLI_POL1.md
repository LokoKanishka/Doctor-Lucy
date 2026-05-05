# Gemini CLI Operator Policy (GCLI-POL1)

## 1. Objetivo
Establecer un marco de ejecución controlado para Gemini CLI dentro del ecosistema Doctora Lucy / LucyClaw, permitiendo la autonomía en tramos técnicos autorizados mediante "permisos agrupados" y garantizando la integridad de las zonas críticas.

## 2. Contexto y Justificación
Para mejorar la eficiencia operativa en tareas repetitivas o multi-archivo (como la creación de plugins LucyClaw), Gemini CLI puede actuar como ejecutor de tramos completos cuando el ticket define un alcance cerrado y seguro.

## 3. Repositorio Canónico y Alcance
- **Ruta**: `/home/lucy-ubuntu/Escritorio/doctora-lucy`
- **Rama**: `memoria/bunker`
- **Remote**: `git@github.com:LokoKanishka/Doctor-Lucy.git`

## 4. Permisos Agrupados (Grouped Permissions)
Cuando un ticket incluye la etiqueta **"PERMISO AGRUPADO AUTORIZADO"**, Gemini CLI puede realizar las siguientes acciones sin confirmación paso a paso:
1. **Validación inicial**: Comprobación de path, rama y limpieza de Git.
2. **Lectura**: Acceso a archivos permitidos dentro del repositorio.
3. **Edición**: Crear o modificar los archivos listados explícitamente en el ticket.
4. **Testing**: Ejecutar `py_compile`, `node --check`, QA1 (`verify_lucyclaw_green_commands.py`) y SEC1 (`verify_lucyclaw_security_policy.py`).
5. **Instalación**: `openclaw plugins install` del plugin específico autorizado.
6. **Reinicio**: Un único reinicio del gateway `openclaw-gateway.service` si los tests pasan.
7. **Commit/Push**: Registrar los cambios con el mensaje indicado y subir a la rama autorizada.

## 5. Zonas Prohibidas (Hard Block)
Gemini CLI tiene terminantemente prohibido:
- Acceder o modificar archivos `.env`.
- Imprimir o procesar tokens, secretos o API keys.
- Acceder a `n8n_data`, bases de datos SQLite o credenciales de n8n.
- Modificar la Bóveda (`boveda_lucy.sqlite`) o la personalidad (`SOUL.md`).
- Acceder a la carpeta legacy `/home/lucy-ubuntu/Escritorio/Doctor-Lucy`.
- Escribir archivos fuera de la raíz del repositorio canónico.

## 6. Restricciones Técnicas
- **No sudo**: Está prohibido el uso de sudo.
- **No shell libre destructiva**: Solo se permiten comandos atómicos o scripts controlados.
- **No borrado masivo**: No se deben eliminar archivos del core sin orden explícita externa al ticket.
- **No scripts de voz**: No ejecutar TTS o scripts de audio sin permiso especial.

## 7. Protocolo de Parada (Hard Stop)
Gemini CLI **DEBE** detenerse y solicitar intervención manual si:
- El entorno no coincide (path, rama o remote incorrectos).
- Aparecen archivos inesperados o conflictos de Git.
- **Falla QA1 o SEC1**.
- Se detectan fugas de secretos o rutas legacy activas.
- El comando `/lucy_next_step` devuelve un estado `BLOCK` después de los cambios.
- El push falla por problemas de red o de permisos.

## 8. Relación con LucyClaw
Esta política complementa las capacidades de planificación:
- `/plan_brief`, `/risk_check`, `/permission_brief`, `/change_plan` y `/scaffold_plan` siguen siendo la fuente de verdad para el diseño técnica antes de la ejecución.

## 10. Protocolo de Voz (VOICE REPORT PRECEDENCE)
De acuerdo con `GEMINI.md` y la Rule 5, el reporte de voz está permitido siempre que no contradiga las restricciones del ticket.
- Si el ticket prohíbe TTS, voz o tocar `n8n_data`, el reporte de voz queda suspendido.
- Las restricciones del ticket tienen prioridad absoluta sobre el protocolo de personalidad.
- Esta regla aplica a cualquier operador (Gemini CLI o Antigravity).
