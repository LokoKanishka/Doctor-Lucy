#!/bin/bash
# Backup Core de Doctora Lucy
# Creado automáticamente por Antigravity

BACKUP_DIR="/home/lucy-ubuntu/Escritorio/LUCY_CORE_BACKUP"
BACKUP_FILE="/home/lucy-ubuntu/Escritorio/LUCY_CORE_BACKUP_$(date +%Y%m%d).tar.gz"

echo "Iniciando protocolo de empaquetado de memoria y sistema..."

# Crear carpeta de staging
mkdir -p "$BACKUP_DIR"

# 1. Proyectos Principales (Excluyendo entornos virtuales pesados o node_modules si es necesario, pero los llevamos por seguridad a menos que pesen demasiado. Mejor copiamos con rsync excluyendo lo más pesado que se puede reinstalar)
echo "Copiando Doctor de Lucy y NIN..."
rsync -aP --exclude 'node_modules' --exclude '.venv' "/home/lucy-ubuntu/Escritorio/doctor de lucy" "$BACKUP_DIR/"
rsync -aP --exclude 'node_modules' --exclude '.venv' "/home/lucy-ubuntu/Escritorio/NIN" "$BACKUP_DIR/"

# 2. Configuración Oculta Vital (SSH, Bash)
echo "Copiando credenciales SSH y configuraciones de terminal..."
[ -d "$HOME/.ssh" ] && cp -r "$HOME/.ssh" "$BACKUP_DIR/dot_ssh"
[ -f "$HOME/.bashrc" ] && cp "$HOME/.bashrc" "$BACKUP_DIR/dot_bashrc"
[ -f "$HOME/.zshrc" ] && cp "$HOME/.zshrc" "$BACKUP_DIR/dot_zshrc"

# 3. Configuraciones de IDE (Cursor o VSCode)
echo "Buscando configuraciones de IDE locales (Cursor/VSCode)..."
mkdir -p "$BACKUP_DIR/ide_settings"
find "$HOME/.config" -type d \( -name "Code" -o -name "Cursor" \) -exec cp -r {} "$BACKUP_DIR/ide_settings/" \; 2>/dev/null

# 4. Memoria de Antigravity (Cerebro local)
echo "Copiando matriz cerebral de Antigravity..."
[ -d "$HOME/.gemini" ] && rsync -aP "$HOME/.gemini" "$BACKUP_DIR/"

# 5. Comprimir todo
echo "Comprimiendo todo en un solo paquete blindado..."
cd /home/lucy-ubuntu/Escritorio
tar -czf "$BACKUP_FILE" "LUCY_CORE_BACKUP"

# 6. Limpiar staging
rm -rf "$BACKUP_DIR"

echo "¡Empaquetado completado! Archivo generado: $BACKUP_FILE"
