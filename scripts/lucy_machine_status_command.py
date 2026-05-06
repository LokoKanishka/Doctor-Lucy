#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import shutil
import platform
import time
import socket

def run_cmd(args):
    try:
        proc = subprocess.run(
            args,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            timeout=5
        )
        return proc.stdout.strip(), proc.stderr.strip(), proc.returncode
    except Exception as e:
        return "", str(e), -1

def get_ram():
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
        mem = {}
        for line in lines:
            if ":" not in line: continue
            parts = line.split(":")
            key = parts[0].strip()
            val = parts[1].strip().split()[0]
            mem[key] = int(val)
        
        total_kb = mem.get("MemTotal", 0)
        available_kb = mem.get("MemAvailable", 0)
        used_kb = total_kb - available_kb
        
        return {
            "total_mb": round(total_kb / 1024, 2),
            "available_mb": round(available_kb / 1024, 2),
            "used_mb": round(used_kb / 1024, 2),
            "used_percent": round((used_kb / total_kb) * 100, 2) if total_kb > 0 else 0
        }
    except Exception as e:
        return {"error": f"Could not read RAM: {str(e)}"}

def get_cpu():
    try:
        # Load avg
        uptime_out, _, _ = run_cmd(["uptime"])
        load = uptime_out.split("load average:")[-1].strip() if "load average:" in uptime_out else "unknown"
        
        # CPU Info
        with open("/proc/cpuinfo", "r") as f:
            cpu_data = f.read()
        
        count = cpu_data.count("processor\t:")
        model = "unknown"
        for line in cpu_data.split("\n"):
            if "model name" in line:
                model = line.split(":")[-1].strip()
                break
                
        return {
            "model": model,
            "cores": count,
            "load_average": load
        }
    except Exception as e:
        return {"error": f"Could not read CPU: {str(e)}"}

def get_disk(path="/"):
    try:
        usage = shutil.disk_usage(path)
        return {
            "path": path,
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "used_percent": round((usage.used / usage.total) * 100, 2)
        }
    except Exception as e:
        return {"error": f"Could not read disk: {str(e)}"}

def get_gpu():
    if shutil.which("nvidia-smi") is None:
        return {"ok": False, "error": "nvidia-smi not available"}
    
    out, err, code = run_cmd(["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader,nounits"])
    if code != 0:
        return {"ok": False, "error": "nvidia-smi failed", "details": err}
    
    try:
        parts = [p.strip() for p in out.split(",")]
        return {
            "ok": True,
            "name": parts[0],
            "utilization_percent": int(parts[1]),
            "memory_used_mib": int(parts[2]),
            "memory_total_mib": int(parts[3]),
            "temperature_c": int(parts[4])
        }
    except Exception as e:
        return {"ok": False, "error": f"Failed to parse GPU data: {str(e)}"}

def get_processes():
    # ps aux --sort=-%cpu | head -n 11
    out, err, code = run_cmd(["ps", "aux", "--sort=-%cpu"])
    if code != 0:
        return {"error": "ps failed", "details": err}
    
    lines = [l.strip() for l in out.split("\n") if l.strip()]
    if not lines:
        return {"error": "no processes found"}
        
    header = lines[0]
    top = lines[1:11] # Top 10 processes
    
    return {
        "header": header,
        "top_processes": top
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Missing command argument"}))
        sys.exit(1)

    cmd = sys.argv[1]
    result = {"ok": True, "command": f"machine_{cmd}", "mode": "read-only"}

    if cmd == "status":
        gpu_info = get_gpu()
        result["data"] = {
            "cpu": get_cpu(),
            "ram": get_ram(),
            "disk": get_disk(),
            "gpu": gpu_info if gpu_info.get("ok") else {"error": gpu_info.get("error")},
            "processes": get_processes().get("top_processes", [])
        }
    elif cmd == "processes":
        result["data"] = get_processes()
    elif cmd == "ram":
        result["data"] = get_ram()
    elif cmd == "disk":
        result["data"] = get_disk()
    elif cmd == "gpu":
        gpu_info = get_gpu()
        if not gpu_info.get("ok"):
            result["ok"] = False
            result["error"] = gpu_info.get("error")
            result["details"] = gpu_info.get("details", "")
        else:
            result["data"] = gpu_info
    else:
        result["ok"] = False
        result["error"] = f"Unknown command: {cmd}"

    result["mutation_allowed"] = False
    result["sudo_used"] = False
    result["shell_used"] = False
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
