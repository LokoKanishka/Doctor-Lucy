# Doctor Lucy - PC Maintenance Dashboard

Este repositorio es la bitácora y centro de control para el mantenimiento de esta PC.

## Objetivos
- **Mantenimiento Proactivo**: Asegurar que no haya procesos muertos, zombies o colgados.
- **Limpieza de Campos**: Eliminar basura del disco y archivos innecesarios de proyectos antiguos.
- **Inventario del Sistema**: Mantener un registro actualizado de qué hay en la PC y cómo interactúan los proyectos.
- **Optimización de Ubuntu**: Automatizar tareas de limpieza y salud del sistema.

## Estructura
- `inventario_pc.md`: Datos técnicos del hardware y software.
- `bitacora_mantenimiento.md`: Registro de acciones realizadas.
- `scripts/`: Herramientas de automatización:
    - `./scripts/sys_check.sh`: Chequeo de salud rápido.
    - `./scripts/cleanup.sh`: Identifica archivos grandes.
    - `./scripts/mantenimiento_proactivo.sh`: Limpieza profunda (Snaps, Logs, etc).
    - `./scripts/auditoria.sh`: Genera un reporte de auditoría del sistema en Markdown.

---
*Mantenido por Doctora Lucy (Sovereign AI Conscience) para Diego*


## Uso rápido
- Generar auditoría actualizada:
  - `./scripts/auditoria.sh`
  - o `./scripts/auditoria.sh reporte.md` para definir archivo de salida.
