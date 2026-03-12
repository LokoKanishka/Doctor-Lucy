# 📂 Estructura del Repositorio Doctor-Lucy

Para mantener el orden y la integridad del sistema, se establece la siguiente norma de organización.

## 🏗️ Capas de Organización

### 1. Directorio Raíz (Núcleo)
Solo archivos esenciales para la identidad, configuración de seguridad y arranque del sistema.
- `AGENTS.md`, `GEMINI.md`, `README.md`
- `.env`, `mcp_config.json`
- `telegram_alert.py`, `vital_signs.py`, `start_lucy_hub.sh`

### 2. `docs/` (Documentación y Bitácora)
Manuales, inventarios y el registro histórico de intervenciones.
- `bitacora_mantenimiento.md`
- `inventario_pc.md`
- `lista_aplicaciones.md`
- `archive/`: Archivos obsoletos, atajos de escritorio y herramientas legacy (ej. `bfg.jar`).

### 3. `diagnostics/` (Salud del Sistema)
Reportes técnicos generados por auditorías y scripts de control.
- `auditoria_sistema.md`
- `audits/`: Histórico de reportes de auditoría.

### 4. `memoria/` (Memoria Semántica y RAG)
Persistencia de la conciencia de Lucy y bases de datos.
- `agente_memoria.db`
- `Memoria_Principal_Lucy/`: Datos internos de Qdrant/Redis.
- `conciencia_rag.py`, `persistencia.py`, etc.

### 5. `scripts/` (Motores de Automatización)
Herramientas ejecutables de mantenimiento, seguridad y sincronización.

---
**REGLA DE ORO:** No generar archivos nuevos en la raíz. Todo reporte o dato generado debe ir a su carpeta correspondiente según su categoría.
