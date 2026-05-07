# Evidence Envelope (AG-TOOLS2) — Agent Tools Runtime

- **tranche_id**: AG-TOOLS2
- **title**: Agent Tools Runtime Exposure for Telegram
- **date**: 2026-05-07T02:30:00Z
- **operator**: Codex
- **base_commit**: 84b3a55
- **target_commit**: PENDING_COMMIT
- **branch**: memoria/bunker
- **risk_level**: YELLOW_CODE_CHANGE
- **runtime_touched**: true
- **restart_count**: 4
- **telegram_verified**: false
- **technical_close**: true
- **functional_close**: false
- **no_tts**: true
- **sensitive_clean**: true

## Summary

The runtime was not missing the plugin; it was missing the plugin tools inside the sandbox tool allowlist for agent `main`. AG-TOOLS2 fixed that by explicitly extending `agents.main.tools.sandbox.tools.allow` with the `lucy_machine_*` tools.

## Controls

- no phrase router
- no `node_modules` patch
- no Telegram listener duplication
- no `.env` or token handling
- slash commands preserved
