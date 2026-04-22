# HEARTBEAT.md — Tareas Proactivas de Lucy

Este archivo contiene la lista de verificación que Lucy evaluará de forma autónoma cada vez que se active su "latido" (daemon heartbeat).

## Tareas Diarias / Cada 30 min
- `[ ]` **Salud Docker**: Verificar que el contenedor `doctor_lucy_n8n` esté arriba y saludable. (`/docker`)
- `[ ]` **Memoria**: Alertar si el uso de swap excede el 50% o la RAM el 90%. (`/status`)
- `[ ]` **Conectividad**: Verificar que el Túnel Cloudflare o n8n sigan respondiendo.
- `[ ]` **Limpieza**: Ejecutar `scripts/cleanup.sh` si el disco `/` tiene menos de 10GB libres.

## Tareas Eventuales
- `[ ]` **Auditoría de Seguridad**: Ejecutar `scripts/seguridad_check.sh` una vez por semana.
- `[ ]` **Backup**: Verificar que `scripts/backup_lucy_core.sh` se haya completado con éxito.

---
> [!NOTE]
> Lucy marcará con `[x]` las tareas completadas y reportará anomalías a Diego por Telegram de forma inmediata.
