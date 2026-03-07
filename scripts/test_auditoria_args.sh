#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AUDIT="$ROOT_DIR/scripts/auditoria.sh"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

ok() { echo "[OK] $*"; }
fail() { echo "[FAIL] $*" >&2; exit 1; }

# Caso feliz: salida por flag y timeout numérico
"$AUDIT" --out "$TMP_DIR/reporte.md" --timeout 2 >/dev/null
[ -s "$TMP_DIR/reporte.md" ] || fail "No se generó reporte con --out"
rg -q "Scope default: \*\*PROJECT-ONLY\*\*" "$TMP_DIR/reporte.md" || fail "Falta scope default en reporte"
ok "Generación de reporte con --out/--timeout"

# Compatibilidad posicional
"$AUDIT" "$TMP_DIR/reporte_posicional.md" >/dev/null
[ -s "$TMP_DIR/reporte_posicional.md" ] || fail "No se generó reporte con salida posicional"
ok "Compatibilidad posicional"

# Error esperado: --out sin valor válido
set +e
"$AUDIT" --out --docker >"$TMP_DIR/err_out.txt" 2>&1
EC=$?
set -e
[ "$EC" -eq 2 ] || fail "--out sin valor no devolvió exit 2"
rg -q "Falta valor válido para --out" "$TMP_DIR/err_out.txt" || fail "Mensaje de error --out incorrecto"
ok "Validación de --out sin valor"

# Error esperado: timeout inválido
set +e
"$AUDIT" --timeout abc >"$TMP_DIR/err_timeout.txt" 2>&1
EC=$?
set -e
[ "$EC" -eq 2 ] || fail "--timeout abc no devolvió exit 2"
rg -q "Valor inválido para --timeout" "$TMP_DIR/err_timeout.txt" || fail "Mensaje de timeout inválido incorrecto"
ok "Validación de --timeout no numérico"

echo "Todas las pruebas de auditoría CLI pasaron."
