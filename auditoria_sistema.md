# 🔍 Auditoría del Sistema — Doctor Lucy
**Última actualización:** 2026-03-02 01:18:57 -03
**Host:** lucy-ubuntu-System-Product-Name | **Usuario:** lucy-ubuntu

---

## 💻 Estado del Sistema
- **OS:** Ubuntu 24.04.4 LTS
- **Kernel:** 6.17.0-14-generic
- **Uptime:** up 6 hours, 32 minutes
- **Carga promedio:** 0,61, 0,61, 0,60

## ⚙️ Recursos
- **Memoria (free -h):**
```
               total       usado       libre  compartido   búf/caché  disponible
Mem:           124Gi        27Gi        71Gi       245Mi        27Gi        97Gi
Inter:         8,0Gi          0B       8,0Gi
```
- **Disco raíz (df -h /):**
```
S.ficheros     Tamaño Usados  Disp Uso% Montado en
/dev/sda2        457G   243G  191G  56% /
```

## 🔒 Seguridad básica
### Puertos en escucha no-localhost
```
udp 0.0.0.0:47864 
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=2065,fd=34))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=2065,fd=33))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=2065,fd=29))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=2065,fd=25))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=2065,fd=31))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=2065,fd=30))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=2065,fd=28))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=2065,fd=26))
udp 0.0.0.0:5353 users:(("openclaw-gatewa",pid=2065,fd=24))
udp 0.0.0.0:5353 
udp [::]:42251 
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
NAMES                      STATUS                 PORTS
searxng-lucy               Up 7 hours             127.0.0.1:8080->8080/tcp
qdrant-lucy                Up 7 hours             127.0.0.1:6335->6333/tcp, 127.0.0.1:6336->6334/tcp
n8n-lucy                   Up 3 hours             127.0.0.1:5688->5678/tcp
lucy_fusion_ui_panel       Up 7 hours (healthy)   127.0.0.1:5111->5100/tcp
lucy_fusion_antigravity    Up 7 hours (healthy)   127.0.0.1:5011->5000/tcp
lucy_fusion_n8n            Up 7 hours (healthy)   127.0.0.1:5690->5678/tcp
lucy_fusion_searxng        Up 7 hours             127.0.0.1:8088->8080/tcp
lucy_fusion_socket_proxy   Up 7 hours             127.0.0.1:2377->2375/tcp
lucy_fusion_redis          Up 7 hours             6379/tcp
lucy_fusion_qdrant         Up 7 hours             6334/tcp, 127.0.0.1:6339->6333/tcp
lucy_brain_runners         Up 7 hours (healthy)   
lucy_brain_n8n             Up 7 hours (healthy)   
lucy_eyes_searxng          Up 7 hours             127.0.0.1:8081->8080/tcp
lucy_hands_antigravity     Up 6 hours (healthy)   127.0.0.1:5000->5000/tcp
lucy_ui_panel              Up 7 hours (healthy)   
lucy_memory_qdrant         Up 7 hours             127.0.0.1:6333->6333/tcp, 6334/tcp
lucy_memory_redis          Up 7 hours             6379/tcp
lucy_docker_socket_proxy   Up 7 hours             127.0.0.1:2375->2375/tcp
lucy_voice_alltalk         Up 7 hours             0.0.0.0:7851->7851/tcp, [::]:7851->7851/tcp
lucy_open_webui            Up 7 hours (healthy)   127.0.0.1:3001->8080/tcp
lucy_ui_dockge             Up 7 hours (healthy)   127.0.0.1:5001->5001/tcp
antigravity_container      Up 6 hours             
```

## ✅ Recomendaciones rápidas
- Revisar puertos expuestos a 0.0.0.0 / [::] y cerrar los no necesarios.
- Si hay poco espacio en /, correr limpieza de paquetes y cachés.
- Validar que servicios críticos de Docker estén en estado healthy.

---
*Auditoría generada automáticamente por scripts/auditoria.sh*
