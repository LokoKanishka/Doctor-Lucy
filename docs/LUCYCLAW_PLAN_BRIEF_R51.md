# LucyClaw Plan Brief R51

Date: 2026-05-03

## Objective

`R51` adds `/plan_brief <request>`, a deterministic read-only planning command that prepares a safe task brief without touching code, runtime, memory, or credentials.

## Examples

- `/plan_brief agregar comando para ver ultimas docs Lucy`
- `/plan_brief revisar riesgo de nuevo comando de status`
- `/plan_brief preparar smoke de plugin read-only`

## Output Contract

The command returns compact JSON with:

- `decision = PLAN_ONLY`
- `scope = read-only`
- `files_to_review`
- `risks`
- `permissions_needed`
- `checks`
- `tests`
- `acceptance_criteria`

The command may classify the target task as green, yellow, or red, but the command itself remains read-only.

## Security Limits

- no file writes
- no plugin install
- no gateway restart
- no `.env`
- no auth material
- no memory / vault / personality
- no n8n internals
- no shell freedom
- no sudo

## Relationship To Existing Commands

- `/repo_map` orients the tree
- `/doc_brief` summarizes safe docs or command files
- `/plan_brief` turns an idea into a bounded work brief
- `/risk_check` classifies the target action
- `/permission_brief` explains authorization needs

## Tests

```bash
python3 -m py_compile scripts/lucy_plan_brief_command.py scripts/lucy_planning_readonly.py
node --check openclaw_plugins/lucy-plan-brief-command/index.js
python3 scripts/lucy_plan_brief_command.py "agregar comando para ver ultimas docs Lucy"
python3 scripts/verify_lucyclaw_green_commands.py
python3 scripts/verify_lucyclaw_security_policy.py
```

## Non-Mutation

`/plan_brief` only analyzes the request and returns a brief. It does not mutate repo or runtime state.
