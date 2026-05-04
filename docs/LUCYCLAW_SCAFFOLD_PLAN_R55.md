# LUCYCLAW_SCAFFOLD_PLAN_R55

## Stage Status: R55 (Implementation)
**ID**: DOCTOR_LUCY__7X9K_R55
**Command**: `/scaffold_plan`
**Mode**: PLAN_ONLY (Read-only)

## Overview
`/scaffold_plan` analyzes a natural language request to create a new command and generates a technical plan without performing any mutations. It is the precursor to the actual scaffolding logic, ensuring that any proposed command follows the read-only and security policies.

## Components
1. **Script**: `scripts/lucy_scaffold_plan_command.py`
2. **Logic**: Uses `lucy_planning_readonly.py` for risk classification and permission mapping.
3. **Output**: Deterministic JSON with `decision: "PLAN_ONLY"`.

## Security Policies (SEC1)
- Must NOT create files.
- Must NOT install plugins.
- Must NOT restart services.
- Must NOT commit changes.
- Risk "RED" blocks file/modify suggestions.

## Acceptance Criteria (QA1)
- [ ] Returns valid JSON.
- [ ] Correctly extracts command slug.
- [ ] Redacts sensitive information from input.
- [ ] Maps permissions according to risk level.
- [ ] Suggests correct file structure for new plugins.
