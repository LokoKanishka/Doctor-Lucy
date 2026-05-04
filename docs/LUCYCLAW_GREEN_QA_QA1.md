# LucyClaw Green QA QA1

Date: 2026-05-01

## Objective

Implement one unified smoke verifier for the LucyClaw green layer:

- `scripts/verify_lucyclaw_green_commands.py`

The verifier exists to prove that the current read-only command surface still behaves safely after future changes.

## Scope

The script validates the current green commands:

- `/fs_read`
- `/sys_status`
- `/gpu_status`
- `/disk_status`
- `/process_status`
- `/openclaw_health`
- `/docker_status`
- `/ollama_status`
- `/n8n_health`
- `/service_status`
- `/log_tail`
- `/health_report`
- `/health_brief`
- `/lucy_capabilities`
- `/lucy_next_step`
- `/repo_map`
- `/plan_brief`
- `/risk_check`
- `/permission_brief`
- `/change_plan`
- `/scaffold_plan`

## What QA1 Checks

The verifier runs wrappers locally and checks:

- valid JSON output
- expected `command` fields
- expected top-level keys
- bounded log counts where applicable
- no heavy `data` block in `health_brief`
- no full log lines in `health_brief`
- no `.env` path leaks
- no obvious secret/token assignments
- no legacy hardcoded `doctor de lucy` paths
- no workflow detail leakage in `n8n_health`

## Security Model

QA1 does not add runtime powers:

- no `sudo`
- no shell freedom
- no `.env` reads
- no memory access
- no n8n workflow access
- no vault access
- no personality edits

It only executes the already approved green wrappers.

## Usage

```bash
python3 scripts/verify_lucyclaw_green_commands.py
```

Expected success shape:

```json
{
  "ok": true,
  "command": "verify_lucyclaw_green_commands",
  "verified": [...]
}
```

## Recommendation

Run QA1:

- after each new Lucy green command
- before pushing multi-command refactors
- after runtime/plugin path changes

This is the first step toward turning policy promises into repeatable evidence.
