# LucyClaw Current State

Date: 2026-05-01

## 1. Current Short State

- Expected branch: `memoria/bunker`
- Last known healthy commit: `e98120e` `chore(lucyclaw): clean local hygiene leftovers`
- Current operational status: green read-only layer is solid and repeatably verifiable
- Immediate recommendation: keep `QA1` and `SEC1` as explicit non-regression gates and use `TPL1` before adding new functional powers

## 2. Confirmed Healthy Base

The current stable baseline is:

- OpenClaw gateway healthy
- Telegram healthy
- Lucy plugins execute from `/home/lucy-ubuntu/Escritorio/doctora-lucy`
- `/health_report` active
- `/health_brief` active
- `/lucy_capabilities` active
- QA1 verifier available

This means Lucy currently has a real bounded green zone, not just a documented one.

## 3. Active Green Commands

### Safe Bounded Read

- `/fs_read`

Usage:

- exact line-range reading from allowed repo files only

### Machine Status

- `/sys_status`
- `/gpu_status`
- `/disk_status`
- `/process_status`

Usage:

- host, GPU, disk, and bounded process inspection

### Services and Logs

- `/openclaw_health`
- `/docker_status`
- `/ollama_status`
- `/n8n_health`
- `/service_status`
- `/log_tail`

Usage:

- gateway/service health, bounded container visibility, bounded sanitized logs

### Reports

- `/health_report`
- `/health_brief`

Usage:

- aggregate diagnostic report
- compact Telegram-friendly summary

### Capability / Policy Map

- `/lucy_capabilities`

Usage:

- deterministic explanation of green, yellow, and red operational boundaries

## 4. Green / Yellow / Red Map

### Green

Allowed without prior authorization:

- bounded file reading
- diagnostics
- machine status
- service status
- sanitized bounded logs
- aggregate reporting
- local QA verification

### Yellow

Require explicit authorization before execution:

- plugin installation or registration
- OpenClaw gateway restart
- code or config edits
- repair actions
- commit and push operations
- desktop operation

### Red

Prohibited except for exceptional explicit authorization:

- `sudo`
- shell freedom
- `/bash`
- `/exec`
- `/mcp` as a shortcut around policy
- `.env` access
- token exposure
- memory edits
- `n8n` workflow access
- vault access
- personality changes
- arbitrary deletion
- automatic repair

## 5. Active Lucy Plugins

Currently active Lucy plugin family:

- `lucy-fs-readonly-command`
- `lucy-machine-status-command`
- `lucy-service-status-command`
- `lucy-health-report-command`
- `lucy-health-brief-command`
- `lucy-capabilities-command`

Expected implementation pattern:

- Python wrapper
- separate OpenClaw plugin
- `spawn(..., shell:false)`
- relative path resolution via `import.meta.url` + `resolve`
- compact JSON output
- local tests
- tranche documentation
- authorized reload and smoke

## 6. Mandatory Minimum QA

After touching any Lucy green command or Lucy plugin, run:

```bash
python3 scripts/verify_lucyclaw_green_commands.py
python3 scripts/verify_lucyclaw_security_policy.py
```

QA1 verifies:

- valid JSON
- expected `command` fields
- expected top-level keys
- bounded log counts
- no heavy `data` block in `health_brief`
- no full log lines in `health_brief`
- no `.env` path leaks
- no obvious secret or token assignments
- no legacy `doctor de lucy` path regression
- no workflow detail leakage in `n8n_health`

SEC1 verifies:

- no `shell:true`
- no `shell=True`
- no `child_process.exec` or `execSync`
- no operational `.env` access
- no legacy runtime tree reintroduction
- no direct `n8n` workflow / credential / SQLite access in green commands
- no repair or deletion primitives in green commands
- no unexpected `acceptsArgs:true` outside explicit allowlists

QA1 plus SEC1 are the current minimum gates for the green layer.

## 7. Local Hygiene State

`HYG2` resolved the previously known local pending items in a controlled way:

- `.gitignore` now keeps the local archive and `n8n_backups/` out of version control without duplicating older rules
- `docs/OPENCLAW_REBUILD_1A_PROFILE.md` is preserved as a short historical rebuild note
- `.agents/archive_openclaw_scope_fix_20260429_153235/` remains local-only and intentionally ignored

Current expectation:

- a healthy LucyClaw working tree should not show these older hygiene leftovers as pending changes

## 8. How To Validate Healthy State

Minimum sanity checklist:

```bash
git status --short --branch
git log -1 --oneline
python3 scripts/verify_lucyclaw_green_commands.py
python3 scripts/verify_lucyclaw_security_policy.py
```

Useful runtime checks:

- `/health_brief`
- `/lucy_capabilities`

If those are healthy and QA1 passes, the green layer is currently in good standing.

## 9. Recommended Next Tranche Order

Preferred order:

1. `R47` — next functional capability, likely `/fs_find` and `/fs_grep`
2. use `TPL1` as the default generator for future Lucy command tranches
3. keep `SEC1` and `QA1` mandatory before each Lucy command/plugin commit

Alternative order if repo cleanliness becomes urgent:

1. `R47`
2. use `TPL1` as the default generator for future Lucy command tranches
3. keep `SEC1` and `QA1` mandatory before each Lucy command/plugin commit

Guidance:

- avoid adding new functional power without going through `TPL1` unless there is a strong operational reason
- keep `SEC1` and `QA1` as mandatory non-regression checks for future Lucy tranches

## 10. Non-Regression Rules

Do not regress the current baseline:

- do not introduce `shell:true`
- do not reintroduce hardcoded legacy `doctor de lucy` paths
- do not expose `.env` or tokens
- do not read `n8n` workflows from green commands
- do not add repair behavior to green commands
- do not broaden filesystem scope without documentation and tests
- do not commit HYG1/HYG2 pending items without explicit decision
