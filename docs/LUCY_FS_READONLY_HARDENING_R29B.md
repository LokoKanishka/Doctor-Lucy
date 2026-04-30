# Lucy FS Readonly Hardening R29B

Fecha: 2026-04-29

## Objetivo

Ejecutar tests borde de seguridad sobre `scripts/lucy_fs_readonly.py` antes de
considerar cualquier integracion con OpenClaw o Telegram.

## Regresion

Pruebas ejecutadas:

- `python3 -m py_compile scripts/lucy_fs_readonly.py`
- `python3 scripts/lucy_fs_readonly.py read_lines --path scripts/lucy_openclaw_bridge.py --start 138 --end 168`

Resultado:

- `py_compile`: OK
- `read_lines` valido: OK

## Rechazos

Pruebas ejecutadas y exit codes:

- `.env`:
  - comando: `read_lines --path .env --start 1 --end 2`
  - resultado: rechazado
  - exit: `2`

- `n8n_data`:
  - comando: `read_lines --path n8n_data/daemon.pid.dead.20260429_185731.bak --start 1 --end 2`
  - resultado: rechazado
  - exit: `2`

- traversal:
  - comando: `read_lines --path ../.bashrc --start 1 --end 2`
  - resultado: rechazado
  - exit: `2`

- absolute path:
  - comando: `read_lines --path /home/lucy-ubuntu/.openclaw/openclaw.json --start 1 --end 2`
  - resultado: rechazado
  - exit: `2`

- rango excesivo:
  - comando: `read_lines --path scripts/lucy_openclaw_bridge.py --start 1 --end 300`
  - resultado: rechazado
  - exit: `2`

- symlink externo:
  - symlink temporal dentro del repo apuntando a `/etc/hosts`
  - resultado: rechazado con `path escapes repository root`
  - exit: `2`

## Limpieza

- symlink temporal borrado: si
- status final: limpio respecto de este tramo; solo permanecen no trackeados
  previos ajenos al test

## Seguridad

- OpenClaw tocado: no
- Telegram tocado: no
- tokens impresos: no
- archivos fuera del repo leidos: no

## Estado

`scripts/lucy_fs_readonly.py` queda validado para estos casos borde locales.
Sigue siendo una tool local, no integrada todavia a OpenClaw ni a Telegram.
