# LucyClaw Capabilities R46

Date: 2026-05-01

## Objective

Implement one deterministic read-only command for LucyClaw:

- `/lucy_capabilities`

The command exposes the current operational map of LucyClaw in compact JSON:

- what is allowed without asking first
- what requires explicit authorization
- what is prohibited by policy

## Relation to R45

R45 added `/health_brief` as a compact runtime status summary.

R46 does not add new powers. It adds operational self-description so Lucy can explain:

- what she can do now
- what needs approval
- what stays off-limits

## Command Implemented

Created:

- `scripts/lucy_capabilities_command.py`
- `openclaw_plugins/lucy-capabilities-command/package.json`
- `openclaw_plugins/lucy-capabilities-command/openclaw.plugin.json`
- `openclaw_plugins/lucy-capabilities-command/index.js`

Telegram/OpenClaw command:

- `/lucy_capabilities`

## Design

The wrapper is deterministic and static:

- no system inspection
- no shell freedom
- no `.env` reads
- no memory access
- no n8n workflow access
- no vault access
- no secret printing

It only returns the already confirmed capability map and policy limits.

## Output Shape

Expected compact JSON:

```json
{
  "ok": true,
  "command": "lucy_capabilities",
  "stage": "R46",
  "green": {
    "description": "Acciones read-only permitidas sin autorización previa.",
    "commands": ["/fs_read", "/health_brief", "/health_report", "/lucy_capabilities"]
  },
  "yellow": {
    "description": "Acciones que requieren autorización explícita antes de ejecutarse.",
    "examples": ["instalar o registrar plugins", "reiniciar OpenClaw gateway"]
  },
  "red": {
    "description": "Acciones prohibidas salvo autorización explícita excepcional.",
    "limits": ["no sudo", "no .env", "no memoria"]
  },
  "next": "Usar /health_brief para estado rápido o /health_report para detalle."
}
```

## Security Limits

Preserved:

- no memory access
- no n8n workflow access
- no vault access
- no personality edits
- no `.env` access
- no token output
- no shell freedom
- no `sudo`
- no `/bash`
- no `/exec`
- no `/mcp`
- no model/provider changes
- no repair logic
- no dependency installation

## Tests

Required local tests:

- `python3 -m py_compile scripts/lucy_capabilities_command.py`
- `node --check openclaw_plugins/lucy-capabilities-command/index.js`
- `python3 scripts/lucy_capabilities_command.py`

## Reload / Rollback

To activate the plugin in the live gateway:

```bash
openclaw plugins install --link /home/lucy-ubuntu/Escritorio/doctora-lucy/openclaw_plugins/lucy-capabilities-command
systemctl --user restart openclaw-gateway.service
```

Rollback:

- revert the four R46 files above
- remove or disable the plugin from OpenClaw config if needed
- restart the gateway only if the plugin had already been loaded

## No-Mutation Confirmation

This tranche is policy/reporting only:

- no memory changes
- no n8n workflow changes
- no vault changes
- no personality changes
- no `.env` reads
- no token printing
- no repair
