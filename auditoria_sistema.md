# 🔍 Auditoría del Sistema — Doctor Lucy
**Última actualización:** 2026-03-01 04:23hs
**Host:** lucy-ubuntu | **Uptime típico:** 10-11h por sesión

---

## 💻 Estado del Sistema (OS & Kernel)
- **OS:** Ubuntu 24.04.4 LTS (Noble Numbat)
- **Kernel:** 6.17.0-14-generic
- **Arquitectura:** x86_64
- **1 usuario activo:** `lucy-ubuntu`

## ⚙️ Hardware (Resumen)
- **CPU:** Ryzen 9 7950X · 16 núcleos / 32 threads · Máx 5.883 GHz
- **RAM:** 124 GB total · ~20-21 GB en uso habitual · SWAP 8 GB (0 B usado)
- **GPU:** NVIDIA GeForce RTX 5090 · 32 GB VRAM · Uso habitual 11-19% · Temp 38-56°C · ~57-68W
- **CPU Load típico:** 5-8 en reposo. Picos de hasta 14 durante instalaciones de paquetes.

## 💽 Almacenamiento
- **SSD CT500 (Linux /):** `/dev/sda2` | 457 GB | 270 GB usados | **164 GB libres (62%)**
- **NVMe ADATA (Windows):** `/dev/nvme0n1p3` | 1.9 TB | NTFS · Sin montar en Linux
- **Snap loops:** 20+ particiones loop (snaps varios) — normal
- **Tendencia:** +4 GB desde 2026-02-27. Monitorear.

## 🐳 Contenedores Docker (22 activos al 01/03/2026)

### Stack Lucy/NIN (15 containers)
| Contenedor | RAM | Puerto | Estado |
| :--- | :--- | :--- | :--- |
| `lucy_brain_n8n` | 216 MB | — | ✅ healthy |
| `lucy_brain_runners` | 5 MB | — | ✅ healthy |
| `lucy_hands_antigravity` | 38-40 MB | 5000 | ✅ healthy |
| `lucy_ui_panel` | 38 MB | — | ✅ healthy |
| `lucy_open_webui` | 624 MB | 3001 | ✅ healthy |
| `lucy_ui_dockge` | 117 MB | 5001 | ✅ healthy |
| `lucy_voice_alltalk` | **4.8 GB** | 7851 (LAN) | ✅ |
| `lucy_memory_qdrant` | 156 MB | 6333 | ✅ |
| `lucy_memory_redis` | 7 MB | 6379 | ✅ |
| `lucy_eyes_searxng` | 104 MB | 8081 | ✅ |
| `lucy_docker_socket_proxy` | 20 MB | 2375 | ✅ |
| `antigravity_container` | 36 MB | — | ✅ |
| `n8n-lucy` | 1.2 GB | 5688 | ⚠️ Loop encryption key |
| `qdrant-lucy` | 156 MB | 6335/6336 | ✅ |
| `searxng-lucy` | 116 MB | 8080 | ✅ |

### Stack Lucy-C / Fusion Hub (7 containers — activo desde 01/03/2026 ~03:45hs)
`lucy_fusion_n8n` · `lucy_fusion_antigravity` · `lucy_fusion_ui_panel`
`lucy_fusion_searxng` · `lucy_fusion_socket_proxy` · `lucy_fusion_redis` · `lucy_fusion_qdrant`

## 🌐 Servicios de Red & Puertos
| Puerto | Servicio | Exposición |
| :--- | :--- | :--- |
| 5678 | n8n (lucy_brain_n8n) | localhost |
| 5688 | n8n-lucy (legacy) | localhost |
| 6333/6335 | Qdrant | localhost |
| 3001 | Open WebUI | localhost |
| 5001 | Dockge | localhost |
| 8080/8081 | SearXNG | localhost |
| 5000 | Antigravity MCP | localhost |
| **7851** | **AllTalk TTS** | **⚠️ 0.0.0.0 (LAN)** |
| **11434** | **Ollama** | **⚠️ 0.0.0.0 (LAN)** |

## 🤖 Modelos Ollama (5 modelos, ~62 GB disco)
| Modelo | Tamaño |
| :--- | :--- |
| `huihui_ai/qwq-abliterated:32b-Q6_K` | 26.9 GB |
| `mistral-uncensored:latest` | 26.4 GB |
| `llama3.2-vision:latest` | 7.8 GB |
| `llama3.2:1b` | 1.3 GB |
| `nomic-embed-text:latest` | 0.3 GB |

## 🔒 Seguridad & Observaciones

### Conocidos / Resueltos
- `script.py` en AllTalk Docker → inofensivo (confirmado 2026-02-27)
- `n8n-lucy` en loop de error → `Mismatching encryption keys` — contenedor legacy, no es una amenaza

### Pendientes de atender
- **Puertos LAN abiertos:** 7851 (AllTalk) y 11434 (Ollama) escuchan en `0.0.0.0`. Si la red LAN es confiable, OK. Si no, cerrar con firewall.
- **Qdrant sin colecciones:** `:6333` vacío al 01/03/2026. Verificar si el RAG del Búnker está indexando.

## 📊 n8n Workflows — Estado al 01/03/2026
- **Activos:** Memory (Search/Upsert/Apply/Feedback), Consultar Colmena, Research Colmena, Sirena Telegram, Doctor System, System Health, Ejecutor Python, Repo Scanner, Grep Repo, Scraping Profundo, Analizar Github, Administrador APIs, Control Docker, Vigía Redes Sociales, Noticias IA, Escribir Búnker, Agente Secreto Mapeador, Búnker RAG, Lucy nin c, Envío CV, Ping, Notebook (inactivo)
- **⚠️ Con problemas:** `Groq Fast Processor` (duplicado, ambos inactivos), `Tavily Advanced Search` (inactivo), `Consultar Cerebro` (HTTP 500)

## 🧬 Proyectos en Escritorio (mapa actual)
| Proyecto | Ruta | Estado |
| :--- | :--- | :--- |
| **NIN** | `Escritorio/NIN/` | ✅ Activo · `nin_demon.py` modificado sin commit |
| **Cunningham-Espejo** | `Escritorio/cunningham-Espejo/` | ✅ Activo · checkpoint 01/03 |
| **Lucy-C** | `Escritorio/Lucy-C/` | 🆕 Fusion hub NiN+Cunn · stack docker activo |
| `lucy c demon` | `Escritorio/lucy c demon/` | 🆕 Creado 01/03 02:51 |
| `cunn-nin-fusion-lab` | `Escritorio/cunn-nin-fusion-lab/` | 🆕 Creado 01/03 01:55 |
| `cunningham-verde` | `Escritorio/cunningham-verde/` | ❓ Solo `/workspace`, owner `root` |
| `Cerebro` | `Escritorio/Cerebro/` | Notas vacías (test del Búnker) |
| `doctor de lucy` | `Escritorio/doctor de lucy/` | ✅ Este repo. Sincronizado. |

---
*Auditoría actualizada por Antigravity · 2026-03-01 04:23hs*
