# LUCYCLAW_COMMANDS_BRIEF_R57

## Stage Status: R57 (Implementation)
**ID**: DOCTOR_LUCY__7X9K_R57
**Command**: `/commands_brief`
**Mode**: READ_ONLY

## Overview
`/commands_brief` provides an ultra-compact, categorical index of the LucyClaw command surface. It complements `/lucy_help` by focusing on raw command listing rather than usage flow.

## Components
1. **Script**: `scripts/lucy_commands_brief_command.py`
2. **Logic**: Static JSON payload with grouped command inventory.
3. **Output**: Deterministic JSON.

## Security Policies (SEC1)
- Must NOT execute actions.
- Must NOT read sensitive zones (.env, n8n, etc.).
- Must NOT accept arguments (bounded scope).
- Must NOT use LLM or external network.

## Acceptance Criteria (QA1)
- [ ] Returns valid JSON.
- [ ] Correctly groups all active green commands.
- [ ] Includes `/lucy_help` and `/commands_brief`.
- [ ] Correctly lists blocked zones/actions.
- [ ] Integrated into `lucy_capabilities`.
