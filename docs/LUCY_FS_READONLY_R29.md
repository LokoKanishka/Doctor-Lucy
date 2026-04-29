# Lucy FS Readonly R29

Fecha: 2026-04-29

## Objetivo

Crear una herramienta local estrictamente read-only para buscar y leer archivos
dentro del repo `Doctor-Lucy`, sin integrarla todavia a OpenClaw o Telegram.

## Script

- Archivo: `scripts/lucy_fs_readonly.py`
- Tipo: CLI local con salida JSON
- Acciones:
  - `find_files`
  - `grep_text`
  - `read_lines`

## Guardrails

- Base path fija al repo derivada desde la ubicacion del script.
- Rechaza rutas absolutas.
- Rechaza `..`.
- Rechaza rutas resueltas fuera del repo.
- Rechaza symlinks que salgan del repo.
- Excluye `.git`, `.agents`, `n8n_data`, `__pycache__`, `.venv`, `.voice_env`,
  `node_modules`.
- Excluye `.env`, `.sqlite`, `.log`, sidecars SQLite y nombres con `backup` o
  `secret`.
- Extensiones permitidas:
  `.py`, `.sh`, `.md`, `.txt`, `.json`, `.yml`, `.yaml`, `.toml`, `.html`,
  `.css`, `.js`.
- `max-results` por defecto 20, maximo 50.
- `read_lines` limita a 120 lineas por request.
- Exit code:
  - `0` exito
  - `2` error de validacion

## Pruebas de exito

Se ejecutaron:

- `python3 -m py_compile scripts/lucy_fs_readonly.py`
- `python3 scripts/lucy_fs_readonly.py find_files --query openclaw --max-results 10`
- `python3 scripts/lucy_fs_readonly.py grep_text --query delegate_mission --path scripts --max-results 10`
- `python3 scripts/lucy_fs_readonly.py read_lines --path scripts/lucy_openclaw_bridge.py --start 138 --end 168`

Resultado esperado:

- `find_files` devuelve rutas relativas reales.
- `grep_text` devuelve coincidencias con numero de linea.
- `read_lines` devuelve lineas exactas del rango pedido.

## Pruebas de rechazo

Se ejecutan:

- `read_lines --path ../.bashrc --start 1 --end 2`
- `read_lines --path /home/lucy-ubuntu/.openclaw/openclaw.json --start 1 --end 2`
- `grep_text --query TELEGRAM_BOT_TOKEN --path . --max-results 5`

Resultado esperado:

- traversal rechazado;
- ruta absoluta rechazada;
- no se lee `.env`;
- si aparecen menciones publicas del texto buscado en docs o scripts, pueden
  devolverse sin valores secretos.

## Estado

- Herramienta local creada.
- No integrada todavia a Telegram.
- No integrada todavia a OpenClaw MCP/tools.
- No toca `~/.openclaw`.
- No toca servicios.
