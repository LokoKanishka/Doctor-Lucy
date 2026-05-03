# LucyClaw Risk Check R52

Date: 2026-05-03

## Objective

`R52` adds `/risk_check <request>`, a deterministic read-only classifier that labels a requested task as green, yellow, or red before any execution.

## Examples

- `/risk_check reiniciar openclaw gateway`
- `/risk_check agregar comando para ver ultimas docs Lucy`
- `/risk_check tocar env-files`

## Output Contract

The command returns compact JSON with:

- `risk`
- `authorization`
- `summary`
- `reasons`
- `checks_previos`
- `rollback`
- `safe_alternatives`

## Policy Intent

This keeps LucyClaw from treating:

- reading docs
- changing code
- restarting gateway
- touching forbidden zones

as if they were equivalent operations.

## Security Limits

- no execution
- no runtime mutation
- no file writes
- no auth material
- no env files
- no memory / vault / personality
- no n8n internals

## Tests

```bash
python3 -m py_compile scripts/lucy_risk_check_command.py scripts/lucy_planning_readonly.py
node --check openclaw_plugins/lucy-risk-check-command/index.js
python3 scripts/lucy_risk_check_command.py "reiniciar openclaw gateway"
python3 scripts/verify_lucyclaw_green_commands.py
python3 scripts/verify_lucyclaw_security_policy.py
```
