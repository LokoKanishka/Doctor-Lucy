# Lucy FS MCP Wrapper R31

Fecha: 2026-04-29

## Objetivo

Exponer `lucy_fs_readonly.py` como tools MCP stdio locales, sin tocar Telegram
real ni la configuracion principal de OpenClaw.

## Wrapper

- Script: `scripts/lucy_fs_mcp_server.py`
- Tipo: servidor MCP stdio minimo
- Protocolo implementado:
  - `initialize`
  - `tools/list`
  - `tools/call`
- Tools expuestas:
  - `lucy_find_files`
  - `lucy_grep_text`
  - `lucy_read_lines`

## Diseño

- El wrapper no usa dependencias externas.
- Cada tool llama a `scripts/lucy_fs_readonly.py` via subprocess controlado.
- No usa `shell=True`.
- La salida de cada tool es JSON compacto dentro de `content[].text`.
- Los errores del helper se preservan como JSON y `isError=true`.
- No escribe archivos ni logs.

## Pruebas locales

Ejecutadas:

- `python3 -m py_compile scripts/lucy_fs_readonly.py scripts/lucy_fs_mcp_server.py`
- `python3 scripts/test_lucy_fs_mcp_server.py`
- `python3 scripts/lucy_fs_mcp_server.py --help`

Validaciones:

- `initialize`: OK
- `tools/list`: OK
- `lucy_grep_text`: devuelve coincidencias reales para `delegate_mission`
- `lucy_read_lines`: devuelve linea 138 real de `scripts/lucy_openclaw_bridge.py`
- traversal `../.bashrc`: rechazado

## Perfil aislado OpenClaw

Se inspecciono:

- `openclaw mcp set --help`
- `openclaw --profile lucy-fs-test mcp list --json`

Resultado:

- `mcp set` fue claro y acepto el formato:
  `{"command":"python3","args":["/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_fs_mcp_server.py"]}`
- Se registro el server `lucy-fs-readonly` solo en:
  `/home/lucy-ubuntu/.openclaw-lucy-fs-test/openclaw.json`
- `openclaw --profile lucy-fs-test mcp list --json`: OK, muestra
  `lucy-fs-readonly`
- `openclaw --profile lucy-fs-test mcp show --json`: OK, muestra command/args
- `openclaw mcp list --json` en el perfil principal sigue devolviendo `{}`.

## Seguridad

- `~/.openclaw` principal: no tocado
- Telegram real: no tocado
- gateway principal: no reiniciado
- tokens: no impresos
- lectura fuera del repo: no

## Riesgos

- El wrapper depende del contrato JSON actual de `lucy_fs_readonly.py`
- El siguiente tramo debe verificar que OpenClaw consuma bien el MCP desde un
  perfil paralelo antes de pensar en Telegram

## Proximo R32

- Probar llamada de tool desde OpenClaw usando el perfil `lucy-fs-test`
- Verificar lectura exacta via MCP sin Telegram real
- Confirmar que el resultado coincide con verificacion directa de Codex
