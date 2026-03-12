# Auditoría de Sistema - Doctor Lucy
**Fecha y Hora:** 2026-03-05 03:36:00
**Estado General:** ÓPTIMO

## 1. Sistema Operativo y Uptime
- **OS:** Ubuntu 24.04.2 LTS (Noble Numbat)
- **Kernel:** 6.13.0-1017-oem
- **Uptime:** 18:34
- **Hostname:** lucy-ubuntu

## 2. Hardware Principal
- **CPU:** AMD Ryzen 9 7950X3D (32 hilos, hasta 5.7GHz)
- **RAM:** 64GB DDR5 (62.7Gi total, ~12Gi usada, ~47Gi libre+cache)
- **GPU:** NVIDIA GeForce RTX 5090 (32GB VRAM)
  - **Driver:** 570.211.01
  - **Temp:** 34°C
  - **Utilización:** 0% (Idle)

## 3. Almacenamiento (Discos)
- **nvme0n1p2 (Root):** 1.8T total, 1.2T libre (33% usado)
- **sda1 (Lucy Data):** 2.0T total, 1.1T libre (45% usado)

## 4. Servicios y Red
- **n8n:** Activo en puerto 6969
- **Ollama:** Activo en puerto 11434
- **Docker:** Activo con contenedores (SearXNG, Keycloak, AllTalk TTS, etc.)
- **Puertos clave operativos:** 22 (SSH), 80/443 (HTTP/S), 6969 (n8n), 11434 (Ollama).

## 5. Modelos AI (Ollama)
- llama3.3:latest (70b)
- deepseek-r1:32b
- mistral-nemo:latest
- dolphin-mistral:latest

## 6. Software Crítico
- VS Code: 1.109.5
- Docker: 29.2.1
- Node.js: 22.22.0
- Python: 3.12.3 & 3.10.20

## 7. Observaciones y Pendientes
- [OK] Estabilidad térmica y de memoria.
- [PENDIENTE] Activar workflows de boot/commit en n8n (puerto 6969).
- [PENDIENTE] Dashboard de salud visual.

---
*Auditoría generada automáticamente por Doctora Lucy.*
