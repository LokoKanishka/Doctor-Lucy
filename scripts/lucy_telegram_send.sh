#!/bin/bash
# Lucy Telegram Sender — Envía mensajes y archivos a Diego por Telegram.
# Uso:
#   Mensaje:  bash scripts/lucy_telegram_send.sh "texto del mensaje"
#   Archivo:  bash scripts/lucy_telegram_send.sh --file /ruta/al/archivo "caption opcional"

BOT_TOKEN="8591918754:AAHlxsxP4olX3De2uWGH0NUUXEiHX3iUhLk"
CHAT_ID="5154360597"
API_URL="https://api.telegram.org/bot${BOT_TOKEN}"

if [ "$1" == "--file" ]; then
    FILE_PATH="$2"
    CAPTION="${3:-}"
    
    if [ ! -f "$FILE_PATH" ]; then
        echo "[ERROR] Archivo no encontrado: $FILE_PATH"
        exit 1
    fi
    
    echo "[Lucy TG] Enviando archivo: $FILE_PATH"
    curl -s -X POST "${API_URL}/sendDocument" \
        -F "chat_id=${CHAT_ID}" \
        -F "document=@${FILE_PATH}" \
        -F "caption=${CAPTION}"
    echo ""
    echo "[Lucy TG] Archivo enviado."
else
    MESSAGE="$1"
    echo "[Lucy TG] Enviando mensaje..."
    curl -s -X POST "${API_URL}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${MESSAGE}" \
        -d "parse_mode=Markdown"
    echo ""
    echo "[Lucy TG] Mensaje enviado."
fi
