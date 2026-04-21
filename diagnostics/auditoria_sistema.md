# Auditoría Completa del Sistema
**Fecha de Auditoría:** 2026-04-21 20:17 (Local)

## Estado del Sistema
- **OS:** Ubuntu 24.04.4 LTS
- **Kernel:** 6.17.0-20-generic
- **Uptime:** up 48 minutes
- **Hostname:** lucy-ubuntu-System-Product-Name

## Hardware Clave
- **CPU:** 32 cores, 1 Socket, escalando entre 425 MHz y 5883 MHz.
- **Memoria RAM:** 124Gi Total / 19Gi Usado / 77Gi Libre.
- **GPU:** NVIDIA GeForce RTX 5090 (32607 MiB), Driver 570.211.01. Temp: 45C. Utilización: 2%.

## Almacenamiento
- **Raíz (nvme0n1p2):** 1.9T Total / 946G Usado (53%)

## Contenedores Docker Activos
- doctor_lucy_n8n
- searxng-lucy
- qdrant-lucy
- N8N-NiN-uso-exclusivo-del-proyecto-nin
- lucy_open_webui
- lucy_memory_qdrant

## Procesos de Inteligencia (Servicios & IA)
- **Ollama:** Inactivo temporalmente o sin modelos cargados en memoria RAM.
- **AllTalk TTS (Lucy):** Activo (PID 12478) usando 3.0% RAM y 124% CPU (Picos al hablar).
- **AllTalk (Fusion Reader):** Activo (PID 13269, 13265) usando ~2.7% RAM conjunta.

## Observaciones de Salud
- La GPU 5090 está prácticamente en reposo absoluto (2%).
- RAM sobra por completo (77 GB libres).
- Discos con 53% de uso, hay espacio de sobra.
- Todo corre a la perfección.
