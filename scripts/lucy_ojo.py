#!/usr/bin/env python3
import cv2
import numpy as np
import pyautogui
import os
import sys
import argparse
from PIL import Image
import json
import subprocess

# Configuración de Rutas
BASE_DIR = "/home/lucy-ubuntu/Escritorio/doctor de lucy"
TEMPLATES_DIR = os.path.join(BASE_DIR, "resources/ui_templates")
TEMP_SCREENSHOT = "/tmp/lucy_vision_temp.png"

class NinOjo:
    def __init__(self, debug=False):
        self.debug = debug
        if not os.path.exists(TEMPLATES_DIR):
            os.makedirs(TEMPLATES_DIR)

    def capturar_pantalla(self):
        """Captura la pantalla actual y la guarda en /tmp."""
        screenshot = pyautogui.screenshot()
        screenshot.save(TEMP_SCREENSHOT)
        if self.debug:
            print(f"[DEBUG] Pantalla capturada en {TEMP_SCREENSHOT}")
        return TEMP_SCREENSHOT

    def localizar_template(self, template_name, threshold=0.8):
        """Usa OpenCV para encontrar un elemento visual en la pantalla."""
        template_path = os.path.join(TEMPLATES_DIR, template_name)
        if not os.path.exists(template_path):
            print(f"[ERROR] Template no encontrado: {template_path}")
            return None

        # Cargar imagen de pantalla y template
        img_rgb = cv2.imread(TEMP_SCREENSHOT)
        template = cv2.imread(template_path)
        w, h = template.shape[1], template.shape[0]

        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        
        points = list(zip(*loc[::-1]))
        if points:
            # Retornar el centro del primer match encontrado
            best_match = points[0]
            center_x = best_match[0] + w // 2
            center_y = best_match[1] + h // 2
            if self.debug:
                print(f"[DEBUG] Encontrado '{template_name}' en ({center_x}, {center_y})")
            return (center_x, center_y)
        
        return None

    def consultar_vision_semantica(self, prompt="¿Qué ves en esta imagen? Describe los elementos de la interfaz."):
        """Envía la captura a Ollama Llama 3.2 Vision para análisis semántico."""
        if not os.path.exists(TEMP_SCREENSHOT):
            self.capturar_pantalla()

        try:
            # Comando para Ollama Vision (Asumiendo llama3.2-vision instalado)
            # Nota: Esto es un placeholder simplificado de la integración por CLI
            cmd = [
                "ollama", "run", "llama3.2-vision", 
                f"{prompt} Responde de forma concisa. Imagen: {TEMP_SCREENSHOT}"
            ]
            # En producción usaríamos la API de Ollama, pero esto sirve para el prototipo
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error en consulta de visión: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OJO: El Demonio de Visión de la Doctora Lucy")
    parser.add_argument("--test-capture", action="store_true", help="Probar captura de pantalla")
    parser.add_argument("--test-vision", action="store_true", help="Probar análisis semántico con Ollama")
    args = parser.parse_args()

    ojo = NinOjo(debug=True)
    
    if args.test_capture:
        path = ojo.capturar_pantalla()
        print(f"Captura exitosa: {path}")

    if args.test_vision:
        print("Consultando a Ollama Vision...")
        print(ojo.consultar_vision_semantica())
