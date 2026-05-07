# Evidence Envelope (AG-HOST-NL3) — Machine NL Runtime Intercept

- **tranche_id**: AG-HOST-NL3
- **title**: Natural language machine runtime intercept
- **date**: 2026-05-06T22:30:00Z
- **operator**: Codex
- **base_commit**: 7b8bbb1
- **target_commit**: pending
- **branch**: memoria/bunker
- **risk_level**: YELLOW_CODE_CHANGE
- **runtime_touched**: true
- **restart_count**: 1
- **telegram_verified**: false
- **technical_close**: true
- **functional_close**: false
- **no_tts**: true
- **sensitive_clean**: true

## Summary

Se implementó un intercepto runtime real en el gateway local de OpenClaw para promover frases naturales seguras a slash commands internos `machine_*` antes del modelo. La arquitectura elegida fue un patch mínimo y reversible del runtime Telegram, porque OpenClaw no ofrece una API nativa de short-circuit pre-modelo para texto no slash.

## Runtime Touch

- patched: `/home/lucy-ubuntu/.npm-global/lib/node_modules/openclaw/dist/reply-DeXK9BLT.js`
- backup: `/home/lucy-ubuntu/.openclaw/backups/AG_HOST_NL3/reply-DeXK9BLT.js.bak`
- config touched: none

## Result

- gateway post-restart: live
- direct machine wrappers: preserved
- router local: preserved
- Telegram verification: pending operator confirmation
