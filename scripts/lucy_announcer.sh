#!/usr/bin/env bash
# Lucy Announcer Script - Tono Elegante
# Uso: ./scripts/lucy_announcer.sh "Mensaje"

PAYLOAD_FILE="${WORKSPACE_ROOT:-/home/lucy-ubuntu/Escritorio/doctor de lucy}/n8n_data/voice_payload.txt"
VOICE="female_03.wav"
LANGUAGE="es"

# El patrón Buzón dicta que el archivo payload ya debe existir creado por la IA nativamente.
# Esto es solo un fallback de conveniencia para pruebas manuales del desarrollador.
if [ -n "$1" ]; then
    echo "$1" > "$PAYLOAD_FILE"
fi

# Reproducir usando el modo --file para evitar bloqueos del Zero-Prompt del IDE
python3 "$(dirname "$0")/lucy_alltalk.py" --file "$PAYLOAD_FILE" "$VOICE" "$LANGUAGE"

# RECOLECCIÓN DE BASURA: Eliminar el payload para evitar ataques de datos o reproducción de memoria fantasma
if [ -f "$PAYLOAD_FILE" ]; then
    rm -f "$PAYLOAD_FILE"
fi
