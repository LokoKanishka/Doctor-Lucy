#!/usr/bin/env bash
# Lucy Announcer Script - Tono Elegante
# Uso: ./scripts/lucy_announcer.sh "Mensaje"

PAYLOAD_FILE="/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/voice_payload.txt"
VOICE="female_03.wav"
LANGUAGE="es"

if [ ! -f "$PAYLOAD_FILE" ] && [ -n "$1" ]; then
    echo "$1" > "$PAYLOAD_FILE"
fi

# Reproducir usando el nuevo modo --file para evitar escapes de shell complejos
python3 "$(dirname "$0")/lucy_alltalk.py" --file "$PAYLOAD_FILE" "$VOICE" "$LANGUAGE"
