# LucyClaw Agent Tools Runtime — AG-TOOLS2

## Objective

Diagnose why the `lucy_machine_*` agent tools created in AG-TOOLS1 were loaded but not usable from natural-language runs coming from Telegram/OpenClaw.

## Cause Found

- `api.registerTool(...)` was working.
- `lucy-machine-agent-tools` was loaded and visible in `openclaw plugins info`.
- The real Telegram agent is `main`.
- The real model route is `openai-codex/gpt-5.4`.
- The agent runs in sandbox mode `all`.
- `openclaw sandbox explain --agent main` showed a sandbox tool allowlist with only built-in tools:
  - `exec`, `process`, `read`, `write`, `edit`, `apply_patch`, `image`, `sessions_*`, `subagents`, `session_status`
- Because of that sandbox allowlist, the plugin tools never reached the agent run, so the model answered as if it had no host machine access.

## Change Applied

Outside the repo, `~/.openclaw/openclaw.json` was updated with:

- explicit `plugins.allow`
- `agents.list[id=main].tools.alsoAllow` for the 10 `lucy_machine_*` tool names
- `agents.list[id=main].tools.sandbox.tools.allow` set to:
  - the default sandbox allowlist
  - plus the 10 `lucy_machine_*` tool names

This was the effective fix. `tools.sandbox.tools.alsoAllow` was tested first and discarded because this local OpenClaw build only honors `allow` / `deny` for sandbox tool policy resolution.

## Verification

- `openclaw sandbox explain --agent main` now reports `allow (agent)` and includes all 10 `lucy_machine_*` tools.
- `openclaw agent --agent main --message "cuánta vram estoy usando?" --json` now includes the 10 `lucy_machine_*` tools in `systemPromptReport.tools.entries`.
- The same local run returned real GPU/VRAM data instead of sandbox-only guidance.
- Slash commands and Python wrappers remained healthy.

## Files and Runtime

- Repo change:
  - `openclaw_plugins/lucy-machine-agent-tools/openclaw.plugin.json`
  - docs and run-registry records for AG-TOOLS2
- Runtime/config change outside repo:
  - `~/.openclaw/openclaw.json`

## Backups

- `~/.openclaw/openclaw.json.bak.AG_TOOLS2_20260507_021528`
- `~/.openclaw/openclaw.json.bak.AG_TOOLS2_20260507_022045`
- `~/.openclaw/openclaw.json.bak.AG_TOOLS2_20260507_022359`
- `~/.openclaw/openclaw.json.bak.AG_TOOLS2_20260507_022502`
- `~/.openclaw/openclaw.json.bak.AG_TOOLS2_20260507_022600`

## Rollback

1. Restore the latest `~/.openclaw/openclaw.json.bak.AG_TOOLS2_*`.
2. Restart `openclaw-gateway.service`.
3. Re-run `openclaw sandbox explain --agent main`.

## Final State

- Technical runtime path corrected.
- Telegram natural-language functional closure still pending Diego verification.
- No router by phrases.
- No `node_modules` patch.
- No TTS.
