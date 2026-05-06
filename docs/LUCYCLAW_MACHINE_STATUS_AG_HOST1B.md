# LucyClaw Machine Status Monitoring (AG-HOST1B)

## Objetivo
Proveer a LucyClaw de capacidades de observación real del estado del sistema host de forma segura y de solo lectura. Esto permite diagnosticar cuellos de botella de hardware o procesos sin riesgo de alteración del sistema.

## Comandos Disponibles
- `/machine_status`: Resumen general de CPU, RAM, Disco y GPU.
- `/machine_processes`: Listado de los 10 procesos con mayor consumo de CPU.
- `/machine_ram`: Detalle del uso de memoria RAM (MemTotal vs MemAvailable).
- `/machine_disk`: Detalle del uso de espacio en el disco raíz `/`.
- `/machine_gpu`: Estado de la GPU/VRAM (requiere `nvidia-smi`).

## Seguridad y Limitaciones
- **Solo Lectura**: Ningún comando permite modificar procesos o archivos.
- **Sin Sudo**: Todos los datos se obtienen como el usuario actual o vía `/proc`.
- **Aislamiento**: No se accede a archivos sensibles (`.env`, `n8n_data`, etc.).
- **Comandos Fijos**: El wrapper Python solo ejecuta comandos de sistema pre-aprobados (`ps`, `uptime`, `nvidia-smi`).

## Próximo Paso
AG-HOST1C: Implementar lectura segura de documentos permitidos (PDF, DOCX, TXT).
