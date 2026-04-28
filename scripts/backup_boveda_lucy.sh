#!/bin/bash
# scripts/backup_boveda_lucy.sh
# Backup seguro de la memoria viva (boveda_lucy.sqlite)

set -euo pipefail

# Detectar la raíz del workspace dinámicamente
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuración de backup
BACKUP_ROOT="${BACKUP_ROOT:-$HOME/Doctor_Lucy_Backups/boveda}"
BOVEDA_PATH="$WORKSPACE_ROOT/n8n_data/boveda_lucy.sqlite"

echo "=== Doctor Lucy: Backup de Memoria Viva ==="

# Verificar que la base existe
if [ ! -f "$BOVEDA_PATH" ]; then
    echo "❌ Error: No se encontró la base de datos en $BOVEDA_PATH"
    exit 1
fi

# Verificar integridad si sqlite3 está disponible
if command -v sqlite3 &> /dev/null; then
    echo "Verificando integridad de la base de datos..."
    CHECK_RESULT=$(sqlite3 -readonly "$BOVEDA_PATH" "PRAGMA quick_check;")
    if [ "$CHECK_RESULT" != "ok" ]; then
        echo "❌ Error: La verificación de integridad falló. Resultado: $CHECK_RESULT"
        echo "Abortando backup para evitar respaldar una base corrupta."
        exit 1
    fi
    echo "✅ Integridad: OK"
else
    echo "⚠️ Advertencia: sqlite3 no está instalado. Saltando verificación de integridad."
fi

# Crear directorio de backup con timestamp
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$BACKUP_ROOT/$STAMP"
mkdir -p "$BACKUP_DIR"

echo "Creando backup en: $BACKUP_DIR"

# Copiar archivos
cp -a "$BOVEDA_PATH" "$BACKUP_DIR/"
echo "✅ Copiado: boveda_lucy.sqlite"

if [ -f "${BOVEDA_PATH}-wal" ]; then
    cp -a "${BOVEDA_PATH}-wal" "$BACKUP_DIR/"
    echo "✅ Copiado: boveda_lucy.sqlite-wal"
fi

if [ -f "${BOVEDA_PATH}-shm" ]; then
    cp -a "${BOVEDA_PATH}-shm" "$BACKUP_DIR/"
    echo "✅ Copiado: boveda_lucy.sqlite-shm"
fi

# Crear checksums
echo "Generando checksums SHA-256..."
(
    cd "$BACKUP_DIR"
    sha256sum * > SHA256SUMS.txt
)

echo "=== Backup Completado Exitosamente ==="
echo "Directorio: $BACKUP_DIR"
ls -lh "$BACKUP_DIR" | awk '{print $5, $9}' | tail -n +2
