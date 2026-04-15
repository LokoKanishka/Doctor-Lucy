# Revision de Pendientes - Doctora Lucy

**Fecha:** 2026-04-15 17:35 -03
**Alcance:** Doctor Lucy workspace, servicios locales, puertos, n8n, memoria y referencias historicas.

## Estado General

OPERATIVO con pendientes historicos depurados. La mayoria de las tareas antiguas eran estado viejo o pertenecian a proyectos externos. Tras recibir credencial sudo, el bloqueo de Ollama quedo resuelto. El pendiente Boot/Commit quedo implementado el 2026-04-15 18:58 -03 mediante gateway local + workflows n8n.

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
- **Boot/Commit como workflows n8n**: Resuelto el 2026-04-15 18:58 -03.
  - Backup previo: `n8n_backups/pre_boot_commit_20260415_1848/`.
  - Gateway local: `lucy-memory-gateway.service`, escuchando en `http://172.17.0.1:6970`.
  - Workflow activo: `LUCY - Boot Memory`, webhook `GET /webhook/lucy/boot`.
  - Workflow activo: `LUCY - Commit Memory`, webhook `POST /webhook/lucy/commit`.
  - Validacion: ambos webhooks devolvieron HTTP 200; Commit inserto registro smoke test id 20 en `memoria_core`.
- **Incidente de cuelgue/reinicio 2026-04-15**: Revisado y mitigado. Ver `diagnostics/incidente_20260415_colgada.md`.
  - `watcher-daemon.service` fue reparado con guard wrapper: no vuelve a fallar en loop si falta Cunningham.
  - El proyecto `/home/lucy-ubuntu/Escritorio/cunningham-naranja` no existe actualmente, por lo que el watcher no puede cumplir trabajo real hasta restaurar ese proyecto.
  - `doctor_lucy_n8n_openbind_backup_20260415_000948` quedo detenido y sin `restart=always` para evitar doble escritura SQLite.
  - Se creo `doctor_lucy_n8n_isolated_backup_20260415_1908`, clon aislado en `127.0.0.1:6979`, con SQLite propia.
- **Groq Fast Processor / Consultar Cerebro**: No existen en la instancia actual de `doctor_lucy_n8n`; no hay duplicado ni HTTP 500 reproducible. Si se necesitan, deben restaurarse desde `n8n_backups/workflows_json/`.
- **Repo externo NIN**: `/home/lucy-ubuntu/Escritorio/NIN` tiene muchos archivos no trackeados. No se modifico por politica de jurisdiccion; requiere orden explicita sobre NIN.

## Persistencia Final

- Guardado en bóveda SQLite: `n8n_data/boveda_lucy.sqlite`.
- Sincronizado al búnker JSONL: `data/lucy_bunker_log.jsonl`.
- Guardado en Knowledge Graph local: `memoria/agente_memoria.db`.
- Registrado en bitácoras: `memoria/bitacora_mantenimiento.md` y `docs/bitacora_mantenimiento.md`.
- Guardado remoto historico: rama `memoria/bunker` en GitHub.
- Política de secretos: la API key completa queda solo en la carpeta local de contraseñas, no en Git ni en reportes versionados.

## Boot/Commit Memoria - 2026-04-15 18:58 -03

- Servicio creado: `scripts/lucy_memory_gateway.py`.
- Servicio systemd user: `systemd/lucy-memory-gateway.service`.
- Rutas gateway:
  - `GET http://172.17.0.1:6970/healthz`
  - `GET http://172.17.0.1:6970/boot`
  - `POST http://172.17.0.1:6970/commit`
- Workflows fuente:
  - `workflows/LUCY__Boot_Memory.json`
  - `workflows/LUCY__Commit_Memory.json`
- Nota n8n: se requirio `webhookId` explicito para que n8n registrara rutas limpias `lucy/boot` y `lucy/commit`.

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

## Prueba Contenedores n8n 2026-04-15 18:17 -03

- `doctor_lucy_n8n`: OK. `GET /healthz` en `127.0.0.1:6969` devuelve `{"status":"ok"}`; editor HTTP 200; API `GET /api/v1/workflows` con la API key local devuelve 200 y lista vacia.
- `N8N-NiN-uso-exclusivo-del-proyecto-nin`: OK como servicio. `GET /healthz` en `127.0.0.1:5688` devuelve `{"status":"ok"}`; editor HTTP 200. Base con 67 workflows, 0 activos, 0 credenciales, 0 webhooks.
- `doctor_lucy_n8n_openbind_backup_20260415_000948`: Respondia OK internamente, pero compartia `/home/node/.n8n` con `doctor_lucy_n8n`. Se detuvo de forma reversible para evitar dos procesos n8n sobre la misma SQLite.
- No se ejecutaron workflows: NIN incluye flujos con efectos externos potenciales y no tiene credenciales cargadas; la prueba fue de infraestructura, API y consistencia de base.
