# LucyClaw Permission Brief R53

Date: 2026-05-03

## Objective

`R53` adds `/permission_brief <request>`, a deterministic read-only command that explains which authorizations would be required before executing a task.

## Examples

- `/permission_brief agregar comando para ver ultimas docs Lucy`
- `/permission_brief reiniciar openclaw gateway`
- `/permission_brief preparar fix de plugin`

## Output Contract

The command returns compact JSON with:

- `permissions_needed`
- `authorization_mode`
- `grouped_authorization_recommended`
- `checks_before_execution`
- `blocked_zones`

## Why It Exists

LucyClaw needs a compact way to say:

- what would need approval
- what stays forbidden
- how to group authorization sensibly

before any yellow execution is even considered.

## Security Limits

- no execution
- no writes
- no installs
- no restarts
- no env files
- no auth material
- no memory / vault / personality
- no n8n internals

## Tests

```bash
python3 -m py_compile scripts/lucy_permission_brief_command.py scripts/lucy_planning_readonly.py
node --check openclaw_plugins/lucy-permission-brief-command/index.js
python3 scripts/lucy_permission_brief_command.py "agregar comando para ver ultimas docs Lucy"
python3 scripts/verify_lucyclaw_green_commands.py
python3 scripts/verify_lucyclaw_security_policy.py
```
