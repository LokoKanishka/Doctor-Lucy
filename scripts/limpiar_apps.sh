#!/bin/bash
echo "🚀 Iniciando limpieza de aplicaciones no deseadas..."
sudo snap remove thunderbird
sudo apt purge -y thunderbird transmission-gtk rhythmbox shotwell cheese simple-scan remmina
sudo apt autoremove -y
echo "✅ Limpieza completada satisfactoriamente."
