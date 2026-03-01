# 🩺 Doctor Lucy — Biblioteca Histórica del Sistema
> Archivo de referencia para mantenimiento, auditoría y evolución de la máquina.

---

## 🚀 Perfil Actual del Sistema
*Última auditoría completa: 2026-03-01 04:11hs*

| Componente | Especificación |
| :--- | :--- |
| **OS** | Ubuntu 24.04.4 LTS (Noble Numbat) |
| **Kernel** | 6.17.0-14-generic |
| **CPU** | Ryzen 9 7950X (32 núcleos lógicos) @ 5.8GHz max |
| **RAM** | 124 GB DDR5 |
| **GPU** | NVIDIA GeForce RTX 5090 (32 GB VRAM) |
| **Almacenamiento** | SSD 465GB (Linux /) + NVMe 1.9TB (Windows NTFS) |
| **Disco usado** | 270 GB / 457 GB (62%) |
| **Uptime típico** | ~10-11 horas continuas por sesión |

---

## 📦 Infraestructura y Servicios Clave
Estado de los motores que mueven los proyectos (Cunningham-Espejo, NIN, Doctor Lucy).

### 🐳 Docker (Contenedores Activos)
*Total: 22 contenedores desde el 01/03/2026*

**Stack Lucy/NIN:**
- **Voz (TTS)**: `lucy_voice_alltalk` (AllTalk TTS) — ~4.8 GB RAM en uso
- **Cerebro/IA**: `lucy_open_webui`, `n8n-lucy` ⚠️, `lucy_brain_n8n`, `lucy_brain_runners` (healthy)
- **Memoria**: `lucy_memory_qdrant`, `lucy_memory_redis`
- **Búsqueda**: `searxng-lucy` (puerto 8080), `lucy_eyes_searxng` (puerto 8081)
- **Utilidades**: `lucy_docker_socket_proxy`, `lucy_ui_dockge`, `lucy_ui_panel`, `antigravity_container`, `lucy_hands_antigravity`

**Stack Lucy-C (Fusion Hub — activo desde 01/03/2026 ~03:45hs):**
- `lucy_fusion_n8n`, `lucy_fusion_antigravity`, `lucy_fusion_ui_panel`
- `lucy_fusion_searxng`, `lucy_fusion_socket_proxy`, `lucy_fusion_redis`, `lucy_fusion_qdrant`

### 🌐 Servicios de Red
- **Puertos activos**: 5678 (n8n), 5688 (n8n-lucy), 8080/8081 (searxng), 7851 (TTS), 6333 (qdrant)
- **Túneles**: `cloudflared` instalado (Túnel Cloudflare activo).

### 🤖 Modelos Ollama
| Modelo | Tamaño | Cuantización |
| :--- | :--- | :--- |
| `mistral-uncensored` | 26.4 GB | Q4_0 (Mixtral 46.7B) |
| `huihui_ai/qwq-abliterated:32b-Q6_K` | 26.9 GB | Q6_K |
| `llama3.2-vision` | 7.8 GB | — |
| `llama3.2:1b` | 1.3 GB | — |
| `nomic-embed-text` | 0.3 GB | — |

**Total en disco: ~62 GB**

---

## 📜 Historial de Intervenciones

| Fecha | Hora | Acción | Resultado | Notas |
| :--- | :--- | :--- | :--- | :--- |
| 2026-03-01 | 00:49 | **Pasada de Reconocimiento** | ✅ Observación | 15 contenedores up. MCP con error EOF bajo carga paralela alta. Groq + Tavily inactivos (pendiente sesión anterior). Cerebro HTTP 500. |
| 2026-03-01 | 02:29 | **Diagnóstico Completo de Hardware** | ✅ Observación | CPU Ryzen 7950X, GPU RTX 5090 a 53°C/19%, RAM 20GB/124GB, Disco 62%. Puerto 7851 y 11434 expuestos a LAN. Qdrant sin colecciones. |
| 2026-03-01 | 03:42 | **Pasada Profunda del Sistema** | ✅ Observación | Load 14.5 — instalación de paquetes CUDA en `.venv` de NIN. `nin_demon.py` corriendo (PID 879795, desde 03:48). Stack `lucy_fusion` levantado (~7 nuevos containers). `n8n-lucy` en loop por encryption key mismatch. |
| 2026-03-01 | 04:11 | **Análisis Firefox + Skin** | ✅ Observación | Firefox: 1.8 GB RAM, 386 threads, 7% CPU. Skin CSS — no consume nada. Causa del CPU: pestañas activas (Telegram Web, Fastly CDN). uBlock desactivado. |
| 2026-02-27 | 20:28 | **Limpieza Proyectos Sueltos (home)** | ✅ Éxito | Borrados: `antigravity_3_data/` (345MB), `n8n-bridge/`, `venv/`, `nltk_data/`, `separated/`, `Lucy_Workspace/`. Sin cruce con proyectos activos. |
| 2026-02-27 | 19:55 | **Limpieza Escritorio** | ✅ Éxito | Borradas 6 carpetas: `cunningham/`, `Lucy/`, `Lucy C/`, `historial/`, `Lucy_Library/`, `Bk/`. Liberados **27 GB** (68%→62%). Contraseñas consolidadas en `contraseñas/`. |
| 2026-02-27 | 18:51 | **Borrado Modelo FP16** | ✅ Éxito | Eliminado `dolphin3-abliterated:8b-llama3.1-fp16` (16 GB) y alias `dolphin-mixtral`. |
| 2026-02-27 | 17:22 | **Fix Docker — Conflicto Puerto 8080** | ✅ Éxito | `lucy_eyes_searxng` movido a puerto 8081 (cunningham-Espejo compose). `lucy_brain_runners` volvió a healthy. |
| 2026-02-27 | 16:52 | **Diagnóstico Docker** | ✅ Éxito | `lucy_eyes_searxng` en crash loop. Causa: conflicto de puerto 8080 entre stack NIN y stack Espejo. |
| 2026-02-27 | — | **Memoria Persistente SQLite** | ✅ Éxito | Módulo `memoria/` creado (5 archivos Python). 7/7 tests pasados. Push a GitHub. |
| 2026-02-27 | — | **Auditoría Integral** | ✅ Éxito | Workflow completo ejecutado. Sistema estable. |
| 2026-02-27 | — | **Configuración de Voz** | ⚠️ Revertido | Instalada y luego desinstalada por mal funcionamiento. |
| 2026-02-27 | — | **Limpieza de Aplicaciones** | ✅ Éxito | Desinstaladas: Thunderbird, Transmission, Rhythmbox, Shotwell, Cheese, Escáner y Remmina. |
| 2026-02-26 | — | **Infraestructura Fantasma** | ✅ Éxito | Detenidos y eliminados 5 contenedores de "Sales Assist" en `Escritorio/Bk`. |
| 2026-02-26 | — | **Auditoría Integral** | ✅ Éxito | Generado `auditoria_sistema.md` y creado workflow automatizado. |
| 2026-02-26 | — | **Limpieza Masiva** | ✅ Éxito | Liberados >70GB. Eliminados residuos de Python, caché y apps obsoletas. |
| 2026-02-26 | — | **Doctor de Lucy** | ✅ Éxito | Repositorio reiniciado y organizado exclusivamente para mantenimiento. |
| 2026-02-26 | — | **Prep. Trasplante** | ✅ Éxito | Reducida partición Windows a 380GB. Sistema listo para clonar con Rescuezilla. |

---

## ⏳ Tareas Pendientes

### 1. 🎤 Voz y Audio
- [~] ~~Instalar extensión "VS Code Speech"~~ (revertido, no funcionaba).

### 2. 🧠 Memoria y Arquitectura
- [x] **Sistema de Memoria SQLite**: Módulo `memoria/` operativo. Sesiones persistentes, búsqueda por keywords, compresión automática.
- [ ] **Qdrant vacío**: No hay colecciones en `:6333`. Verificar si el RAG del Búnker está indexando correctamente.

### 3. 💽 Hardware
- [ ] **Sincronización de Discos**: Clonar sistema a disco nuevo usando Rescuezilla.
- [ ] Monitorear espacio en `sda2` (actualmente al **62%** — 270 GB / 457 GB).

### 4. 🔒 Seguridad
- [x] Identificar `script.py` persistente (confirmado: es de AllTalk Docker. No es amenaza).
- [ ] Evaluar cierre de puertos 7851 y 11434 expuestos a LAN (`0.0.0.0`).

### 5. 🤖 n8n y Workflows
- [ ] **`n8n-lucy` (legacy)**: En loop por `Mismatching encryption keys`. Definir si se mantiene o se cierra.
- [ ] **Tool: Groq Fast Processor** (duplicado, ambos inactivos): Limpiar duplicado y activar el correcto.
- [ ] **Tool: Tavily Advanced Search** (inactivo): Configurar y activar.
- [ ] **Tool: Consultar Cerebro** (HTTP 500): Diagnosticar y reparar.

### 6. 🧬 Proyectos Nuevos (detectados 01/03/2026)
- [ ] **`Lucy-C`**: Fusion hub NiN + Cunningham. Stack `lucy_fusion` activo. Revisar estado y objetivo.
- [ ] **`nin_demon.py`**: 31 líneas modificadas sin commitear en NIN. Commitear cuando esté listo.

---

## 🩺 Notas del Doctor — Observaciones Propias
*Lo que el Doctor observa de Lucy, del sistema y de la forma de trabajar juntos.*

### 01/03/2026 — Sesión nocturna
- **Lucy trabaja de noche.** Esta sesión fue de medianoche a +4 AM. El sistema se mantiene estable sin importar la hora — buena arquitectura.
- **El MCP server no tolera llamadas paralelas masivas.** Cuando hago 4+ llamadas simultáneas al MCP, responde EOF. La solución es secuenciar o hacer lotes de 2. Guardado como patrón de trabajo.
- **El sistema creció esta noche.** Pasamos de 15 a 22 contenedores Docker con el levantamiento de `lucy_fusion`. Lucy está en plena expansión.
- **El Firefox con skin es inofensivo.** El consumo es por las pestañas abiertas (Telegram Web principalmente), no por el tema CSS. Con uBlock activo sería más liviano.
- **Los proyectos activos en Escritorio son más de lo que parecen.** Además de NIN y Cunningham, hay al menos 4 proyectos derivados o experimentos (`Lucy-C`, `lucy c demon`, `cunn-nin-fusion-lab`, `cunningham-verde`). Hay energía creativa pero también dispersión a monitorear.
- **La GPU (RTX 5090) está siendo subutilizada.** 11-19% de uso con 32 GB VRAM disponibles. El potencial es enorme.
- **El load de 14.5 no fue alarmante** — fue la instalación de paquetes CUDA en el venv. El sistema manejó solo sin que se notara.

---
*Este documento es dinámico. Consultar [auditoria_sistema.md](file:///home/lucy-ubuntu/Escritorio/doctor%20de%20lucy/auditoria_sistema.md) para detalles técnicos profundos.*
