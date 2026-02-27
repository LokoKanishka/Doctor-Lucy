# 🩺 Auditoría del Sistema — Doctor de Lucy
> Última actualización: 2026-02-26 22:50 ART

---

## 🖥️ Sistema Operativo
| Campo | Valor |
|---|---|
| OS | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Kernel | 6.17.0-14-generic |
| Hostname | lucy-ubuntu-System-Product-Name |
| Uptime | 39 min (al momento de la auditoría) |

---

## 🧠 Hardware

### CPU
| Campo | Valor |
|---|---|
| Núcleos lógicos | 32 |
| Velocidad máx. | 5883 MHz |
| Velocidad mín. | 425 MHz |
| Factor de escala | 61% al momento |

### RAM
| Campo | Valor |
|---|---|
| Total | 124 GiB |
| Libre | ~45 GiB |
| En uso | ~19 GiB |
| Swap total | 8 GiB |
| Swap usado | 0 GiB (swap libre) |

### GPU
| Campo | Valor |
|---|---|
| Modelo | NVIDIA GeForce RTX 5090 |
| VRAM | 32 GiB |
| Driver | 570.211.01 |
| Temperatura | 52°C |

---

## 💾 Almacenamiento

| Dispositivo | Tamaño | Tipo | Sistema | Uso |
|---|---|---|---|---|
| /dev/sda2 | 464 GB | HDD/SSD | ext4 Linux (/) | **68% usado (292 GB)** |
| /dev/sda1 | 1 GB | SSD | vfat (EFI) | baja |
| nvme0n1p3 | 1.9 TB | NVMe | NTFS (Windows) | sin montar |
| nvme0n1p4 | 707 MB | NVMe | NTFS (Recovery) | sin montar |

> ⚠️ El disco principal (sda2) está al **68% de uso**. Monitorear regularmente.

---

## ⚙️ Servicios Activos (systemd)

| Servicio | Estado | Descripción |
|---|---|---|
| `docker.service` | ✅ running | Docker Engine |
| `containerd.service` | ✅ running | Container Runtime |
| `ollama.service` | ✅ running | LLM local (Ollama) |
| `nvidia-persistenced.service` | ✅ running | NVIDIA Persistence |
| `NetworkManager.service` | ✅ running | Red |
| `bluetooth.service` | ✅ running | Bluetooth |
| `cups.service` | ✅ running | Impresión |
| `gnome-remote-desktop.service` | ✅ running | Escritorio remoto GNOME |
| `cron.service` | ✅ running | Tareas programadas |
| `rsyslog.service` | ✅ running | Logs del sistema |
| `snapd.service` | ✅ running | Paquetes Snap |
| `wpa_supplicant.service` | ✅ running | WiFi |

---

## 🌐 Puertos Abiertos

| Puerto | Protocolo | Proceso | Descripción |
|---|---|---|---|
| 5432 | TCP (0.0.0.0) | PostgreSQL | Base de datos (expuesto en LAN) |
| 5678 | TCP (0.0.0.0) | n8n | Workflow automation (expuesto en LAN) |
| 8080 | TCP (local) | open-webui (uvicorn) | Chat UI para LLMs |
| 8787 | TCP (local) | python3 | Script propio |
| 6333 | TCP (local) | Qdrant | Base de datos vectorial |
| 5432 | TCP (local) | PostgreSQL | DB local |
| 3001 | TCP (local) | Desconocido | Por identificar |
| 5100 | TCP (local) | Desconocido | Por identificar |
| 5001 | TCP (local) | Desconocido | Por identificar |
| 631 | TCP (local) | CUPS | Impresión |
| 2375 | TCP (local) | Docker | API Docker sin TLS |

> ⚠️ **Puerto 5432 (PostgreSQL) y 5678 (n8n) escuchan en 0.0.0.0** — accesibles en la red local.
> ⚠️ **Puerto 2375 (Docker API) sin TLS** — potencial riesgo de seguridad si accesible externamente.

---

## 🤖 Procesos Relevantes en Ejecución

| Proceso | PID | RAM aprox. | Descripción |
|---|---|---|---|
| `openclaw-gateway` | 2101 | ~400 MB | Gateway Antigravity |
| `open-webui (uvicorn)` | 3661 | ~800 MB | UI web para LLMs |
| `python script.py` | 6592 | ~900 MB | Script Python (root) |
| `gnome-shell` | 3111 | ~400 MB | Escritorio GNOME |
| `google-chrome` | 12547 | ~300 MB | Chrome |
| `n8n (node)` | 4288 | ~300 MB | n8n Workflow |
| `VS Code` | 11046 | ~850 MB | Editor de código |
| `antigravity` | 18793+ | ~500 MB | Suite Antigravity |

---

## 🧠 Modelos Ollama Instalados

| Modelo | Tamaño | Última vez usado |
|---|---|---|
| `huihui_ai/dolphin3-abliterated:8b-llama3.1-fp16` | 16 GB | Hace 41 horas |
| `mistral-uncensored:latest` | 26 GB | Hace 7 días |
| `huihui_ai/qwq-abliterated:32b-Q6_K` | 26 GB | Hace 8 días |
| `dolphin-mixtral:latest` | 26 GB | Hace 8 días |
| `nomic-embed-text:latest` | 274 MB | Hace 2 semanas |
| `llama3.2-vision:latest` | 7.8 GB | Hace 4 semanas |

> 💡 Total aprox. en modelos: ~102 GB en disco.

---

## 👤 Usuarios del Sistema

| Usuario | Tipo |
|---|---|
| `root` | Superusuario |
| `lucy-ubuntu` | Usuario principal |

---

## 🔒 Seguridad — Observaciones

- **PostgreSQL (5432)** escucha en todas las interfaces — revisar si debe ser público
- **n8n (5678)** escucha en todas las interfaces — revisar si debe ser público
- **Docker API (2375)** sin TLS — riesgo si hay acceso externo
- **UFW**: estado no verificado (requiere contraseña sudo)
- **Script Python corriendo como root (PID 6592)** — identificar qué es
- `gnome-remote-desktop.service` activo — confirmar si está en uso
- `cloudflared` instalado — hay un túnel Cloudflare configurado

---

## 🐳 Docker

| Estado | Descripción |
|---|---|
| Docker activo | `containerd.service` + `docker.service` running |
| API Docker | Puerto 2375 (local, sin TLS) |

---

## 📦 Software Clave Instalado

- `antigravity 1.19.5`
- `code 1.109.4` (VS Code)
- `cloudflared 2026.2.0`
- `cmake 3.28.3`
- `docker / containerd`
- `ollama` (con múltiples modelos LLM)
- `n8n` (corriendo como proceso Node)
- `open-webui` (corriendo en puerto 8080)
- `qdrant` (base de datos vectorial, puerto 6333)
- `postgresql` (base de datos, puerto 5432)
- `audacious` (reproductor de audio)
- `cheese` (cámara)
- `thunderbird` (correo, via snap)
- `firefox` (navegador, via snap)
- `spotify` (via snap)
- `chrome` (Google Chrome instalado)

---

## 📝 Notas para Próximas Acciones

- [ ] Identificar el `script.py` corriendo como root (PID 6592)
- [ ] Identificar puertos 3001, 5100, 5001
- [ ] Evaluar si PostgreSQL y n8n deben estar expuestos en LAN
- [ ] Verificar estado de UFW (firewall)
- [ ] Limpiar modelos Ollama no utilizados (dolphin-mixtral, mistral-uncensored, qwq-abliterated sin usar hace días) — libera ~78 GB
- [ ] Monitorear uso del disco (68% en sda2)
