# 🩺 Doctor Lucy — Biblioteca Histórica del Sistema
> Archivo de referencia para mantenimiento, auditoría y evolución de la máquina.

---

## 🚀 Perfil Actual del Sistema
*Última auditoría completa: 2026-02-27 20:28hs*

| Componente | Especificación |
| :--- | :--- |
| **OS** | Ubuntu 24.04.4 LTS (Noble Numbat) |
| **Kernel** | 6.17.0-14-generic |
| **CPU** | Ryzen 9 7950X (32 núcleos lógicos) @ 5.8GHz max |
| **RAM** | 124 GB DDR5 |
| **GPU** | NVIDIA GeForce RTX 5090 (32 GB VRAM) |
| **Almacenamiento** | SSD 465GB (Linux /) + NVMe 1.9TB (Windows NTFS) |
| **Disco usado** | 266 GB / 457 GB (62%) |

---

## 📦 Infraestructura y Servicios Clave
Estado de los motores que mueven los proyectos (Cunningham-Espejo, NIN, Doctor Lucy).

### 🐳 Docker (Contenedores Activos)
- **Voz (TTS)**: `lucy_voice_alltalk` (AllTalk TTS)
- **Cerebro/IA**: `lucy_open_webui`, `n8n-lucy`, `lucy_brain_n8n`, `lucy_brain_runners` (healthy)
- **Memoria**: `lucy_memory_qdrant`, `lucy_memory_redis`
- **Búsqueda**: `searxng-lucy` (puerto 8080), `lucy_eyes_searxng` (puerto **8081** — fix 27/02)
- **Utilidades**: `lucy_docker_socket_proxy`, `lucy_ui_dockge`, `lucy_ui_panel`

### 🌐 Servicios de Red
- **Puertos activos**: 5678 (n8n), 5688 (n8n-lucy), 8080/8081 (searxng), 7851 (TTS), 6333 (qdrant)
- **Túneles**: `cloudflared` instalado (Túnel Cloudflare activo).

### 🤖 Modelos Ollama
| Modelo | Tamaño | Cuantización |
| :--- | :--- | :--- |
| `mistral-uncensored` | 26 GB | Q4_0 (Mixtral 46.7B) |
| `qwq-abliterated:32b-Q6_K` | 26 GB | Q6_K |
| `llama3.2-vision` | 7.8 GB | — |
| `nomic-embed-text` | 274 MB | — |

---

## 📜 Historial de Intervenciones

| Fecha | Hora | Acción | Resultado | Notas |
| :--- | :--- | :--- | :--- | :--- |
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

### 3. 💽 Hardware
- [ ] **Sincronización de Discos**: Clonar sistema a disco nuevo usando Rescuezilla.
- [ ] Monitorear espacio en `sda2` (actualmente al **62%** — 266 GB / 457 GB).

### 4. 🔒 Seguridad
- [x] Identificar `script.py` persistente (confirmado: es de AllTalk Docker. No es amenaza).
- [ ] Evaluar cierre de puertos hacia la LAN.

---
*Este documento es dinámico. Consultar [auditoria_sistema.md](file:///home/lucy-ubuntu/Escritorio/doctor%20de%20lucy/auditoria_sistema.md) para detalles técnicos profundos.*
