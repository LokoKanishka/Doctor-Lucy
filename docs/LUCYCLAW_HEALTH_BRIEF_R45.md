# LucyClaw Health Brief R45

Date: 2026-05-01

## Objective

Implement one deterministic compact read-only command for LucyClaw:

- `/health_brief`

The command is a Telegram-friendly summary layer on top of R44 `/health_report`. It does not add host powers, read new surfaces, or broaden permissions.

## Relation to R44

R44 already aggregates the bounded machine, service, and log wrappers into `/health_report`.

R45 reuses that existing safe report and compresses it into a small JSON response suitable for Telegram:

- keep `overall`
- keep a short `brief`
- keep bounded warning text
- keep one `next` recommendation
- omit heavy `data`
- omit full log lines
- omit model/auth raw output

## Command Implemented

Created:

- `scripts/lucy_health_brief_command.py`
- `openclaw_plugins/lucy-health-brief-command/package.json`
- `openclaw_plugins/lucy-health-brief-command/openclaw.plugin.json`
- `openclaw_plugins/lucy-health-brief-command/index.js`

Telegram/OpenClaw command:

- `/health_brief`

## Output Shape

Expected compact JSON:

```json
{
  "ok": true,
  "command": "health_brief",
  "overall": "ok",
  "brief": "OK: máquina, GPU, disco, OpenClaw, Docker, Ollama y n8n sanos.",
  "warnings": [],
  "next": "No reparar. Usar /health_report para detalle."
}
```

When warnings exist, the command should still stay compact and omit the heavy `data` tree from `/health_report`.

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
- no unbounded logs
- no raw `openclaw models status --json` output

The wrapper only consumes the sanitized R44 JSON and emits a smaller sanitized JSON.

## Tests

Required local tests:

- `python3 -m py_compile scripts/lucy_health_brief_command.py`
- `node --check openclaw_plugins/lucy-health-brief-command/index.js`
- `python3 scripts/lucy_health_brief_command.py`
- `python3 scripts/lucy_health_report_command.py`

## Reload / Rollback

If the plugin must be loaded into the live OpenClaw gateway, that reload requires separate authorization.

Suggested restart only after approval:

```bash
systemctl --user restart openclaw-gateway.service
```

Rollback:

- revert the four R45 files above
- restart the gateway only if the plugin had already been loaded

## No-Mutation Confirmation

This tranche is read-only in capability design:

- no memory changes
- no n8n workflow changes
- no vault changes
- no personality changes
- no `.env` reads
- no token printing
- no repair
