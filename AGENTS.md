# Mandamientos de Automatización n8n para Agentes IA (AGENTS.md) 🩺⚖️

## 🚀 Autonomy Preflight & Domain Router (PRIORITY)

Antes de cualquier ejecución de herramientas, LucyClaw debe aplicar este protocolo de decisión:

1. **Identificar Intención**: ¿El usuario quiere leer, clickear, abrir, diagnosticar el sistema o exportar un archivo?
2. **Verificar Precondiciones**:
   - **Chrome (Control)**: Requiere pestañas adjuntadas (`browser status`). Si no hay, reportar BLOQUEO exacto.
   - **Firefox (Visibilidad)**: Solo para apertura (`lucy_firefox_open`). No prometer lectura DOM ni clicks.
   - **Sistema (Estado)**: Usar herramientas `machine_*`. No responder de memoria.
3. **Acción con Evidencia**: Ejecutar y verificar con una observación fresca (snapshot, status, ls).
4. **Reporte Final**: Entrega evidencia real o el motivo del bloqueo. Prohibido decir "listo" sin evidencia.

| Dominio | Herramienta | Evidencia Mínima |
| :--- | :--- | :--- |
| **Lectura Web** | `browser` (Chrome) | Snapshot de texto visible |
| **YouTube** | `browser` (Chrome) | Título + Estado de reproducción |
| **NotebookLM** | `browser` (Chrome) | Snapshot (Read-only por defecto) |
| **Firefox Open** | `lucy_firefox_open` | Confirmación de apertura visible |
| **Diagnóstico** | `machine_*` | Datos reales del hardware/servicio |
| **Archivos** | `fs_write` / `lowriter` | Ruta verificada + Tamaño de archivo |

---

Como agente en el workspace de Doctora Lucy, juro respetar y acatar las siguientes reglas fundamentales al operar, diseñar o modificar flujos de trabajo en n8n:

## Frontera Local De Voz

- Doctora Lucy usa AllTalk/TTS solo en `127.0.0.1:7854`.
- Fusion Reader v2 usa AllTalk/TTS en `127.0.0.1:7853`; Doctora Lucy no debe
  usar, matar, reiniciar ni tomar ese puerto como fallback.
- `7852` queda como puerto historico/no asignado. Si aparece en memorias o
  bitacoras viejas, no usarlo para nuevos arranques.
- `7851` es legacy compartido y no debe usarse como voz principal de Doctora.
- Para arrancar voz de Doctora, usar `scripts/start_lucy_voice_tts.sh`, que solo
  limpia su propio puerto `7854`.

### 1. Preeminencia de Plantillas (Templates First)
Antes de construir cualquier flujo desde cero, **debo buscar obligatoriamente** en la biblioteca de plantillas de la comunidad de n8n. No reinventaré la rueda si existe una solución comunitaria validada para tareas comunes.

### 2. Configuración Explícita (Never trust defaults)
**Jamás confiaré en los valores por defecto** de los nodos de n8n. Estos son la fuente principal de alucinaciones y fallos. Siempre configuraré explícitamente TODOS los parámetros y variables pertinentes que dicten el comportamiento de un nodo.

### 3. Validación Multinivel Estricta
Aplicaré una estrategia de validación en fases antes de dar un flujo por terminado:
- **Nivel 1:** Chequeo rápido (`mode: 'minimal'`) de campos requeridos.
- **Nivel 2:** Validación exhaustiva (`mode: 'full', profile: 'runtime'`) para arreglar errores de configuración antes de la ejecución.
- **Nivel 3/4:** Uso de validadores de flujo completo y revisiones post-despliegue mediante ejecuciones de prueba reales.

### 4. Operaciones por Lotes (Batch Operations)
Para no saturar la API ni mi propia ventana de contexto, **agruparé las modificaciones de los nodos** usando operaciones parciales de actualización (`n8n_update_partial_workflow` o equivalentes) en una sola llamada estructurada, evitando llamadas atómicas y repetitivas.

### 5. Sintaxis Rigurosa en Conexiones (`addConnection`)
Al conectar nodos, seguiré la estructura estricta requerida. **Nunca** enviaré conexiones como objetos amalgamados o strings combinados. Las conexiones requieren sus parámetros exactos: *nodo origen*, *tipo de salida*, *índice de salida*, y *nodo destino*.

### 6. Enrutamiento Preciso en Nodos IF (Branch)
En los nodos condicionales (ej. IF, Switch), **especificaré siempre la ruta o rama exacta** (`branch`). Nunca omitiré este parámetro para evitar que las lógicas TRUE/FALSE terminen confluyendo en la misma salida y arruinando el flujo causal. Ruta "0" suele ser TRUE, Ruta "1" FALSE.

### 7. Nodo Code como Último Recurso
Priorizaré el uso de nodos nativos y estándar de n8n (HTTP Request, Set, Switch, IF, etc.). Solo usaré el nodo "Code" (JavaScript/Python) cuando sea absolutamente imposible resolver la lógica con los bloques visuales estándar.

### 8. Enfoque "Lite" para Cuidar el Contexto
Entiendo que los JSON de n8n masivos rompen ventanas de contexto. Utilizaré un enfoque semántico y ligero: emplearé herramientas tipo "scan" para obtener índices resumidos y solo haré "focus" o "zoom" en los nodos específicos que necesite auditar o modificar, minimizando la carga de tokens.

### 9. Protocolo "Revisión de Lucy" (Diagnóstico Estándar)
Entiendo que frases como "revisá la PC", "revisá a Lucy" o "qué está pasando en la PC" activan el protocolo canónico definido en `docs/REVIEW_PROTOCOL.md`.
*   **Prioridad**: Por defecto realizaré una **Revisión Normal**.
*   **Foco**: Debo priorizar el estado actual, detectar anomalías o cuellos de botella, y emitir una recomendación final clara.
*   **Salud Integral**: Evaluaré hardware, infraestructura n8n/Hub, y la integridad de mi propia memoria.

### 10. Política de Backups Pre-Modificación (Rollback)
Antes de ejecutar actualizaciones parciales o totales sobre un workflow productivo mediante la API de n8n o modificar un JSON de flujo, **debo forzar siempre un backup local** del estado actual para garantizar la capacidad de rollback inmediato si la inyección lógica falla.

### 11. Frontera de Navegadores (Chrome vs Firefox)
Entiendo la distinción técnica entre las herramientas de navegación:
- **Chrome/Chromium (OpenClaw)**: Es mi navegador principal de automatización. Solo en este puedo realizar `snapshot`, `click`, `type`, y obtener el `DOM` o capturas de pantalla con fines de verificación.
- **Firefox (Host Tool)**: Solo tengo capacidad de **apertura** (`lucy_firefox_open`). No puedo leer el contenido, ni interactuar con los elementos, ni obtener evidencia visual o de datos de lo que sucede dentro de Firefox.
- **Evidencia**: Nunca afirmaré haber realizado una acción en Firefox (como "leí el texto" o "hice click") ya que carezco de los drivers para ello. Si se requiere interacción, usaré Chrome.

---
*Santificado y asimilado en el núcleo de Doctora Lucy. Estas no son sugerencias, son leyes absolutas de diseño.*
