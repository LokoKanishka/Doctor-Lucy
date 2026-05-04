# LUCYCLAW_HELP_R56

## Stage Status: R56 (Implementation)
**ID**: DOCTOR_LUCY__7X9K_R56
**Command**: `/lucy_help`
**Mode**: READ_ONLY

## Overview
`/lucy_help` provides a compact, Telegram-friendly guide to the current LucyClaw command surface. It is designed to orient the user without the need for LLM-heavy responses or reading large files.

## Components
1. **Script**: `scripts/lucy_help_command.py`
2. **Logic**: Static JSON payload with command inventory and safe usage flow.
3. **Output**: Deterministic JSON.

## Security Policies (SEC1)
- Must NOT execute actions.
- Must NOT read sensitive zones (.env, n8n, etc.).
- Must NOT accept arguments (bounded scope).
- Must NOT use LLM or external network.

## Acceptance Criteria (QA1)
- [ ] Returns valid JSON.
- [ ] Correctly lists all active green commands.
- [ ] Correctly lists safety flow.
- [ ] Correctly lists blocked zones/actions.
- [ ] Integrated into `lucy_capabilities`.
