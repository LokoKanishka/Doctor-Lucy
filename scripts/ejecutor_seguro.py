#!/usr/bin/env python3
"""
ejecutor_seguro.py — "El Túnel Seguro"
Wrapper para prevenir que la IA (o n8n) se cuelgue al ejecutar comandos del sistema.
Provee timeouts duros, truncado automático de salidas inmensas y manejo robusto de errores
evitando strings rotos o bloqueos asíncronos en los MCP.

Uso:
    python scripts/ejecutor_seguro.py "docker ps"
    python scripts/ejecutor_seguro.py "find / -name '*.log'" --max-chars 5000 --timeout 5
"""

import subprocess
import json
import argparse
import sys
import os

def ejecutar_comando(comando: str, timeout: int = 10, max_chars: int = 2000) -> dict:
    """
    Ejecuta un comando del sistema con protecciones fuertes.
    Retorna un diccionario estructurado (ideal para JSON).
    """
    try:
        # Ejecutamos de forma síncrona, con captura de std y timeout estricto
        proceso = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            executable="/bin/bash" # Fomentar entorno predecible
        )
        
        stdout_str = proceso.stdout or ""
        stderr_str = proceso.stderr or ""
        
        # Truncado de seguridad para no ahogar el contexto del LLM
        truncated = False
        if len(stdout_str) > max_chars:
            stdout_str = stdout_str[:max_chars] + f"\n... [TRUNCADO: Salida excede los {max_chars} caracteres]"
            truncated = True
            
        if len(stderr_str) > max_chars:
            stderr_str = stderr_str[:max_chars] + f"\n... [TRUNCADO: Error excede los {max_chars} caracteres]"
            truncated = True

        return {
            "estado": "exito" if proceso.returncode == 0 else "fallo",
            "codigo_salida": proceso.returncode,
            "stdout": stdout_str,
            "stderr": stderr_str,
            "truncado": truncated,
            "comando_original": comando
        }

    except subprocess.TimeoutExpired:
        # El comando se colgó y tuvo que ser matado por el timeout
        return {
            "estado": "timeout",
            "codigo_salida": -1,
            "stdout": "",
            "stderr": f"TIMEOUT EXCEDIDO ({timeout}s). El proceso fue terminado para evitar que la IA se cuelgue.",
            "truncado": False,
            "comando_original": comando
        }
    except Exception as e:
        # Cualquier otro pánico
        return {
            "estado": "error_interno",
            "codigo_salida": -1,
            "stdout": "",
            "stderr": f"Error del wrapper ejecutando comando: {str(e)}",
            "truncado": False,
            "comando_original": comando
        }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Túnel seguro para agentes IA ejecutando Shell.")
    parser.add_argument("comando", type=str, help="El comando bash a ejecutar.")
    parser.add_argument("--timeout", type=int, default=10, help="Segundos máximos antes de matar el proceso. (default: 10)")
    parser.add_argument("--max-chars", type=int, default=2000, help="Caracteres máximos de salida antes de truncar. (default: 2000)")
    parser.add_argument("--formato", type=str, choices=["json", "texto"], default="json", help="Formato de salida (default: json)")

    args = parser.parse_args()

    resultado = ejecutar_comando(args.comando, timeout=args.timeout, max_chars=args.max_chars)

    if args.formato == "json":
        # Ensure ASCII is false to allow internal unicode
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        # Salida modo texto (human readable)
        print(f"ESTADO: {resultado['estado'].upper()} (Cod: {resultado['codigo_salida']})")
        if resultado['stderr']:
            print(f"--- ERRORES ---\n{resultado['stderr']}")
        if resultado['stdout']:
            print(f"--- SALIDA ---\n{resultado['stdout']}")
        if resultado['truncado']:
            print("--- ADVERTENCIA: SALIDA TRUNCADA ---")

    # Salimos con el mismo código que el sub-proceso, salvo en timeout
    if resultado["estado"] == "timeout":
        sys.exit(124) # Convención standard de timeout de shell
    else:
        sys.exit(resultado["codigo_salida"])
