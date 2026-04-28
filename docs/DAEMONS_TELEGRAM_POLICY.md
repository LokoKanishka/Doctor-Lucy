# Doctor-Lucy — Política de Daemons y Telegram

Este documento establece la política oficial de ejecución para los componentes de autonomía (daemons) y escucha de Telegram en Doctor-Lucy.

## 1. Entry points canónicos

| Componente | Función | Estado | Cuándo usarlo | Qué NO hacer |
|---|---|---|---|---|
| `scripts/lucy_daemon_v2_cloud.py` | Daemon cloud principal. Orquesta OpenClaw, Telegram, y envíos de archivos. | ✅ Activo | Para iniciar la autonomía completa y acceso a herramientas en la nube. | No correr simultáneamente con otros daemons locales a menos que se aísle el scope. |
| `scripts/lucy_telegram_listener.py` | Listener local con cerebro de IA (Ollama/Qwen3). | ✅ Activo | Para operar 100% offline o testear razonamiento local. | No ejecutar si `lucy_daemon_v2_cloud.py` ya está escuchando en el mismo bot de Telegram. |
| `scripts/lucy_telegram_send.sh` | Wrapper para enviar mensajes/archivos a Telegram. | ✅ Activo | Para notificaciones proactivas desde el sistema (ej. finalización de un backup). | No usar `telegram_alert.py` en su lugar. |

## 2. Piezas legacy

| Componente | Motivo de legacy | Riesgo | Estado recomendado |
|---|---|---|---|
| `scripts/lucy_daemon_v1.py` | Usa un MCP local anterior. Reemplazado por v2_cloud. | Menor | En transición. No borrar, pero preferir v2. |
| `scripts/lucy_telegram_listener.sh` | Duplica la lógica de `lucy_telegram_listener.py` usando Python inline en bash. | Conflictos de PID | Bloqueado por defecto. |
| `scripts/telegram_bridge.py` | Implementación puente antigua. Reemplazada por el listener oficial. | Obsoleto | Bloqueado por defecto. |
| `scripts/telegram_daemon.py` | Daemon muy antiguo. Contiene rutas absolutas hacia proyectos externos (NIN). | Corrupción de estado ajeno | Bloqueado por defecto. |
| `telegram_alert.py` | Script suelto en root, funcionalidad cubierta por `lucy_telegram_send.sh`. | Desorden | No usar. Mantener inactivo. |
| `scripts/start_demon.sh` | Script bash histórico que dispara un daemon en `/home/lucy-ubuntu/Escritorio/NIN/`. | Alto. Ejecutarlo rompe fronteras de workspaces. | Bloqueado por defecto. |

## 3. Regla de consolidación

Para mantener la estabilidad del sistema:
- **No borrar** piezas legacy sin un tramo de limpieza explícito.
- **No ejecutar** piezas legacy sin permiso explícito ni evadiendo las variables de seguridad `DOCTOR_LUCY_ALLOW_LEGACY_*`.
- **No tener dos listeners** compitiendo por el mismo token/bot.
- **No arrancar** el daemon cloud y el listener local de forma simultánea a menos que uno actúe como esclavo o tengan flujos de polling claramente separados.
- **No usar** scripts que apunten al directorio de NIN (`/Escritorio/NIN/`) desde el entorno de Doctor-Lucy.

## 4. Riesgo de doble listener

Si se ejecutan dos listeners de Telegram (`daemon_v2` y `telegram_listener` o algún componente legacy):
- Ambos competirán por leer el API de Telegram.
- Se generarán conflictos de lectura y escritura en `n8n_data/telegram_offset.txt`.
- Habrá pérdida de mensajes y respuestas duplicadas incongruentes para el usuario.
- Siempre detenga un listener antes de levantar otro.

## 5. Start/stop seguro

Actualmente no existe un único entrypoint formal. Los scripts se lanzan manualmente o vía procesos dedicados.
**Acción requerida (Tramo futuro):** Crear `scripts/lucy_entrypoint.sh` o `scripts/lucy_status.sh` para gestionar los ciclos de vida de estos procesos de manera unificada.
