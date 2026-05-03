# LucyClaw Change Plan R54

Date: 2026-05-03

## Objective

`R54` adds `/change_plan <request>`, a deterministic read-only command that turns a change request into a technical plan without writing files, installing plugins, restarting services, or touching sensitive zones.

## Output Contract

The command returns compact JSON with:

- `decision = PLAN_ONLY`
- `risk`
- `change_type`
- `files_to_review`
- `files_to_create`
- `files_to_modify`
- `permissions_needed`
- `tests`
- `acceptance_criteria`
- `rollback`
- `blocked_actions`
- `safe_next`

## Risk Model

- `GREEN`: lectura, documentación o planificación sin runtime
- `YELLOW`: edición de código, plugin, restart, commit/push
- `RED`: `.env`, tokens, memoria, n8n workflows/credentials, sudo, shell libre, borrado, reparación automática

## Security Limits

- no file writes
- no plugin install
- no gateway restart
- no commit
- no `.env`
- no auth material
- no memory / vault / personality
- no n8n internals
- no shell freedom
- no sudo

## Relationship To Planning Layer

- `/plan_brief` arma el brief general
- `/risk_check` clasifica riesgo
- `/permission_brief` resume permisos necesarios
- `/change_plan` consolida el plano técnico de cambio, pero no ejecuta nada

## Tests

```bash
python3 -m py_compile scripts/lucy_planning_readonly.py
python3 -m py_compile scripts/lucy_change_plan_command.py
node --check openclaw_plugins/lucy-change-plan-command/index.js
python3 scripts/lucy_change_plan_command.py "agregar comando read-only para listar docs Lucy"
python3 scripts/lucy_change_plan_command.py "reiniciar openclaw gateway"
python3 scripts/lucy_change_plan_command.py "tocar .env"
python3 scripts/verify_lucyclaw_green_commands.py
python3 scripts/verify_lucyclaw_security_policy.py
```

## Non-Mutation

`/change_plan` only analyzes the request and returns a structured technical plan. It never executes the plan.
