# 🩺 Doctor Lucy — Biblioteca Histórica del Sistema
> Archivo de referencia para mantenimiento, auditoría y evolución de la máquina.

---

## 🚀 Perfil Actual del Sistema
*Última auditoría completa: 2026-02-26*

| Componente | Especificación |
| :--- | :--- |
| **OS** | Ubuntu 24.04.4 LTS (Noble Numbat) |
| **Kernel** | 6.17.0-14-generic |
| **CPU** | Ryzen 9 7950X (32 núcleos lógicos) @ 5.8GHz max |
| **RAM** | 124 GB DDR5 |
| **GPU** | NVIDIA GeForce RTX 5090 (32 GB VRAM) |
| **Almacenamiento** | SSD 465GB (Linux /) + NVMe 1.9TB (Windows NTFS) |

---

## 📦 Infraestructura y Servicios Clave
Estado de los motores que mueven los proyectos (Cunningham, NIN, Doctor Lucy).

### 🐳 Docker (Contenedores Activos)
- **Voz (TTS)**: `lucy_voice_alltalk` (AllTalk TTS)
- **Cerebro/IA**: `lucy_open_webui`, `n8n-lucy`, `ollama`
- **Memoria**: `lucy_memory_qdrant`, `lucy_memory_redis`
- **Utilidades**: `searxng-lucy`, `lucy_ui_dockge`, `lucy_ui_panel`

### 🌐 Servicios de Red (Atención)
- **Puertos LAN**: 5432 (DB), 5678 (n8n), 8080 (UI), 7851 (TTS) - *Abiertos a la red local.*
- **Túneles**: `cloudflared` instalado (Túnel Cloudflare activo).

---

## 📜 Historial de Intervenciones
| Fecha | Acción | Resultado | Notas |
| :--- | :--- | :--- | :--- |
| 2026-02-27 | **Configuración Marketplace** | Éxito | Cambiado a Microsoft para habilitar extensión de voz. Requiere reinicio. |
| 2026-02-27 | **Limpieza de Aplicaciones** | Éxito | Desinstaladas: Thunderbird, Transmission, Rhythmbox, Shotwell, Cheese, Escáner y Remmina. |
| 2026-02-26 | **Infraestructura Fantasma** | Éxito | Detenidos y eliminados 5 contenedores de "Sales Assist" en `Escritorio/Bk`. |
| 2026-02-26 | **Auditoría Integral** | Éxito | Generado `auditoria_sistema.md` y creado workflow automatizado. |
| 2026-02-26 | **Limpieza Masiva** | Éxito | Liberados >70GB. Eliminados residuos de Python, caché y apps obsoletas. |
| 2026-02-26 | **Doctor de Lucy** | Éxito | Repositorio reiniciado y organizado exclusivamente para mantenimiento. |
| 2026-02-26 | **Prep. Trasplante** | Éxito | Reducida partición Windows a 380GB. Sistema listo para clonar con Rescuezilla. |

---

## ⏳ Tareas Pendientes

### 1. 🎤 Voz y Audio
- [ ] **Reiniciar VS Code** para activar el marketplace de Microsoft.
- [ ] Instalar extensión **"VS Code Speech"**.
- [ ] Configurar TTS en Antigravity para respuesta por voz.

### 2. 💽 Hardware
- [ ] **Sincronización de Discos**: Clonar sistema a disco nuevo usando Rescuezilla.
- [ ] Monitorear espacio en `sda2` (actualmente al 68%).

### 3. 🔒 Seguridad
- [ ] Identificar `script.py` persistente (ahora sabemos que es de AllTalk Docker).
- [ ] Evaluar cierre de puertos 5432/5678 hacia la LAN.

---
*Este documento es dinámico. Consultar [auditoria_sistema.md](file:///home/lucy-ubuntu/Escritorio/doctor%20de%20lucy/auditoria_sistema.md) para detalles técnicos profundos.*
