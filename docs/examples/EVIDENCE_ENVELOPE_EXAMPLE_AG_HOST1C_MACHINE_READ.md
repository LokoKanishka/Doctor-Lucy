# Evidence Envelope (AG-HOST1C) — Machine Read

- **tranche_id**: AG-HOST1C
- **title**: Read-only Document Reading Commands
- **date**: 2026-05-06T23:30:00Z
- **operator**: Codex
- **base_commit**: 6a8094b
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
Se agregaron `/machine_read` y `/machine_doc_brief` como lectura local acotada para documentos seguros sin tocar el intercepto de lenguaje natural.

## Archivos
- `scripts/lucy_machine_read_command.py`
- `openclaw_plugins/lucy-machine-read-command/*`
- `scripts/lucy_capabilities_command.py`
- `scripts/lucy_repo_map_command.py`
- `scripts/verify_lucyclaw_green_commands.py`

## Controles
- Rutas seguras allowlisted
- Rechazo explícito de secretos y runtime sensible
- PDF solo con `pdftotext` allowlisted
- DOCX sin macros ni dependencias externas
