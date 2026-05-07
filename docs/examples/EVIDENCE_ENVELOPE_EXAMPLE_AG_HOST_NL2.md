# Evidence Envelope (AG-HOST-NL2) — Machine NL Router

- **tranche_id**: AG-HOST-NL2
- **title**: Natural language router for machine tools
- **date**: 2026-05-06T23:59:00Z
- **operator**: Codex
- **base_commit**: 355ee12
- **target_commit**: 7b8bbb1
- **branch**: memoria/bunker
- **risk_level**: YELLOW_CODE_CHANGE
- **qa1_pre**: pending
- **sec1_pre**: pending
- **registry_pre**: pending
- **envelope_validated**: true
- **technical_close**: false
- **functional_close**: false
- **runtime_integration**: false
- **runtime_touched**: false
- **restart_count**: 0
- **telegram_verified**: false
- **no_tts**: true
- **sensitive_clean**: true

## Resumen
Se implementó el router determinístico local y su QA. La integración runtime real quedó bloqueada por la arquitectura actual de OpenClaw: los hooks disponibles no ofrecen short-circuit limpio del turno antes del modelo ni respuesta directa por canal desde `message_received`.

## Archivos
- `scripts/lucy_machine_nl_router.py`
- `scripts/verify_lucyclaw_green_commands.py`
- `docs/LUCYCLAW_MACHINE_NL_ROUTER_AG_HOST_NL2.md`

## Hallazgos SEC1
- Sin `subprocess` en el router.
- Sin shell libre.
- Sin acceso a `.env`, tokens, memoria, bóveda, personalidad ni `n8n_data`.
