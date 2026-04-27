# Auditoría del Sistema — Doctora Lucy
**Fecha:** 2026-04-26 16:58 (UTC-3)
**Fingerprint:** DOCTOR_LUCY__7X9K

---

## 🟢 Estado General: OPERATIVO

---

## Sistema Operativo
| Campo | Valor |
|-------|-------|
| OS | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Kernel | 6.17.0-22-generic |
| Uptime | 14 minutos |
| Hostname | lucy-ubuntu |

---

## Hardware

### CPU & RAM
| Campo | Valor |
|-------|-------|
| RAM Total | 124 GiB |
| RAM Usada | 17 GiB |
| RAM Libre | 81 GiB |
| RAM Disponible | 107 GiB |
| Swap Total | 8.0 GiB |
| Swap Usada | 0 B |

### GPU (NVIDIA)
| Campo | Valor |
|-------|-------|
| Modelo | NVIDIA GeForce RTX 5090 |
| VRAM Total | 32607 MiB |
| VRAM Usada | 25655 MiB (78.6%) |
| Driver | 570.211.01 |
| Temperatura | 34°C |
| Utilización | 10% |

> ⚠️ **ATENCIÓN:** 78.6% de VRAM consumida. Principales consumidores: AllTalk TTS (Lucy 7854 + Fusion 7853) y Ollama.

### Almacenamiento
| Dispositivo | Tamaño | Usado | Disponible | Uso% |
|-------------|--------|-------|------------|------|
| /dev/nvme0n1p2 (/) | 1.9 TB | 1.2 TB | 631 GB | 65% |
| /dev/nvme0n1p1 (/boot/efi) | 1.1 GB | 6.2 MB | 1.1 GB | 1% |

---

## Docker — Contenedores Activos
| Contenedor | Imagen | Puerto | Estado |
|------------|--------|--------|--------|
| doctor_lucy_n8n | n8nio/n8n:latest | 127.0.0.1:6969 | ✅ Up |
| searxng-lucy | searxng/searxng:latest | 127.0.0.1:8080 | ✅ Up |
| qdrant-lucy | qdrant/qdrant:latest | 127.0.0.1:6335-6336 | ✅ Up |
| N8N-NiN | n8nio/n8n:latest | 127.0.0.1:5688 | ✅ Up |
| lucy_open_webui | open-webui:cuda | 0.0.0.0:3001 | ✅ Up (healthy) |
| lucy_memory_qdrant | qdrant/qdrant | 127.0.0.1:6333 | ✅ Up |

---

## Puertos Clave
| Puerto | Servicio | Estado |
|--------|----------|--------|
| 7854 | AllTalk TTS - **Doctora Lucy** | ✅ ACTIVO (python3 PID 23136) |
| 7853 | AllTalk TTS - **Fusion Reader v2** | ✅ ACTIVO (python PID 14509) |
| 6969 | n8n - Doctor Lucy | ✅ ACTIVO |
| 8080 | SearXNG | ✅ ACTIVO |
| 11434 | Ollama | ✅ ACTIVO |
| 3001 | Open WebUI | ✅ ACTIVO |
| 6970 | Lucy Daemon (Gateway) | ✅ ACTIVO (python3 PID 3162) |
| 8010 | Servicio Python | ✅ ACTIVO (PID 17157) |
| 8021 | Servicio Python (STT) | ✅ ACTIVO (PID 16726) |

---

## Modelos Ollama Instalados (26)
| Modelo | Tamaño |
|--------|--------|
| gpt-oss:20b-sanguine-q8 | 22 GB |
| gpt-oss:20b-multilingual-reasoner-q8 | 22 GB |
| ministral:14b-instruct-q8 | 14 GB |
| mistral-nemo:12b-q8 | 13 GB |
| ministral:14b-reasoning-q8 | 14 GB |
| qwen3:14b-q8_0 | 15 GB |
| qwen3-coder-next:latest | 51 GB |
| qwen3-coder:30b-a3b-q8_0 | 32 GB |
| qwen3-coder:30b | 18 GB |
| glm-4.7-flash:latest | 19 GB |
| devstral-small-2:latest | 15 GB |
| qwen2.5-coder:32b | 19 GB |
| qwen3:30b | 18 GB |
| devstral-small-2:24b-q8_0 | 25 GB |
| gemma-3-stable:latest | 29 GB |
| gemma-3-safe:latest | 29 GB |
| gemma-3-27b-heretic-v2 Q8_0 | 29 GB |
| nomic-embed-text:latest | 274 MB |
| llama3.2-vision:latest | 7.8 GB |
| *(+7 más)* | — |

---

## Top Procesos por RAM
| Proceso | PID | RAM |
|---------|-----|-----|
| AllTalk Lucy (7854) | 23136 | 2.2% (~2.9 GB) |
| AllTalk Fusion (7853) | 14509 | 2.0% (~2.7 GB) |
| Ollama Runner | 26059 | 1.0% (~1.4 GB) |
| Open WebUI | 3114 | 0.9% (~1.2 GB) |
| Fusion STT Server | 16726 | 0.7% (~1.0 GB) |
| VS Code (node) | 6085 | 0.6% (~795 MB) |
| Qdrant (lucy) | 3720 | 0.4% (~579 MB) |

---

## 🔍 DIAGNÓSTICO CRÍTICO

### ❌ Problema Principal Detectado: Caídas al Iniciar Conversación
- **Causa:** Los servidores de **Gemini 3.1 Pro** están sobrecargados ("high traffic").
- **Esto NO es un problema local.** La PC, la red, Docker, n8n — todo está operativo.
- **Solución aplicada:** Cambiar al modelo **Claude Opus 4.6 (Thinking)** que usa servidores distintos.
- **Recomendación:** Mantener Claude Opus como modelo primario hasta que Gemini estabilice sus servidores. Si Opus también falla, probar con otro modelo disponible en Antigravity.

### ⚠️ VRAM Alta (78.6%)
- Dos instancias de AllTalk TTS corriendo simultáneamente (Lucy 7854 + Fusion 7853).
- Ollama con modelo cargado en GPU.
- No es crítico ahora pero puede serlo si se carga un modelo grande en Ollama.

### ✅ Todo lo demás: SALUDABLE
- Todos los contenedores Docker UP
- Todos los puertos respondiendo
- RAM del sistema holgada (107 GiB disponibles)
- Disco al 65% — sin riesgo
- Temperatura GPU: 34°C — excelente
- Daemon Lucy en puerto 6970 — activo

---

## Acciones Recomendadas
1. **CERRAR la pestaña de conversación vieja** ("Resuming Lucy Operational Identity") que muestra el error de Gemini
2. **Usar Claude Opus 4.6** como modelo principal hasta nuevo aviso
3. Monitorear VRAM si se necesitan modelos Ollama grandes
