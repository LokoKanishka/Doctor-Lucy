# Evidence Envelope (AG-TOOLS1) — Agent Tools

- **tranche_id**: AG-TOOLS1
- **title**: Machine Capabilities as Agent Tools
- **date**: 2026-05-07T00:00:00Z
- **operator**: Codex
- **base_commit**: ecd7dab
- **target_commit**: COMMIT_REAL_FINAL
- **branch**: memoria/bunker
- **risk_level**: YELLOW_CODE_CHANGE
- **runtime_touched**: true
- **restart_count**: 1
- **telegram_verified**: false
- **technical_close**: true
- **functional_close**: false
- **no_tts**: true
- **sensitive_clean**: true

## Resumen
Se registran capabilities `machine_*` como agent tools reales mediante `api.registerTool(...)`, manteniendo intactos los slash commands existentes.

## Controles
- sin router por frases
- sin patch de `node_modules`
- sin hooks runtime de short-circuit
- wrappers Python existentes preservados
