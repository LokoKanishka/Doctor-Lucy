# 📟 Registro de Puertos de Voz y Servicios (Frontera Lucy-Fusion)

Este documento define la asignación estricta de puertos para evitar conflictos entre los sistemas de **Doctora Lucy (Antigravity)** y **Fusion Reader v2**.

## 🛡️ Frontera de Puertos TTS (Auditado: 2026-04-19)

| Puerto | Servicio | Responsable | Notas |
| :--- | :--- | :--- | :--- |
| **7854** | **Doctora Lucy TTS** | Antigravity | **Puerto dedicado de Lucy.** Usar `start_lucy_voice_tts.sh`. |
| **7853** | **Fusion Reader TTS GPU** | Fusion Reader | **PROHIBIDO TOCAR.** Reservado para GPU local de Fusion. |
| **7852** | Histórico / no asignado | Ninguno | No usar para nuevos arranques; puede aparecer en bitácoras antiguas. |
| **7851** | AllTalk TTS (Legacy) | Compartido | No se recomienda para uso activo de Lucy. |

## 📦 Otros Servicios Clave

- **8010**: Fusion Reader UI (Panel Principal)
- **8021**: Fusion Reader STT (Speech-to-Text)
- **11434**: Ollama API (Modelos Locales)
- **6969**: n8n Core (Doctora Lucy)
- **13019**: n8n NiN (Extensión V3)

---
> [!IMPORTANT]
> **Regla de Oro**: Ningún script de Doctora Lucy debe ejecutar `fuser -k` sobre el puerto **7853**. Cualquier limpieza de procesos debe limitarse estrictamente al puerto **7854**.
