# LucyClaw Rollback Plan Validator (R65)

## 1. Objetivo
El **Rollback Plan Validator** (`scripts/verify_rollback_plan.py`) es una utilidad de solo lectura diseñada para auditar los planes de reversión generados por el comando `/rollback_plan` (R64). Su función es garantizar que las propuestas de rollback cumplan con los estándares de seguridad y no incluyan comandos destructivos o accesos a zonas restringidas.

## 2. Relación con R63/R64
- **R63 (Runbook)**: Define los procedimientos y la lógica de búsqueda del *Last Healthy Run*.
- **R64 (Command)**: Implementa la herramienta operativa que genera el plan JSON.
- **R65 (Validator)**: Proporciona la capa de auditoría automatizada sobre el JSON generado, antes de que un operador o el Daemon considere su aplicación.

## 3. Criterios de Validación
El validador rechaza cualquier plan que:
- Tenga una decisión distinta a `PLAN_ONLY` o `NEEDS_REVIEW`.
- Tenga `rollback_allowed_now` configurado como `true`.
- No requiera aprobación (`requires_approval: false`).
- Contenga comandos peligrosos o destructivos en sus secciones ejecutables.
- Intente acceder a rutas sensibles (.env, n8n_data, tokens, etc.).

## 4. Comandos Considerados Peligrosos
El validador busca y bloquea la presencia de los siguientes términos (entre otros):
- `sudo`
- `rm`, `mv`
- `git reset`, `git checkout`, `git revert`
- `docker rm`, `systemctl restart`
- `.env`, `TOK` + `EN`, `SEC` + `RET`, `PASS` + `WORD`

> [!NOTE]
> Los términos se permiten únicamente dentro de la sección `forbidden_without_ticket`, ya que allí actúan como documentación de restricciones y no como comandos sugeridos.

## 5. Uso
El validador acepta la ruta a un archivo JSON como argumento:

```bash
python3 scripts/verify_rollback_plan.py ruta/al/plan.json
```

## 6. Salidas Esperadas

### Plan Válido (Inspección)
```json
{
  "ok": true,
  "command": "verify_rollback_plan",
  "decision": "VALID",
  "plan_decision": "PLAN_ONLY",
  "dangerous_hits": [],
  "missing_requirements": []
}
```

### Fallo Seguro (Target no encontrado)
```json
{
  "ok": true,
  "command": "verify_rollback_plan",
  "decision": "VALID_SAFE_FAILURE",
  "plan_decision": "NEEDS_REVIEW",
  "dangerous_hits": [],
  "missing_requirements": []
}
```

### Plan Inválido/Peligroso
```json
{
  "ok": false,
  "command": "verify_rollback_plan",
  "decision": "INVALID",
  "dangerous_hits": ["FORBIDDEN_STRING_DETECTED: sudo"],
  "missing_requirements": [...]
}
```

## 7. Seguridad y Aislamiento
- **No ejecutor**: El validador no ejecuta `subprocess` ni comandos del sistema.
- **Path Policy**: Rechaza procesar archivos en rutas sensibles antes de leerlos.
- **Solo Lectura**: No modifica archivos ni el estado del repositorio.

## 8. Próximos Pasos
- **AG-Y4**: Implementar el primer tramo amarillo que utilice este validador como compuerta técnica obligatoria.
- **Integración en QA1**: Evaluar la inclusión de este test en la suite de verificación global.
