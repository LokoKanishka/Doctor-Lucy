#!/usr/bin/env bash
# Script para estabilizar el proyector en hardware dual (NVIDIA + AMD)
# Este script puentea los proveedores de video y configura el modo extendido.

# 1. Puente de proveedores (NVIDIA Source -> AMD Sink)
# Identificadores detectados: 1 (AMD), 0 (NVIDIA)
xrandr --setprovideroutputsource 1 0

# Esperar sincronización
sleep 2

# 2. Configurar modo extendido (Proyector a la derecha)
xrandr --output HDMI-A-1-0 --auto --right-of HDMI-0

echo "[Lucy Display] Proyector configurado en modo extendido (Derecha)."
