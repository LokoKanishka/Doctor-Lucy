# Revision de Pendientes - Doctora Lucy

**Fecha:** 2026-04-15 17:35 -03
**Alcance:** Doctor Lucy workspace, servicios locales, puertos, n8n, memoria y referencias historicas.

## Estado General

OPERATIVO con pendientes historicos depurados. La mayoria de las tareas antiguas eran estado viejo o pertenecian a proyectos externos. Tras recibir credencial sudo, el bloqueo de Ollama quedo resuelto; queda pendiente solo lo que requiere API key o decision explicita de restauracion/importacion.

## Resuelto / Cerrado

- **Migracion NVMe**: Cerrada. `/` esta en `/dev/nvme0n1p2`, 1.9T totales, 863G usados, 933G libres, 49%.
- **Monitoreo sda2**: Obsoleto. El disco raiz actual es `/dev/nvme0n1p2`.
- **doctor_lucy_n8n**: Activo y saludable en `127.0.0.1:6969`; `/healthz` responde `{"status":"ok"}`.
- **n8n-lucy legacy**: No esta corriendo como contenedor separado. No se observa loop activo por encryption key.
- **Puerto 7851**: No esta escuchando.
- **Ollama puerto 11434**: Resuelto. El override systemd ahora define `OLLAMA_HOST=127.0.0.1:11434`; `ss` confirma escucha solo en localhost y `GET /api/tags` responde 18 modelos.
- **Lucy Fusion/lucy_fusion**: No hay stack activo.
- **nin_demon/send_cvs**: No hay procesos activos.
- **Subagente de prueba**: `_test_subagent/task.md` completo y `_test_subagent/LUCY_REPORT.md` presente.

## Pendientes Reales

- **API key n8n**: Resuelto el 2026-04-15. Se creo una API key nueva para `doctor_lucy_n8n`, validada con `GET /api/v1/workflows` (`200 OK`). La clave completa quedo fuera del repo en `/home/lucy-ubuntu/Escritorio/Malorms Documentos/contraseñas/n8n_api_key_doctor_lucy_20260415.txt` con permisos `600`.
- **Boot/Commit como workflows n8n**: La base `n8n_data/database.sqlite` tenia 0 workflows, 0 credenciales y 0 webhooks. La API ya esta desbloqueada por la key nueva, pero los flujos Boot/Commit reales requieren una decision tecnica adicional: el contenedor de n8n no trae `sqlite3` ni `python3`, por lo que un workflow nativo no puede leer/escribir `boveda_lucy.sqlite` sin agregar una dependencia, un microservicio local o cambiar el diseno a HTTP/script externo.
  - Antes de modificar n8n productivo hay que hacer backup local de la base o export de workflows.
- **Groq Fast Processor / Consultar Cerebro**: No existen en la instancia actual de `doctor_lucy_n8n`; no hay duplicado ni HTTP 500 reproducible. Si se necesitan, deben restaurarse desde `n8n_backups/workflows_json/`.
- **Repo externo NIN**: `/home/lucy-ubuntu/Escritorio/NIN` tiene muchos archivos no trackeados. No se modifico por politica de jurisdiccion; requiere orden explicita sobre NIN.

## Persistencia Final

- Guardado en bóveda SQLite: `n8n_data/boveda_lucy.sqlite`.
- Sincronizado al búnker JSONL: `data/lucy_bunker_log.jsonl`.
- Guardado en Knowledge Graph local: `memoria/agente_memoria.db`.
- Registrado en bitácoras: `memoria/bitacora_mantenimiento.md` y `docs/bitacora_mantenimiento.md`.
- Guardado remoto: rama `memoria/bunker` en GitHub.
- Política de secretos: la API key completa queda solo en la carpeta local de contraseñas, no en Git ni en reportes versionados.

## Comandos Ejecutados

- `docker ps --format ...`
- `ss -ltnp`
- `df -h / /home /tmp`
- `curl http://127.0.0.1:6969/healthz`
- `curl http://127.0.0.1:6969/api/v1/workflows`
- `sqlite3 n8n_data/database.sqlite ...`
- `ps -ef | rg 'send_cvs|nin_demon|lucy_fusion|searxng|ollama serve|n8n'`
- `git status --short --branch`
- `systemctl cat ollama`
- `systemctl status ollama --no-pager`
- `curl http://127.0.0.1:11434/api/tags`
- `curl http://127.0.0.1:6969/api/v1/workflows` con `X-N8N-API-KEY`
