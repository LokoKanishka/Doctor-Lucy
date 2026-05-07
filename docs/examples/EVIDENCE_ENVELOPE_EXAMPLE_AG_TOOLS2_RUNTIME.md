# Evidence Envelope (AG-TOOLS2) — Agent Tools Runtime

- **tranche_id**: AG-TOOLS2
- **title**: Agent Tools Runtime Exposure for Telegram
- **date**: 2026-05-07T02:30:00Z
- **operator**: Codex
- **base_commit**: 84b3a55
- **target_commit**: 5cda41fdecb9c587235536ef00d87c717681974a
- **branch**: memoria/bunker
- **risk_level**: YELLOW_CODE_CHANGE
- **runtime_touched**: true
- **restart_count**: 4
- **telegram_verified**: true
- **technical_close**: true
- **functional_close**: true
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

## Closure Notes (AG-TOOLS2-FCLOSE)

- **Final Commit**: 5cda41fdecb9c587235536ef00d87c717681974a.
- **Exposure**: All 10 `lucy_machine_*` tools are verified as exposed to agent `main`.
- **Functional Validation (Diego via Telegram)**:
  - "qué programas están abiertos ahora?" -> Correct response with real processes.
  - "cuánta vram estoy usando?" -> Correct response (RTX 5090 / Real VRAM).
  - "qué fue lo último que descargué?" -> Correct response (llama.cpp-b5027-bin-ubuntu-x64.zip).
  - "hola cómo estás?" -> Correct conversational response (no tool triggered).
- **Dictamen**: The chain (Natural Language -> Agent Tools -> Host Wrappers -> Real Data) is fully functional.
- **Pending Optimization**: Improve "qué fue lo último que descargué?" to deliver data directly without unnecessary confirmation prompts (Non-blocking).

