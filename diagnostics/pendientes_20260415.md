# Revision de Pendientes - Doctora Lucy

**Fecha:** 2026-04-15 17:35 -03
**Alcance:** Doctor Lucy workspace, servicios locales, puertos, n8n, memoria y referencias historicas.

## Estado General

OPERATIVO con pendientes historicos depurados. La mayoria de las tareas antiguas eran estado viejo o pertenecian a proyectos externos. Los bloqueos reales restantes requieren credenciales o sudo.

## Resuelto / Cerrado

- **Migracion NVMe**: Cerrada. `/` esta en `/dev/nvme0n1p2`, 1.9T totales, 863G usados, 933G libres, 49%.
- **Monitoreo sda2**: Obsoleto. El disco raiz actual es `/dev/nvme0n1p2`.
- **doctor_lucy_n8n**: Activo y saludable en `127.0.0.1:6969`; `/healthz` responde `{"status":"ok"}`.
- **n8n-lucy legacy**: No esta corriendo como contenedor separado. No se observa loop activo por encryption key.
- **Puerto 7851**: No esta escuchando.
- **Lucy Fusion/lucy_fusion**: No hay stack activo.
- **nin_demon/send_cvs**: No hay procesos activos.
- **Subagente de prueba**: `_test_subagent/task.md` completo y `_test_subagent/LUCY_REPORT.md` presente.

## Pendientes Reales

- **Ollama puerto 11434**: Sigue escuchando en `*`. Causa confirmada: `/etc/systemd/system/ollama.service.d/override.conf` define `OLLAMA_HOST=0.0.0.0`.
  - Correccion recomendada:
    ```bash
    sudo cp /etc/systemd/system/ollama.service.d/override.conf /etc/systemd/system/ollama.service.d/override.conf.backup-$(date +%Y%m%d-%H%M%S)
    printf '[Service]\nEnvironment="OLLAMA_HOST=127.0.0.1:11434"\n' | sudo tee /etc/systemd/system/ollama.service.d/override.conf
    sudo systemctl daemon-reload
    sudo systemctl restart ollama
    ss -ltnp | grep 11434
    ```
  - Bloqueo: `sudo` requiere password.
- **Boot/Commit como workflows n8n**: La base `n8n_data/database.sqlite` tiene 0 workflows, 0 credenciales y 0 webhooks. La API responde `401` y exige `X-N8N-API-KEY`.
  - Resolver requiere API key n8n o importacion manual desde la UI.
  - Antes de modificar n8n productivo hay que hacer backup local de la base o export de workflows.
- **Groq Fast Processor / Consultar Cerebro**: No existen en la instancia actual de `doctor_lucy_n8n`; no hay duplicado ni HTTP 500 reproducible. Si se necesitan, deben restaurarse desde `n8n_backups/workflows_json/`.
- **Repo externo NIN**: `/home/lucy-ubuntu/Escritorio/NIN` tiene muchos archivos no trackeados. No se modifico por politica de jurisdiccion; requiere orden explicita sobre NIN.

## Comandos Ejecutados

- `docker ps --format ...`
- `ss -ltnp`
- `df -h / /home /tmp`
- `curl http://127.0.0.1:6969/healthz`
- `curl http://127.0.0.1:6969/api/v1/workflows`
- `sqlite3 n8n_data/database.sqlite ...`
- `ps -ef | rg 'send_cvs|nin_demon|lucy_fusion|searxng|ollama serve|n8n'`
- `git status --short --branch`

