# Auditoría Completa del Sistema
**Fecha de ejecución:** 2026-04-16T00:30:00-03:00

## 1. Estado del Sistema
- **OS:** Ubuntu 24.04.4 LTS (Noble Numbat)
- **Kernel:** 6.17.0-20-generic
- **Uptime:** 00:31:03 up 7 min (Sistema reiniciado recientemente)
- **Hostname:** lucy-ubuntu-System-Product-Name

## 2. Hardware
- **CPU:** 32 Cores/Threads, Max 5883 MHz, 1 Socket
- **RAM:** 128 GB (124 GiB total, 12 GiB en uso, 97 GiB libre)
- **Swap:** 8.0 GiB (0 B en uso)
- **GPU:** NVIDIA GeForce RTX 5090 (32 GB VRAM), Driver v570.211.01

## 3. Almacenamiento
- **Disco Principal (nvme0n1):** 2.0 TB NVMe (nvme0n1p2: 1.9 TB, 49% en uso, montado en `/`)
- **Partición EFI:** 1.1 GB (nvme0n1p1, montado en `/boot/efi`)
- **Loops (Snaps):** Múltiples aplicaciones Snap montadas activamente en loop.

## 4. Servicios Activos (Destacados)
- **Docker:** Activo y corriendo con normalidad
- **N8N:** Procesos de `node /usr/local/bin/n8n` detectados (PID 3038, 3137)
- **Antigravity (VS Code/Agents):** Procesos detectados en ejecución de lenguaje natural y extensiones.

## 5. Aplicaciones por Memoria (Top RAM Hogs)
1. `/snap/spotify/93/` (Renderer de Spotify) (3.7% RAM)
2. `chrome` (7.4% RAM - principal proceso web)
3. `antigravity` (Language server y VS Code backend) (2.4% - 4.5% RAM)

## 6. Inteligencia Artificial local (Ollama)
- **Modelos Instalados:** (Total ~263 GB, 18 modelos)
  - qwen3-coder-next:latest (51 GB)
  - qwen3-coder:30b-a3b-q8_0 (32 GB)
  - gemma-3-stable:latest (29 GB)
  - glm-4.7-flash:latest (19 GB)
  - devstral-small-2:latest (15 GB)
  - ...y otros modelos avanzados de LLM y Vision.

## 7. Contenedores Docker (activos)
- `doctor_lucy_n8n` (N8N) - 127.0.0.1:6969
- `searxng-lucy` (SearxNG) - 127.0.0.1:8080
- `qdrant-lucy` (Qdrant Database) - 6333/6334
- `N8N-NiN-uso-exclusivo-del-proyecto-nin` - 127.0.0.1:5688
- `lucy_open_webui` (Open WebUI CUDA) - 0.0.0.0:3001
- `lucy_memory_qdrant` - 6333

## 8. Observaciones / Acciones Pendientes
- **Crasheo previo del entorno gráfico/snap:** Se reportó por la usuaria el congelamiento de ventanas (barra negra, aplicaciones con tildes rojas, Spotify y Firefox cerrándose instantáneamente). Si bien el hardware es extremadamente robusto (RTX 5090, 128GB RAM), los síntomas concuerdan con un crasheo del entorno Wayland/GNOME Shell, o del deamon de Snap (`snapd`) en la sesión anterior, el cual desmontó los File Systems en caliente y produjo que toda interacción causara un error de entrada/salida (cerrando las apps).
- **Fallback Activo:** El sistema volvió con un nuevo boot tras un hard reset. El hardware se encuentra en excelente estado (temperatura GPU 45°C en reposo, 22% VRAM ocupada) y el almacenamiento tiene más de 900 GB libres. No hay indicios de cuellos de botella de capa física.
