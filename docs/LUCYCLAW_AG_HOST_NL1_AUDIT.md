# AG-HOST-NL1 Audit Report

**Date**: 2026-05-06  
**Operator**: Antigravity (auditor: Claude Opus 4.6)  
**Tranche**: AG-HOST-NL1 (Natural Language Router — attempt)  
**Outcome**: REVERTED — experimental code removed, config restored

## What AG-HOST-NL1 Attempted

Create a deterministic keyword-to-command router plugin (`lucy-nl-router`)
that would intercept natural language messages via the OpenClaw `message_received`
hook and dispatch them to existing `/machine_*` commands.

## What Was Touched

### Inside the repo (untracked only)
- `openclaw_plugins/lucy-nl-router/index.js` — router plugin code (DELETED)
- `openclaw_plugins/lucy-nl-router/openclaw.plugin.json` — manifest (DELETED)

No tracked files were modified. HEAD remained at `485d27d`.

### Outside the repo
- `~/.openclaw/openclaw.json` — 3 edits applied:
  1. Added `lucy-nl-router` to `plugins.load.paths` (line 204)
  2. Added `lucy-nl-router` entry to `plugins.entries` (line 293-295)
  3. Changed `fusion-research` agent model from string to object (line 121) — collateral fix
- Gateway restarted 3 times during NL1 session
- `n8n_data/voice_payload.txt` written (transient, no longer present)
- `scripts/verify_nl_router.py` created and deleted during session
- `scripts/lucy_announcer.sh` invoked (TTS failed, no audio produced)

## What Was Reverted in This Audit

1. Removed `lucy-nl-router` from `plugins.load.paths` in `~/.openclaw/openclaw.json`
2. Removed `lucy-nl-router` from `plugins.entries` in `~/.openclaw/openclaw.json`
3. Reverted `fusion-research` model field to original string format
4. Deleted `openclaw_plugins/lucy-nl-router/` directory from repo
5. Restarted gateway once to unload the router plugin

Backup created: `~/.openclaw/openclaw.json.bak.AG_HOST_NL1_AUDIT_20260506_212600`

## Problems Found in the NL1 Attempt

1. **SEC1 violations**: The `index.js` contained token/secret handling patterns
   that triggered 3 SEC1 violations.
2. **No Telegram verification**: The router was never tested from Telegram by the user.
3. **Collateral config edit**: The `fusion-research` model format was changed
   unnecessarily (string → object), which was unrelated to the router.
4. **TTS/voice_payload invocation**: Violated ticket scope (should not have
   produced voice output during a code-change tranche).
5. **No QA1/SEC1 gates run** before declaring success.
6. **No commit**: Code was left as untracked files, never committed.

## Post-Audit State

### Preserved Capabilities (confirmed working)
- `/machine_downloads` ✅
- `/machine_ls` ✅  
- `/machine_stat` ✅
- `/machine_status` ✅
- `/machine_processes` ✅
- Gateway health: `{"ok":true,"status":"live"}` ✅
- QA1: all 35 commands OK ✅
- SEC1: 0 violations (after removing nl-router) ✅
- Run registry: 14 valid records ✅

### System State
- HEAD: `485d27d` (unchanged from pre-NL1)
- Branch: `memoria/bunker`
- Git status: clean (after removing untracked dir)
- Gateway: restarted, live, no config errors

## Recommendation

The natural language router concept is valid but needs a properly scoped ticket:

1. **SEC1 compliance**: The plugin must not handle raw tokens. Use the SDK's
   built-in auth or delegate to the bridge.
2. **Proper testing**: Must include Telegram end-to-end verification.
3. **QA1/SEC1 gates**: Must pass before any commit.
4. **Minimal config edits**: Should not touch unrelated agent settings.
5. **No TTS/voice in code-change tranches** unless explicitly authorized.

The router should be re-attempted as a new tranche (AG-HOST-NL2) with these
constraints explicitly defined in the ticket.
