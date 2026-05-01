# LucyClaw Next Step Gate - R48

Date: 2026-05-01

## Objective

`R48` adds `/lucy_next_step`, a read-only advance gate for LucyClaw.

It does not execute actions. It only decides whether the system is:

- `READY`
- `WARN`
- `BLOCK`

## What It Evaluates

The wrapper checks, in bounded read-only mode:

- `git status --short --branch`
- `python3 scripts/verify_lucyclaw_green_commands.py`
- `python3 scripts/verify_lucyclaw_security_policy.py`
- `python3 scripts/lucy_health_brief_command.py`
- `python3 scripts/lucy_capabilities_command.py`

## Decisions

### READY

Use when:

- git is clean
- QA1 passes
- SEC1 passes without violations
- health is `ok` or only known non-critical `warn`

### WARN

Use when:

- git is clean
- QA1 passes
- SEC1 passes
- health is `warn`

This keeps Lucy in diagnosis mode and recommends reading `/health_report` before adding new capability work.

### BLOCK

Use when:

- git is dirty
- QA1 fails
- SEC1 fails
- health is `error`

## What It Does Not Do

`/lucy_next_step` does not:

- repair
- restart
- install plugins
- commit
- push
- edit runtime config
- touch memory
- touch `n8n` workflows
- touch `.env`

## Relation To Existing Commands

- `/health_brief` provides compact health
- `/lucy_capabilities` provides current allowed/blocked map
- `/lucy_next_step` decides whether it is safe to prepare the next tranche

## Tests

```bash
python3 -m py_compile scripts/lucy_next_step_command.py
node --check openclaw_plugins/lucy-next-step-command/index.js
python3 scripts/lucy_next_step_command.py
python3 scripts/verify_lucyclaw_security_policy.py
python3 scripts/verify_lucyclaw_green_commands.py
```

## Security Limits

- `subprocess` only
- `shell=False`
- bounded timeouts
- compact JSON only
- no stdout dump of raw child output on success

## Rollback

Rollback is file-level revert plus plugin unload/reload if the plugin was installed.

## No-Mutation Note

`R48` is a safe gate. It recommends whether to proceed, diagnose, or hold. It does not execute the next step itself.
