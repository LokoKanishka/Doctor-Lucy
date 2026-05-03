# LucyClaw Current State

Date: 2026-05-03

## 1. Current Short State

- Expected branch: `memoria/bunker`
- Last known healthy commit: `32f5ef3` `feat(lucyclaw): add readonly repo map command`
- Current operational status: green read-only layer is solid, repeatably verifiable, and now includes compact repo orientation, deterministic file briefing, and read-only planning contracts
- Immediate recommendation: use `/repo_map` and `/doc_brief` for safe orientation, then `/lucy_next_step` before advancing capability scope

## 2. Confirmed Healthy Base

The current stable baseline is:

- OpenClaw gateway healthy
- Telegram healthy
- Lucy plugins execute from `/home/lucy-ubuntu/Escritorio/doctora-lucy`
- `/health_report` active
- `/health_brief` active
- `/lucy_capabilities` active
- `/repo_map` active in tranche R49
- `/doc_brief` active in tranche R50A
- `/plan_brief` active in tranche R51
- `/risk_check` active in tranche R52
- `/permission_brief` active in tranche R53
- QA1 verifier available

This means Lucy currently has a real bounded green zone, not just a documented one.

## 3. Active Green Commands

### Safe Bounded Read

- `/fs_read`
- `/fs_find`
- `/fs_grep`
- `/doc_brief`
- `/plan_brief`
- `/risk_check`
- `/permission_brief`
- `/change_plan`

Usage:

- exact line-range reading from allowed repo files only
- bounded file-name search inside the allowed repo tree
- bounded text search inside allowed repo files
- deterministic conceptual briefing for allowed docs and Lucy command files
- deterministic planning, risk and permission briefing for future work
- deterministic technical change contracts without execution

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
- `/lucy_next_step`
- `/repo_map`
- `/doc_brief`
- `/plan_brief`
- `/risk_check`
- `/permission_brief`
- `/change_plan`

Usage:

- aggregate diagnostic report
- compact Telegram-friendly summary
- safe READY / WARN / BLOCK gate before advancing
- compact repo orientation without entering sensitive zones
- deterministic local summary of safe repo docs and command files
- deterministic planning and technical change contracts while staying read-only

### Capability / Policy Map

- `/lucy_capabilities`

Usage:

- deterministic explanation of green, yellow, and red operational boundaries
- deterministic compact repo map for safe navigation

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
- `lucy-fs-search-command`
- `lucy-machine-status-command`
- `lucy-service-status-command`
- `lucy-health-report-command`
- `lucy-health-brief-command`
- `lucy-capabilities-command`
- `lucy-next-step-command`
- `lucy-repo-map-command`
- `lucy-doc-brief-command`
- `lucy-plan-brief-command`
- `lucy-risk-check-command`
- `lucy-permission-brief-command`
- `lucy-change-plan-command`

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
- `/repo_map` shape and sensitive exclusion checks
- `/doc_brief` safe summary and rejection checks
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
- `/repo_map`
- `/doc_brief docs/LUCYCLAW_CURRENT_STATE.md`
- `/lucy_next_step`

If those are healthy and QA1 passes, the green layer is currently in good standing.

## 9. Recommended Next Tranche Order

Preferred order:

1. `R50A` — `/doc_brief` deterministic conceptual read-only briefing
2. `R51-R54` — read-only planning layer: `/plan_brief`, `/risk_check`, `/permission_brief`, `/change_plan`
3. decide between `R55 /scaffold_plan` or the first minimal supervised yellow action

Alternative order if repo cleanliness becomes urgent:

1. `R50A`
2. `R51-R54`
3. keep `SEC1`, `QA1`, and `/lucy_next_step` as the advance gate before each Lucy capability tranche

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
