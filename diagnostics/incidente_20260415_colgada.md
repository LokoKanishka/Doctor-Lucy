# Incidente 2026-04-15 - Cuelgue/Reinicio de Maquina

**Fecha de revision:** 2026-04-15 18:41 -03  
**Alcance:** host local, Docker, n8n, memoria Lucy y servicios systemd de usuario.

## Hallazgos

- La maquina habia reiniciado: `uptime` marcaba ~6 minutos al iniciar la revision.
- `journalctl --list-boots` mostro varios boots cortos durante la madrugada y un corte entre `18:23:51 -03` y `18:35:15 -03`.
- No se observaron senales claras de OOM, disco lleno o presion sostenida de Docker.
- Estado al revisar:
  - RAM: 124 GiB total, ~7 GiB en uso, swap 0.
  - Disco raiz: 49% usado.
  - Docker: contenedores con bajo consumo.
- `watcher-daemon.service` estaba fallando en bucle cada ~5 segundos con `status=203/EXEC`, apuntando a `/home/lucy-ubuntu/Escritorio/cunningham-naranja/scripts/watcher_daemon.sh`.
- Justo antes del corte aparecieron operaciones de instalacion/actualizacion (`apt-get update`, `dpkg -i /tmp/code_latest_amd64.deb`, `npm install -g @openai/codex@latest`) y mensajes graficos/VAAPI de Chrome/GNOME.
- `nvidia-smi` fallo inicialmente con un formato de consulta no compatible, pero luego respondio correctamente: RTX 5090, 32 GB VRAM, ~1.1 GB usados, 53 C.

## Causa Probable

No hay una firma unica de kernel panic u OOM en los logs disponibles. La causa mas probable es una combinacion de reinicio/corte durante operaciones de instalacion y una sesion grafica cargada, con ruido adicional del `watcher-daemon.service` roto reiniciando cientos de veces.

## Acciones Correctivas

- Se reparo `watcher-daemon.service` con un guard wrapper: si `/home/lucy-ubuntu/Escritorio/cunningham-naranja` no existe, sale limpio sin loop. El proyecto fuente no existe actualmente en el disco, por lo que no puede ejecutar un watcher real hasta que sea restaurado.
- Se detuvo `doctor_lucy_n8n_openbind_backup_20260415_000948`, que compartia SQLite con `doctor_lucy_n8n`, y se le cambio `restart=always` a `restart=no` para que no reviva de forma peligrosa.
- Se creo un clon n8n aislado y funcional: `doctor_lucy_n8n_isolated_backup_20260415_1908`, con copia propia de SQLite y puerto `127.0.0.1:6979`.
- Se creo y habilito `lucy-memory-gateway.service`.
- Se importaron y activaron workflows n8n de Boot/Commit para memoria.

## Prevencion

- Mantener deshabilitados servicios user que apunten a rutas inexistentes.
- Evitar dos contenedores n8n escribiendo sobre el mismo volumen SQLite.
- Si se necesita usar el backup de n8n, usar el clon aislado `doctor_lucy_n8n_isolated_backup_20260415_1908` en puerto `6979`, no el contenedor viejo `openbind`.
- Antes de modificar n8n productivo, conservar backup local de `database.sqlite` y `boveda_lucy.sqlite`.
- Si se repite el cuelgue, revisar especificamente GNOME/GPU y logs previos al boot anterior con:
  - `journalctl -b -1 -p warning..alert --no-pager`
  - `journalctl -k -b -1 --no-pager`
  - `nvidia-smi`
