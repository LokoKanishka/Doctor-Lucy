#!/bin/bash
# Script para lanzar el Hub de la Doctora Lucy en Firefox con perfil Enjambre
echo "Iniciando Doctora Lucy Hub..."
# Usamos -P "Enjambre" para forzar el perfil donde ya está logueado n8n
firefox -P "Enjambre" --new-window http://localhost:6969 &
disown
exit
