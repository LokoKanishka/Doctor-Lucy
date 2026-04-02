# 🩺 Auditoría Completa del Sistema - Doctora Lucy

**Fecha y Hora:** 01 de Abril 2026, 23:03 hs (Hora Local)
**Estado General:** 🟩 **OPERATIVO**

---

## 💻 1. Hardware y Sistema Operativo

### OS Info
- **Distribución:** Ubuntu 24.04.4 LTS (Noble Numbat)
- **Kernel:** 6.17.0-19-generic
- **Uptime:** 2:39 hs

### Procesamiento y Memoria
- **CPU:** 32 Cores disponibles. Frecuencia de uso actual ~76%. (Load Average: 3.85, 2.92, 2.44)
- **RAM:** 14 GiB Usados / 86 GiB Libres (Total: 124 GiB)
- **Swap:** 0 B Usados / 8.0 GiB Libres

### GPU (Gráficos y Tensor Core)
- **Modelo:** NVIDIA GeForce RTX 5090
- **VRAM Total:** 32607 MiB
- **Uso actual:** 10%
- **Temperatura:** 54°C
- **Driver:** 570.211.01

### Almacenamiento Principal
- **Disco Raíz (`/`):** 1.9T de capacidad, 539G usados (30%), 1.3T disponibles. SSD NVMe en perfecto estado.

---

## ⚙️ 2. Servicios e Infraestructura

### Contenedores y Nodos
El ecosistema Docker está levantado y saludable:
- `lucy_open_webui`: En puerto 3001
- `N8N-NiN-uso-exclusivo-del-proyecto-nin`: Servidor n8n activo (5678)
- `qdrant-lucy` & `lucy_memory_qdrant`: Motores vectoriales (6333/6334)
- `searxng-lucy`: Motor de búsqueda (8080)

### Motores de Inferencia (Ollama)
Disponemos de un arsenal robusto pre-descargado (15+ modelos), destacando:
- **Qwen3 Coder** (30B y 14B)
- **Gemma 3 Stable** (29GB)
- **GLM 4.7 Flash**
- **LLaMA 3.1 & 3.2 Vision**

### Consumo de Recursos (Top Profiling)
Actualmente los procesos que más memoria demandan son:
1. `steam` (Descargando/Actualizando - recién instalado)
2. `chrome` (Múltiples renderers y procesos)
3. `code` (VS Code + Language Servers)
4. `antigravity` (Servicios AI)
5. `open_webui` (Python backend)

---

## 🔒 3. Seguridad y Anomalías
- **Seguridad:** Puertos estándar locales operativos (`127.0.0.1`). Ningún proceso externo sospechoso consumiendo recursos CPU/GPU.
- **Servicios:** Systemd reporta `35 loaded units` saludables. Daemon de Nvidia, persistencia, Docker y Ollama operando normalmente.
- **Anomalías:** No se detectan bloqueos (locks de apt liberados). El procesador refleja carga moderada por los contenedores, lo cual es normal.

---
*Reporte generado automáticamente por Protocolo "Revisión de Lucy".*
