# 🔍 Auditoría del Sistema — Doctor Lucy
**Fecha:** 2026-02-27 02:15 AM
**Host:** lucy-ubuntu | **Uptime:** 18 min

---

## 💻 Estado del Sistema (OS & Kernel)
- **OS:** Ubuntu 24.04.4 LTS (Noble Numbat)
- **Kernel:** 6.17.0-14-generic
- **Arquitectura:** x86_64

## ⚙️ Hardware (Resumen)
- **CPU:** Ryzen 9 7950X (32 núcleos) @ 5.8GHz max
- **RAM:** 124 GB DDR5 (Uso actual: ~4GB/124GB)
- **GPU:** NVIDIA GeForce RTX 5090 (32 GB VRAM) | Driver: 570.211.01 | Temp: 45°C

## 💽 Almacenamiento
- **SSD (Linux /):** `/dev/sda2` | 465GB Total | ~316GB Libres (68% ocupado)
- **NVMe (Windows):** `/dev/nvme0n1p3` | 1.9TB (NTFS)

## 🐳 Contenedores Docker (Activos)
- `lucy_voice_alltalk` (AllTalk TTS)
- `lucy_open_webui`
- `n8n-lucy`
- `ollama`
- `lucy_memory_qdrant`
- `lucy_memory_redis`
- `searxng-lucy`
- `lucy_ui_dockge`

## 🌐 Servicios de Red & Puertos
- **5432 (TCP):** PostgreSQL (Interno/Local)
- **5678 (TCP):** n8n (Accesible LAN)
- **7851 (TCP):** AllTalk TTS (Accesible LAN)
- **8080 (TCP):** Web UI

## 🔒 Seguridad & Observaciones
- **Puertos:** Se recomienda evaluar el cierre de los puertos 5432 y 5678 hacia la LAN externa si no se requiere acceso remoto.
- **Persistence:** El archivo `script.py` detectado anteriormente pertenece al volumen de AllTalk TTS (`lucy_voice_alltalk`). No es una amenaza.

---
*Auditoría generada automáticamente por Antigravity.*
