# LucyClaw Security Policy - SEC1

Date: 2026-05-01

## Objective

`SEC1` adds a static verifier for LucyClaw security policy regressions.

It exists to catch dangerous code patterns before they reach runtime, especially in:

- `scripts/lucy_*_command.py`
- `scripts/verify_lucyclaw_*.py`
- `openclaw_plugins/lucy-*/index.js`
- Lucy plugin manifests and tranche docs

This does not replace human review. It adds an automatic guardrail.

## Files

- `scripts/verify_lucyclaw_security_policy.py`
- `docs/LUCYCLAW_SECURITY_POLICY_SEC1.md`

## Scope

The verifier checks for regressions such as:

- `shell:true`
- `child_process.exec` or `execSync`
- `subprocess` with `shell=True`
- operational `sudo`
- operational `.env` or `dotenv` access
- obvious token / secret leak assignments
- hardcoded legacy tree references to `/home/lucy-ubuntu/Escritorio/doctor de lucy`
- direct `n8n_data`, workflow, credential, or SQLite access from green commands
- restart / repair / deletion patterns in green commands
- `acceptsArgs:true` in Lucy plugins outside the explicit `/fs_read` allowlist

It does not deeply scan:

- `.agents/`
- `n8n_data/`
- `n8n_backups/`
- `.git/`
- heavy runtime logs

## Violations vs Warnings

### Violation

A violation means the verifier found an operational pattern that should fail the tranche, for example:

- `shell: true`
- `shell=True`
- legacy absolute runtime path
- direct repair or deletion primitives in green commands

Violations return `ok: false` and exit code `2`.

### Warning

A warning is non-blocking and usually means:

- a historical doc mentions the old legacy tree for audit context
- a sanitizer regex contains sensitive marker words as part of defensive code
- known local `HYG2` pending items are still present in `git status`

Warnings return `ok: true` as long as there are no violations.

## How To Run

```bash
python3 scripts/verify_lucyclaw_security_policy.py
```

## Relation To QA1

`QA1` verifies runtime-facing behavior of the green command layer.

Run:

```bash
python3 scripts/verify_lucyclaw_green_commands.py
```

`SEC1` verifies that LucyClaw code and plugin files do not introduce forbidden operational patterns.

Run:

```bash
python3 scripts/verify_lucyclaw_security_policy.py
```

Both should pass after touching:

- `scripts/lucy_*`
- `openclaw_plugins/lucy-*`
- Lucy tranche docs that define or explain operational boundaries

## When To Run

Run both QA gates:

- before each commit that touches `scripts/lucy_*`
- before each commit that touches `openclaw_plugins/lucy-*`
- before shipping a new Lucy capability tranche

## Limits

- does not inspect runtime memory
- does not inspect `.env`
- does not inspect live `n8n` workflows
- does not replace human review
- allowlists must stay explicit and documented

## Current Intent

After `SEC1`, LucyClaw should not depend only on policy prose.

The repo now has a guardrail that helps prevent regressions like:

- `shell:true`
- reintroducing the legacy runtime tree
- accidental secret leakage patterns
- accidental expansion into `n8n` workflow internals
