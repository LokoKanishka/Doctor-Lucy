# 🔍 Auditoría del Sistema — Doctor Lucy
**Última actualización:** 2026-03-01 06:18:41 -03
**Host:** lucy-ubuntu-System-Product-Name | **Usuario:** lucy-ubuntu

---

## 💻 Estado del Sistema
- **OS:** Ubuntu 24.04.4 LTS
- **Kernel:** 6.17.0-14-generic
- **Uptime:** up 13 hours, 22 minutes
- **Carga promedio:** 1,02, 0,79, 1,27

## ⚙️ Recursos
- **Memoria (free -h):**
```
               total       usado       libre  compartido   búf/caché  disponible
Mem:           124Gi        20Gi        45Gi       174Mi        61Gi       104Gi
Inter:         8,0Gi          0B       8,0Gi
```
- **Disco raíz (df -h /):**
```
S.ficheros     Tamaño Usados  Disp Uso% Montado en
/dev/sda2        457G   250G  184G  58% /
```

## 🔒 Seguridad básica
### Puertos en escucha no-localhost
```
udp 0.0.0.0:36485 
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=29))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=28))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=25))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=34))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=33))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=32))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=31))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=30))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=26))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=352969,fd=24))
udp 0.0.0.0:5353 
udp [::]:51783 
udp [::]:5353 
tcp 0.0.0.0:7851 
tcp [::]:7851 
```

### Firewall
- UFW instalado. Estado:
```
Sin permisos para consultar ufw status
```

### Antivirus
- ClamAV no detectado.

## 🐳 Docker
```
NAMES                      STATUS                  PORTS
searxng-lucy               Up 3 hours              127.0.0.1:8080->8080/tcp
qdrant-lucy                Up 3 hours              127.0.0.1:6335->6333/tcp, 127.0.0.1:6336->6334/tcp
n8n-lucy                   Up 3 hours              127.0.0.1:5688->5678/tcp
lucy_fusion_ui_panel       Up 2 hours (healthy)    127.0.0.1:5111->5100/tcp
lucy_fusion_antigravity    Up 3 hours (healthy)    127.0.0.1:5011->5000/tcp
lucy_fusion_n8n            Up 3 hours (healthy)    127.0.0.1:5690->5678/tcp
lucy_fusion_searxng        Up 3 hours              127.0.0.1:8088->8080/tcp
lucy_fusion_socket_proxy   Up 3 hours              127.0.0.1:2377->2375/tcp
lucy_fusion_redis          Up 3 hours              6379/tcp
lucy_fusion_qdrant         Up 3 hours              6334/tcp, 127.0.0.1:6339->6333/tcp
lucy_brain_runners         Up 13 hours (healthy)   
lucy_brain_n8n             Up 13 hours (healthy)   
lucy_eyes_searxng          Up 13 hours             127.0.0.1:8081->8080/tcp
lucy_hands_antigravity     Up 13 hours (healthy)   127.0.0.1:5000->5000/tcp
lucy_ui_panel              Up 13 hours (healthy)   
lucy_memory_qdrant         Up 13 hours             127.0.0.1:6333->6333/tcp, 6334/tcp
lucy_memory_redis          Up 13 hours             6379/tcp
lucy_docker_socket_proxy   Up 13 hours             127.0.0.1:2375->2375/tcp
lucy_voice_alltalk         Up 13 hours             0.0.0.0:7851->7851/tcp, [::]:7851->7851/tcp
lucy_open_webui            Up 13 hours (healthy)   127.0.0.1:3001->8080/tcp
lucy_ui_dockge             Up 13 hours (healthy)   127.0.0.1:5001->5001/tcp
antigravity_container      Up 13 hours             
```

## ✅ Recomendaciones rápidas
- Revisar puertos expuestos a 0.0.0.0 / [::] y cerrar los no necesarios.
- Si hay poco espacio en /, correr limpieza de paquetes y cachés.
- Validar que servicios críticos de Docker estén en estado healthy.

---
*Auditoría generada automáticamente por scripts/auditoria.sh*
