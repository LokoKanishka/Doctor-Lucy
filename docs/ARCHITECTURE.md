# Doctor-Lucy — Arquitectura Real

> Documento canónico de arquitectura. Generado en Tramo 4C (2026-04-27).
> Rama: `memoria/bunker` · HEAD: `d4cafc7`

---

## 1. Propósito del sistema

Doctor-Lucy es el **centro de control, mantenimiento y supervisión autónoma** de la estación de trabajo de Diego (Ubuntu Linux, NVIDIA RTX 5090). Opera como un agente persistente con identidad propia ("Lucy Cunningham"), capaz de:

- Monitorear la salud del hardware y software.
- Recibir y responder comandos vía Telegram.
- Ejecutar razonamiento autónomo con modelos locales (Ollama) o cloud (OpenClaw).
- Hablar mediante síntesis de voz (AllTalk TTS).
- Mantener memoria persistente en SQLite (Bóveda).
- Orquestar flujos de trabajo complejos con n8n.
- Auditar proactivamente el estado del sistema.

La arquitectura creció orgánicamente por capas, y este documento refleja el estado **real** del sistema, no el ideal.

---

## 2. Estado operativo actual

| Campo | Valor |
|---|---|
| Rama canónica | `memoria/bunker` |
| Último commit | `d4cafc7` — `chore(git): ignore generated runtime artifacts` |
| Anterior | `9d72840` — `chore(lucy): stabilize daemon paths and env loading` |
| Sincronización | Local = origin (0 ahead, 0 behind) |

### Archivos vivos que NO deben tocarse a ciegas

| Archivo | Motivo |
|---|---|
| `n8n_data/boveda_lucy.sqlite` | Memoria viva — bóveda principal de Lucy |
| `n8n_data/database.sqlite` | Base de datos de n8n |
| `n8n_data/*.sqlite-wal / -shm` | Sidecars de SQLite en uso |
| `n8n_data/voice_payload.txt` | Payload de voz en tránsito |
| `n8n_data/daemon.pid` | PID del daemon activo |
| `n8n_data/telegram_offset.txt` | Offset de polling Telegram |
| `.env` | Secretos (tokens, API keys) |
| `memoria/agente_memoria.db` | DB secundaria del módulo memoria |

---

## 3. Subsistemas principales

### 3.1 Voz / TTS

**Flujo:** Agente escribe `voice_payload.txt` → `lucy_announcer.sh` lo lee → invoca `lucy_alltalk.py` → AllTalk TTS genera audio → `paplay` reproduce.

| Archivo | Función | Estado |
|---|---|---|
| `scripts/lucy_alltalk.py` | Cliente HTTP hacia AllTalk TTS | ✅ Activo |
| `scripts/lucy_announcer.sh` | Disparador pasivo (lee payload, invoca TTS) | ✅ Activo |
| `scripts/start_lucy_voice_tts.sh` | Arranca servidor AllTalk en puerto 7854 | ✅ Activo |
| `scripts/lucy_voice.sh` | Wrapper alternativo de voz | ❓ Desconocido |
| `scripts/voice_casting.py` | Comparación de voces (test) | ❓ Legacy |
| `n8n_data/voice_payload.txt` | Payload de texto para TTS | Runtime |
| `.voice_env/` | Virtualenv dedicado para dependencias TTS | Infraestructura |

**Puertos (fuente: `VOICE_PORTS.md`):**

| Puerto | Servicio | Dueño |
|---|---|---|
| **7854** | Doctora Lucy TTS | Antigravity |
| **7853** | Fusion Reader TTS GPU | **PROHIBIDO TOCAR** |
| 7852 | Histórico / no asignado | — |
| 7851 | AllTalk Legacy | Compartido |

> **Regla de Oro:** Ningún script de Lucy debe ejecutar `fuser -k` sobre el puerto 7853.

### 3.2 Telegram

**Pieza activa:** `lucy_telegram_listener.py` — Listener v2 con cerebro IA (Ollama/Qwen3-14B).

| Archivo | Función | Estado |
|---|---|---|
| `scripts/lucy_telegram_listener.py` | Listener v2 con cerebro IA local | ✅ Activo |
| `scripts/lucy_telegram_send.sh` | Envío de mensajes/archivos a Diego | ✅ Activo |
| `scripts/lucy_telegram_listener.sh` | Wrapper shell con Python inline | ⚠️ Duplicado/legacy |
| `scripts/telegram_bridge.py` | Bridge simple con dotenv | ❌ Legacy |
| `scripts/telegram_daemon.py` | Daemon Telegram con rutas a NIN | ❌ Legacy (peligroso) |
| `telegram_alert.py` | Script suelto en root | ❌ Legacy |

> **⚠️ Alerta:** Hay 5 piezas de Telegram. Solo `lucy_telegram_listener.py` + `lucy_telegram_send.sh` son activas. Las demás son capas históricas pendientes de consolidación.

### 3.3 Daemons / Autonomía

| Archivo | Función | Estado |
|---|---|---|
| `scripts/lucy_daemon_v2_cloud.py` | Daemon cloud con OpenClaw bridge + Telegram | ✅ Activo (canónico) |
| `scripts/lucy_daemon_v1.py` | Daemon v1 con MCP + sequential-thinking | ⚠️ En transición |
| `scripts/start_demon.sh` | Arranca NIN demon (apunta a otro proyecto) | 🔴 Legacy peligroso |
| `scripts/lucy_watchdog.py` | Watchdog de sub-agentes (Rule 4) | ✅ Activo |
| `n8n_data/daemon.pid` | PID file del daemon activo | Runtime |

**Daemon canónico actual:** `lucy_daemon_v2_cloud.py`
- Escucha Telegram.
- Delega razonamiento a OpenClaw vía `lucy_openclaw_bridge.py`.
- Soporta envío de archivos con `[SEND_FILE: /path]`.
- Lee `SOUL.md` como system prompt.
- Guarda offset en `n8n_data/telegram_offset.txt`.
- Log en `n8n_data/lucy_daemon_v2.log`.

> **🔴 Riesgo:** `start_demon.sh` apunta a `/home/lucy-ubuntu/Escritorio/NIN/` — un proyecto diferente. Si se ejecuta en este workspace, falla o mata procesos ajenos.

### 3.4 n8n

| Componente | Detalle |
|---|---|
| Container Docker | `doctor_lucy_n8n` |
| Puerto | `6969` |
| Datos | `n8n_data/` (SQLite, config, nodes, logs) |
| Backups | `n8n_backups/` (~90 workflows JSON + SQLites de volúmenes) |
| Workflows canónicos | `workflows/LUCY__Boot_Memory.json`, `workflows/LUCY__Commit_Memory.json` |
| Hub | `start_lucy_hub.sh` (abre Firefox perfil "Enjambre" en localhost:6969) |

> **Advertencia:** `n8n_data/` es runtime de un contenedor Docker. No debe tratarse como código fuente; los datos cambian continuamente. El `.gitignore` actual ya excluye `n8n_data/`, pero `boveda_lucy.sqlite` fue trackeada antes de esa regla y sigue en Git históricamente.

### 3.5 Memoria / Bóveda

| Archivo | Función | Estado |
|---|---|---|
| `n8n_data/boveda_lucy.sqlite` | Bóveda principal — tabla `memoria_core` | ✅ Activo (vivo) |
| `memoria/` | Módulo Python (persistencia, sumarización, RAG, knowledge graph) | ✅ Activo |
| `scripts/lucy_memory_gateway.py` | HTTP server para acceso a bóveda (puerto 6970) | ✅ Activo |
| `scripts/sync_memory_to_n8n.py` | Sincronización bóveda → búnker JSONL | ✅ Activo |
| `systemd/lucy-memory-gateway.service` | Unit file systemd | ⚠️ Path desactualizado |

**Módulo `memoria/`:**
- `db.py` — Conexión y DDL SQLite
- `persistencia.py` — Inicio/cierre de sesión, auto-save
- `sumarizacion.py` — Compresión de sesiones
- `herramientas.py` — Consulta de historial
- `conciencia_rag.py` — RAG sobre memoria
- `knowledge_graph.py` — Grafo de conocimiento
- `migrar_a_rag.py` — Script de migración
- `demo.py` — Demo de uso

> **⚠️ Inconsistencia detectada:** `systemd/lucy-memory-gateway.service` apunta a `/home/lucy-ubuntu/Escritorio/doctora-lucy/` (path viejo). El workspace actual es `/home/lucy-ubuntu/Escritorio/doctor de lucy/`. El servicio necesita actualización de paths.

> **Política pendiente:** `boveda_lucy.sqlite` es memoria viva. Requiere tramo propio de backup/política — no debe depender de Git como mecanismo de respaldo.

### 3.6 Auditoría PC

| Archivo | Función | Estado |
|---|---|---|
| `scripts/auditoria.sh` | Auditoría principal con flags (scope, Docker, red) | ✅ Activo |
| `scripts/auditoria_boot.sh` | Check de arranque rápido (Rule 1) | ✅ Activo |
| `scripts/sys_check.sh` | Health check wrapper (opt-in seguro) | ✅ Activo |
| `scripts/seguridad_check.sh` | Auditoría de seguridad (puertos, servicios) | ✅ Activo |
| `scripts/temp_audit.sh` | Auditoría rápida OS (mínima) | ❓ Legacy |
| `scripts/health_dashboard.py` | Dashboard Python con SQLite | ❓ Desconocido |
| `scripts/verify_scope_default.sh` | Validación de fronteras de auditoría | ✅ Activo |
| `diagnostics/` | Reportes de auditoría (8 archivos + subcarpeta) | Generado |

**Protocolo:** Definido en `docs/REVIEW_PROTOCOL.md` con 3 niveles (Corta, Normal, Profunda).

### 3.7 OpenCloud / OpenClaw

| Archivo | Función | Estado |
|---|---|---|
| `scripts/lucy_openclaw_bridge.py` | Bridge HTTP/CLI hacia OpenClaw gateway | ✅ Activo |
| `scripts/lucy_daemon_v2_cloud.py` | Daemon que consume el bridge | ✅ Activo |
| `scripts/test_openclaw_gateway.py` | Test del bridge | Test |
| `scripts/lucy_quota_audit.py` | Auditoría de cuota API | ✅ Activo |
| `scripts/lucy_model_list.py` | Listado de modelos disponibles | ✅ Activo |
| `skills/` | 24 skills de ClawhHub | ⚠️ Mayoría macOS-only |
| `plugins.txt` | Inventario de plugins OpenClaw | Estático |
| `skills.txt` | Inventario de skills | Estático |
| `diagnostics/openclaw_audit_20260426.md` | Último audit de OpenClaw | Generado |

**Skills relevantes en Linux:** Solo `model-usage-linux` fue adaptado. Las demás 23 skills (1password, apple-notes, apple-reminders, bear-notes, bluebubbles, camsnap, discord, goplaces, imsg, mcporter, notion, oracle, peekaboo, sag, session-logs, slack, spotify-player, summarize-pro, things-mac, trello, twitter-x-api, voice-call, clawhub-local) son originales de ClawhHub y **la mayoría requieren macOS** o binarios no instalados.

> **Pendiente:** Este frente requiere auditoría profunda con contexto de Diego. No resolver sin su input explícito.

### 3.8 Utilidades / Wrappers

| Archivo | Función | Estado |
|---|---|---|
| `scripts/lucy_exec.sh` | Wrapper anti-cartel azul (Rule 6) | ✅ Activo |
| `scripts/ejecutor_seguro.py` | Wrapper anti-hang para comandos | ✅ Activo |
| `scripts/backup_lucy_core.sh` | Backup core completo | ✅ Activo |
| `scripts/switch_agent.sh` | Conmutador de roles multi-agente | ✅ Activo |
| `scripts/cleanup.sh` | Limpieza de disco | ✅ Activo |
| `scripts/mantenimiento_proactivo.sh` | Limpieza de snaps/logs/paquetes | ✅ Activo |
| `scripts/limpiar_apps.sh` | Desinstala apps no deseadas | ❓ Legacy (usa sudo) |
| `scripts/fix_projector.sh` | Fix hardware dual GPU NVIDIA+AMD | ❓ Legacy |
| `scripts/master_search.py` | Búsqueda multi-proveedor (Tavily + fallbacks) | ✅ Activo |
| `scripts/md_to_pdf.py` / `.sh` | Conversión Markdown → PDF | ❓ Legacy |
| `scripts/nin_ojo.py` | Visión por computadora (screenshots, OCR) | ❓ Legacy |
| `scripts/nin_dj.py` | Control Spotify vía Firefox | ❓ Legacy |
| `scripts/spotify_cli.py` | CLI Spotify con OAuth | ❓ Legacy |
| `scripts/descargar_behemoth.py` | Descarga modelos HuggingFace GGUF | ❓ Legacy |

### 3.9 Infraestructura del Agente

| Componente | Path | Función |
|---|---|---|
| Identidad | `SOUL.md` | System prompt / personalidad de Lucy |
| Latido | `HEARTBEAT.md` | Estado de salud |
| Reglas agente | `GEMINI.md` | Rules del agente Antigravity |
| Mandamientos n8n | `AGENTS.md` | Leyes de diseño para n8n |
| Puertos de voz | `VOICE_PORTS.md` | Asignación de puertos TTS |
| Roles | `.agents/roles/` | Sub-agentes (N8N_RESEARCHER, SUPERVISOR_FUSION) |
| Workflows agente | `.agents/workflows/` | boot.md, commit.md, auditoria_sistema.md |
| MCPs | `.agents/mcps/servers/` | Servidores MCP embebidos (137MB con node_modules) |
| Trust mode | `.agents/TRUST_MODE` | Flag de ejecución autónoma |
| Servicios systemd | `systemd/` | 2 unit files (memory-gateway, watcher-daemon) |

---

## 4. Flujo operativo principal

```
Diego (Telegram / IDE)
    │
    ├─→ lucy_telegram_listener.py  (polling Telegram)
    │       │
    │       ├─ Comando /status → auditoria_boot.sh → respuesta Telegram
    │       └─ Mensaje libre → Ollama (Qwen3-14B) → respuesta Telegram
    │
    ├─→ lucy_daemon_v2_cloud.py  (daemon cloud)
    │       │
    │       ├─ Mensaje Telegram → delegate_mission()
    │       │       └─ lucy_openclaw_bridge.py → OpenClaw gateway
    │       │               └─ Respuesta IA cloud → Telegram
    │       └─ Archivos: [SEND_FILE: /path] → sendDocument Telegram
    │
    ├─→ Antigravity (IDE)
    │       │
    │       ├─ Escribe voice_payload.txt
    │       └─ Ejecuta lucy_announcer.sh
    │               └─ lucy_alltalk.py → AllTalk TTS (7854) → paplay
    │
    └─→ n8n (puerto 6969)
            │
            ├─ Workflows Boot/Commit Memory
            ├─ Tools (Búnker, Grep, Docker, etc.)
            └─ Cerebro Voz (Alpha/Beta/Gamma workflows en backups)

Memoria:
    boveda_lucy.sqlite ←→ lucy_memory_gateway.py (puerto 6970)
                       ←→ sync_memory_to_n8n.py → búnker JSONL
                       ←→ módulo memoria/ (RAG, knowledge graph)
```

> **Nota:** Los dos listeners (telegram_listener y daemon_v2_cloud) son procesos separados con propósitos distintos: el listener responde con IA local, el daemon delega a OpenClaw. Cuál se usa depende de qué se arranca manualmente.

---

## 5. Componentes activos, legacy y en transición

| Componente | Archivo | Estado | Motivo | Tocar ahora |
|---|---|---|---|---|
| Daemon cloud | `lucy_daemon_v2_cloud.py` | ✅ Activo | Daemon canónico actual | No |
| Daemon v1 | `lucy_daemon_v1.py` | ⚠️ Transición | MCP + sequential-thinking, puede volver | Con cautela |
| Start demon | `start_demon.sh` | 🔴 Peligroso | Apunta a proyecto NIN ajeno | Deprecar |
| Telegram listener | `lucy_telegram_listener.py` | ✅ Activo | Cerebro IA Ollama | No |
| Telegram listener.sh | `lucy_telegram_listener.sh` | ⚠️ Duplicado | Python inline, duplica .py | Deprecar |
| Telegram bridge | `telegram_bridge.py` | ❌ Legacy | Reemplazado por listener | Deprecar |
| Telegram daemon | `telegram_daemon.py` | ❌ Legacy | Rutas NIN hardcodeadas | Deprecar |
| Telegram alert | `telegram_alert.py` | ❌ Legacy | Script suelto en root | Mover o deprecar |
| AllTalk client | `lucy_alltalk.py` | ✅ Activo | Core de voz | No |
| Announcer | `lucy_announcer.sh` | ✅ Activo | Protocolo Rule 5 | No |
| Voice TTS start | `start_lucy_voice_tts.sh` | ✅ Activo | Arranque AllTalk 7854 | No |
| OpenClaw bridge | `lucy_openclaw_bridge.py` | ✅ Activo | Bridge HTTP/CLI | No |
| Memory gateway | `lucy_memory_gateway.py` | ✅ Activo | HTTP server bóveda | No |
| Auditoría | `auditoria.sh` | ✅ Activo | Con flags | No |
| Auditoría boot | `auditoria_boot.sh` | ✅ Activo | Rule 1 | No |
| Exec wrapper | `lucy_exec.sh` | ✅ Activo | Rule 6 anti-cartel azul | No |
| Watchdog | `lucy_watchdog.py` | ✅ Activo | Rule 4 | No |
| Switch agent | `switch_agent.sh` | ✅ Activo | Multi-agente | No |
| Stress test v2 | `lucy_stress_test_v2.py` | ✅ Activo | Testing | No |

---

## 6. Archivos vivos y política Git

### Se versiona normalmente
- `scripts/` (código fuente)
- `docs/` (documentación)
- `memoria/*.py` (módulo Python)
- `SOUL.md`, `HEARTBEAT.md`, `GEMINI.md`, `AGENTS.md`, `VOICE_PORTS.md`
- `.agents/` (roles, workflows, TRUST_MODE)
- `workflows/` (Boot/Commit Memory JSON)
- `systemd/` (unit files)
- `README.md`

### Se ignora (`.gitignore`)
- `__pycache__/`, `*.pyc`
- `.env`, `.env.*`
- `.venv/`, `.voice_env/`
- `n8n_data/` (runtime completo)
- `*.log`, `*.sqlite-wal`, `*.sqlite-shm`
- `scripts/.scratch/`
- `miniconda.sh`, `*.AppImage`, `bfg.jar`
- `output.json`, `scratch_workflow*.json`, `test.md`, `test.pdf`
- `_test_subagent/`

### Se respalda fuera de Git
- `n8n_data/boveda_lucy.sqlite` — Requiere backup automático externo.
- `n8n_data/database.sqlite` — Estado de n8n. Idem.
- `n8n_backups/` — Voluminoso. Mejor en almacenamiento externo.
- `memoria/agente_memoria.db` — DB viva.

### Se commitea solo como snapshot consciente
- `diagnostics/auditoria_sistema.md` — Cambia cada corrida.
- `diagnostics/audits/` — Acumula reportes.
- `STRESS_TEST_REPORT.md` — Cambia cada test.

> **⚠️ boveda_lucy.sqlite** sigue tracked históricamente en Git (fue añadida antes de que `n8n_data/` entrara al `.gitignore`). Requiere tramo propio de decisión: `git rm --cached` o política de snapshot consciente.

---

## 7. Riesgos estructurales conocidos

| Riesgo | Severidad | Detalle |
|---|---|---|
| 5 capas de Telegram | 🟡 Media | Listener, listener.sh, bridge, daemon, alert — solo 1 activo |
| 3 daemons | 🟡 Media | v1, v2-cloud, start_demon — roles no consolidados |
| `start_demon.sh` → NIN | 🔴 Alta | Apunta a proyecto ajeno; puede matar procesos |
| 17 scripts con rutas absolutas | 🟡 Media | Principales dinamizados en 2B; secundarios pendientes |
| Skills OpenClaw macOS-only | 🟡 Media | 23 de 24 skills posiblemente no funcionales en Linux |
| SQLite viva en Git | 🟡 Media | `boveda_lucy.sqlite` tracked históricamente |
| Systemd paths desactualizados | 🟡 Media | `lucy-memory-gateway.service` apunta a path viejo |
| Archivos root sueltos | 🟢 Baja | `telegram_alert.py`, `vital_signs.py`, etc. |
| Diagnostics generados | 🟢 Baja | Pueden ensuciar Git si se commitean sin intención |
| MCP servers embebidos | 🟢 Baja | 137MB de node_modules + .git embebido en `.agents/mcps/servers/` |

---

## 8. Regla de oro para próximos cambios

1. **No tocar piezas activas sin prueba.** Todo lo marcado como "✅ Activo" en §5 funciona y fue estabilizado.
2. **Separar cada saneamiento en un tramo único** con objetivo claro, modo de trabajo definido, y staged selectivo.
3. **No mezclar SQLite/diagnostics con código** en el mismo commit.
4. **OpenCloud/OpenClaw requiere contexto previo de Diego.** No resolver skills ni gateway sin su input.
5. **Usar `WORKSPACE_ROOT`** para cualquier path nuevo. No agregar rutas absolutas.
6. **Respetar la frontera de puertos** definida en `VOICE_PORTS.md`. Puerto 7853 es sagrado.
7. **Los commits de estabilización/normalización van primero**, antes de consolidar o refactorizar.

---

## 9. Próximos tramos recomendados

| Orden | Tramo | Objetivo |
|---|---|---|
| 1 | Política de memoria viva | Decidir qué hacer con `boveda_lucy.sqlite` en Git + backup externo |
| 2 | Consolidación daemons/listeners | Deprecar formalmente capas legacy de Telegram y daemons |
| 3 | Limpieza root suelto | Mover o eliminar `telegram_alert.py`, `vital_signs.py`, etc. |
| 4 | OpenCloud/OpenClaw | Auditoría profunda de skills + gateway con contexto de Diego |
| 5 | Normalización rutas absolutas | Dinamizar los ~12 scripts secundarios que aún tienen `/home/lucy-ubuntu` |
