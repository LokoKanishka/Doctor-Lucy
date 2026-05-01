# LucyClaw Current State

Date: 2026-05-01

## 1. Current Short State

- Expected branch: `memoria/bunker`
- Last known healthy commit: `dde7fba` `test(lucyclaw): add unified green command verifier`
- Current operational status: green read-only layer is solid and repeatably verifiable
- Immediate recommendation: prioritize `SEC1`, `HYG2`, and `TPL1` before adding new functional powers

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

QA1 is the current minimum gate for the green layer.

## 7. Known Local Pending Items

Known local pending items, intentionally outside current Lucy tranches:

- `M .gitignore`
- `?? .agents/archive_openclaw_scope_fix_20260429_153235/`
- `?? docs/OPENCLAW_REBUILD_1A_PROFILE.md`

Important notes:

- these did not block `R45`, `R46`, or `QA1`
- they must not be mixed into new capability tranches
- `HYG2` should resolve them explicitly

## 8. How To Validate Healthy State

Minimum sanity checklist:

```bash
git status --short --branch
git log -1 --oneline
python3 scripts/verify_lucyclaw_green_commands.py
```

Useful runtime checks:

- `/health_brief`
- `/lucy_capabilities`

If those are healthy and QA1 passes, the green layer is currently in good standing.

## 9. Recommended Next Tranche Order

Preferred order:

1. `SEC1` — security policy tests and enforcement
2. `HYG2` — definitive local hygiene cleanup
3. `TPL1` — safe command scaffold/generator
4. `R47` — next functional capability, likely `/fs_find` and `/fs_grep`

Alternative order if repo cleanliness becomes urgent:

1. `HYG2`
2. `SEC1`
3. `TPL1`
4. `R47`

Guidance:

- avoid adding new functional power before `SEC1`, `HYG2`, and `TPL1` unless there is a strong operational reason

## 10. Non-Regression Rules

Do not regress the current baseline:

- do not introduce `shell:true`
- do not reintroduce hardcoded legacy `doctor de lucy` paths
- do not expose `.env` or tokens
- do not read `n8n` workflows from green commands
- do not add repair behavior to green commands
- do not broaden filesystem scope without documentation and tests
- do not commit HYG1/HYG2 pending items without explicit decision
