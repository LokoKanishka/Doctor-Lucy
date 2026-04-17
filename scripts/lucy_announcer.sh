#!/usr/bin/env bash
# Lucy Announcer Script - Tono Elegante
# Uso: ./scripts/lucy_announcer.sh "Mensaje"

MESSAGE=$1
# Voz Sophie Anderson para máxima elegancia y profundidad
VOICE="Sophie_Anderson CC3.wav"
LANGUAGE="es"

# Reproductor robusto: ffplay maneja mejor los cambios de sample rate y buffer.
python3 "$(dirname "$0")/lucy_alltalk.py" "$MESSAGE" "$VOICE" "$LANGUAGE"
