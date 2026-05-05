# LucyClaw Evidence Envelope Validator (AG-Y2)

## Objetivo
Proveer una herramienta local (`scripts/verify_evidence_envelope.py`) que valide de forma estática la estructura y seguridad de los reportes "Evidence Envelope" generados tras cada tramo amarillo, garantizando que cumplan el estándar de R61 antes de integrarlos al repositorio.

## Por qué es el primer cambio amarillo de código
- **Transición**: Marca el paso formal de "diseño de protocolos" a "implementación controlada" bajo la Arquitectura v3 (R59).
- **Dogfooding**: Se obliga al operador (Antigravity) a utilizar el protocolo R60 y entregar la evidencia en el estándar R61 para agregar código nuevo al repositorio.

## Alcance
- Se limita exclusivamente al script validador en Python.
- No afecta ni modifica la lógica de la pasarela (Gateway), los conectores de n8n o la configuración viva (runtime).

## Seguridad
- **Sin red / dependencias**: Ejecución offline pura.
- **Path Policy**: Bloquea por diseño cualquier intento de leer zonas calientes (`.env`, `n8n_data`, `memoria`, `vault`, etc.).
- **String Filtering**: Detecta y rechaza *Evidence Envelopes* que hayan filtrado tokens (`OPENAI_API_KEY`, etc.), forzando al operador a limpiar el reporte antes de commitear.

## Uso del Script
El validador se invoca desde la raíz del repositorio pasando la ruta relativa del envelope a evaluar:
```bash
python3 scripts/verify_evidence_envelope.py docs/examples/EVIDENCE_ENVELOPE_EXAMPLE_AG_Y1_R61.md
```
Devuelve una salida JSON determinista compatible con jq o scripts CI.

## Ejemplos de Validación
- **VALID**: `{ "ok": true, "decision": "VALID", ... }` si contiene todos los campos obligatorios y no filtra strings calientes.
- **INVALID**: `{ "ok": false, "decision": "INVALID", "missing_required_fields": ["base_commit", "target_commit"] }` si le faltan datos críticos.

## Qué NO Hace
- **No es Daemon v3**: Este script no automatiza reinicios ni rollbacks.
- **No implementa el Run Registry**: No es una base de datos ni indexador.
- **No ejecuta el sobre**: Es un verificador estático de markdown/texto; no corre los comandos listados en la evidencia.

## Relación con R60
Cumple el requerimiento de R60 de hacer los tramos auditables proveyendo un mecanismo de revisión automatizada para la fase "REPORT".

## Relación con R61
Mecaniza las "Reglas de Validez" y "Campos Prohibidos" definidas en el estándar de Evidence Envelope (R61).

## Criterios de Aceptación
- El script funciona bajo Python 3 estándar.
- Rechaza rutas prohibidas (Hard Block).
- Falla y reporta si se omiten campos mínimos de trazabilidad.

## Rollback
En caso de falla o vulnerabilidad, el rollback de este tramo es un `git revert` simple, ya que se limita a añadir código de utilería sin impacto en servicios vivos.

## Próximos Pasos
- Integrar la invocación del validador dentro del proceso de CI/CD o en compuertas secundarias como `lucy_next_step`.
- Proceder al diseño de `R62` (Run Registry mínimo documental/JSONL) o `AG-Y3` (Tramos con plugins bajo Evidence Envelope obligatorio).
