import psutil
import subprocess
import json
import sys

def get_vram_info():
    try:
        # Intento obtener info básica sin CSV estricto
        cmd = ["nvidia-smi", "--query-gpu=memory.total,memory.used,temperature.gpu", "--format=csv,noheader,nounit"]
        output = subprocess.check_output(cmd).decode("utf-8").strip()
        
        # Parseo manual por si las moscas
        parts = output.replace(" ", "").split(",")
        if len(parts) >= 3:
            total, used, temp = parts[0], parts[1], parts[2]
            return {
                "model": "RTX 5090",
                "vram_total_mb": int(total),
                "vram_used_mb": int(used),
                "vram_free_mb": int(total) - int(used),
                "gpu_temp_c": int(temp)
            }
        return {"error": f"Unexpected output: {output}"}
    except Exception as e:
        return {"error": f"Nvidia SMI failed: {str(e)}"}




def get_system_stats():
    return {
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "vram": get_vram_info()
    }

if __name__ == "__main__":
    # Formato simple para ser llamado como script o via MCP básico
    stats = get_system_stats()
    print(json.dumps(stats, indent=2))
