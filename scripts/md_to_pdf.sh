#!/bin/bash
# scripts/md_to_pdf.sh
# Convierte un archivo Markdown a PDF usando npx md-to-pdf
# Uso: ./md_to_pdf.sh input.md output.pdf

if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <input.md> <output.pdf>"
    exit 1
fi

INPUT_FILE=$1
OUTPUT_FILE=$2

# Asegurarse de que el input existe
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: El archivo $INPUT_FILE no existe."
    exit 1
fi

# Ejecutar la conversión usando el script de Python
python3 "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/md_to_pdf.py" "$INPUT_FILE" "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "Éxito: PDF generado en $OUTPUT_FILE"
else
    echo "Error: Falló la generación del PDF."
    exit 1
fi
