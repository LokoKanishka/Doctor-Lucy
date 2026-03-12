---
description: Auditoría completa del sistema - hardware, software, procesos, red y seguridad
---

# Auditoría Completa del Sistema

Este workflow recolecta el estado completo de la PC de Lucy y genera el archivo `diagnostics/auditoria_sistema.md` actualizado en el repositorio.

## Pasos

// turbo-all

1. Recolectar info del OS y uptime:
```bash
cat /etc/os-release && uname -r && uptime && hostname
```

2. Recolectar info de CPU y RAM:
```bash
lscpu | grep -E "Model name|Architecture|CPU\(s\)|Thread|Socket|MHz|Cache" && free -h && cat /proc/meminfo | grep -E "MemTotal|MemFree|SwapTotal|SwapFree"
```

3. Recolectar info de GPU (NVIDIA):
```bash
nvidia-smi --query-gpu=name,memory.total,driver_version,temperature.gpu,utilization.gpu --format=csv,noheader 2>/dev/null || echo "GPU no disponible"
```

4. Recolectar estado de discos:
```bash
df -h && lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE
```

5. Listar servicios systemd activos:
```bash
systemctl list-units --type=service --state=running --no-pager
```

6. Listar puertos abiertos:
```bash
ss -tulpn
```

7. Listar procesos por uso de RAM:
```bash
ps aux --sort=-%mem | head -25
```

8. Listar modelos Ollama:
```bash
ollama list 2>/dev/null || echo "Ollama no disponible"
```

9. Listar contenedores Docker:
```bash
docker ps && docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "Docker no disponible"
```

10. Listar usuarios del sistema:
```bash
cat /etc/passwd | grep -v nologin | grep -v false | cut -d: -f1
```

11. Recolectar aplicaciones instaladas relevantes (snap + apt):
```bash
snap list 2>/dev/null && dpkg -l | grep -E "^ii" | awk '{print $2, $3}' | grep -E "code|chrome|firefox|docker|node|python3|postgresql|nginx|cloudflared|ollama|antigravity|cuda|nvidia" | sort
```

12. Con todos los datos recolectados, actualizar el archivo `auditoria_sistema.md` en el repositorio `/home/lucy-ubuntu/Escritorio/doctor de lucy/diagnostics/auditoria_sistema.md` con la información actualizada, incluyendo:
   - Fecha y hora de la auditoría
   - Estado del sistema (OS, kernel, uptime)
   - Hardware (CPU, RAM, GPU)
   - Almacenamiento (discos, particiones, uso)
   - Servicios activos
   - Puertos abiertos y qué proceso los usa
   - Procesos más pesados
   - Modelos Ollama instalados
   - Contenedores Docker
   - Software clave instalado
   - Observaciones de seguridad
   - Notas / acciones pendientes

13. Actualizar también la `docs/bitacora_mantenimiento.md` con la fecha de la última auditoría.

14. Hacer commit de los cambios al repositorio git si hay cambios.
