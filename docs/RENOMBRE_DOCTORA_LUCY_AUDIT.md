# Auditoría y Plan de Renombre: NIN -> Doctora Lucy

## 1. Resumen de la Auditoría
Se ha realizado un escaneo completo del repositorio `/home/lucy-ubuntu/Escritorio/doctor de lucy` para identificar toda la "contaminación" derivada del nombre del proyecto hermano `NIN` (`nin`, `NIN`, `nin-`, `nin_`). 

**Nombre canónico de este proyecto:** Doctora Lucy
**Total de referencias encontradas:** ~42 ocurrencias en 13 archivos distintos.

## 2. Clasificación de Referencias

Las referencias se dividen en 4 categorías de riesgo:

| Archivo / Contexto | Ocurrencia | Clasificación | Riesgo |
| :--- | :--- | :--- | :--- |
| `GEMINI.md` | Menciones en texto ("NIN", "NIN-CORE") | **A** (Branding) | Bajo |
| `bitacora_mantenimiento.md` | Texto narrativo ("Stack NIN", "Graph RAG NiN") | **A** (Branding) | Bajo |
| `docs/regla_aislamiento_*.md` | "NIN standalone" | **A** (Branding) | Bajo |
| `scripts/test_megademon_cot.py`| Prompt: "Sos NiN, el sistema..." | **A** (Branding) | Bajo |
| `scripts/nin_ojo.py` | Argparse: "NIN-OJO: El Demonio..." | **A** (Branding) | Bajo |
| `scripts/start_demon.sh` | Echos a la terminal ("NiN-Demon") | **A** (Branding) | Bajo |
| `scripts/nin_dj.py` | Nombre del script y logs internos | **B** (Técnico Renombrable) | Medio |
| `scripts/nin_ojo.py` | Nombre del script | **B** (Técnico Renombrable) | Medio |
| `scripts/telegram_daemon.py` | Llamadas a `nin_dj.py` | **C** (Requiere Migración) | Medio |
| `scripts/start_demon.sh` | Rutas a `/home/.../NIN/scripts/nin_demon.py` | **D** (Externo/Fijo - No tocar) | Alto (Apunta a otro repo) |
| `scripts/backup_lucy_core.sh` | Exclusión de `/home/.../NIN` | **D** (Externo/Fijo - No tocar) | Alto (Apunta a otro repo) |
| `mcp_config.json` | Claves de servidor (`nin-github`, `nin-n8n-v3`) | **D** (Externo/Fijo - No tocar) | Alto (Rompería MCP) |
| `GEMINI.md` | Lista de tools (`nin-github`, `nin-n8n-v3`) | **D** (Externo/Fijo - No tocar) | Alto (Tool names fijos) |

*(Nota de Clasificación: A = Branding Visible, B = Identificador Técnico Local, C = Técnico Local con Migración, D = Externo/Fijo)*

## 3. Análisis de Factibilidad

- **Branding visible (Tipo A):** ~45%. Puede renombrarse inmediatamente sin romper código.
- **Técnico Local Seguramente Renombrable (Tipo B y C):** ~25%. Requiere renombrar archivos (ej. `nin_dj.py` -> `lucy_dj.py`) y sus respectivos imports/ejecuciones en crontabs o systemd.
- **Técnico Externo y Fijo (Tipo D):** ~30%. **NO DEBE TOCARSE AÚN**. Modificar integraciones de MCP (como `nin-n8n-v3`) rompería el puente con Claude/Gemini. Las rutas estáticas que apuntan al otro proyecto (carpeta `/home/lucy-ubuntu/Escritorio/NIN`) deben conservarse tal cual, porque hablan literalmente del otro proyecto.

## 4. Propuesta de Plan por Etapas

### Etapa 1: Renombre Canónico Visible (Seguro e Inmediato)
- **Archivos:** `GEMINI.md` (textos), bitácoras, `docs/*.md`, `test_megademon_cot.py` (prompts), echos en bash.
- **Acción:** Reemplazar menciones de "NIN" por "Doctora Lucy" o eliminar la contaminación de branding.
- **Riesgos:** Ninguno.
- **Criterio de validación:** Los reportes y la personalidad dejarán de tener crisis de identidad.

### Etapa 2: Renombre Técnico Local y Controlado (Corto Plazo)
- **Archivos:** Renombrar `scripts/nin_dj.py` a `scripts/music_brain_dj.py`, `scripts/nin_ojo.py` a `scripts/lucy_ojo.py`.
- **Acción:** Renombrar scripts físicos y actualizar sus llamadas dentro de `telegram_daemon.py`.
- **Riesgos:** Medio. Podría romper servicios `systemd` si los scripts están corriendo en background o cronjobs.
- **Criterio de validación:** Los demonios siguen levantando correctamente tras el renombre.

### Etapa 3: Identificadores Externos y Compatibilidad (Largo Plazo)
- **Archivos:** `mcp_config.json`, Configuración central de N8N.
- **Acción:** Migración coordinada (renombrar servidores MCP de `nin-github` a `lucy-github`, redesplegar, actualizar mcp_config).
- **Riesgos:** Muy alto. Corta la capacidad de herramientas de los agentes IA.
- **Criterio de validación:** Las tools externas siguen operando bajo el prefijo `lucy-`.

---
**Conclusión:** El proyecto puede recuperar el 70% de su identidad visual y técnica local de forma inmediata. Los conectores externos (MCP Tools) deben mantenerse como "herencia" o planificarse en un ticket de DevOps exclusivo.
