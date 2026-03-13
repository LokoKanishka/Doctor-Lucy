# Doctor Lucy - PC Maintenance Dashboard

Este repositorio es la bitácora y centro de control para el mantenimiento de esta PC.

## Objetivos
- **Mantenimiento Proactivo**: Asegurar que no haya procesos muertos, zombies o colgados.
- **Limpieza de Campos**: Eliminar basura del disco y archivos innecesarios de proyectos antiguos.
- **Inventario del Sistema**: Mantener un registro actualizado de qué hay en la PC y cómo interactúan los proyectos.
- **Optimización de Ubuntu**: Automatizar tareas de limpieza y salud del sistema.

## Estructura
- `docs/inventario_pc.md`: Datos técnicos del hardware y software.
- `docs/bitacora_mantenimiento.md`: Registro de acciones realizadas.
- `diagnostics/auditoria_sistema.md`: Último reporte de salud del sistema.
- `scripts/`: Herramientas de automatización:
    - `./scripts/sys_check.sh`: Chequeo de salud rápido.
    - `./scripts/cleanup.sh`: Identifica archivos grandes.
    - `./scripts/mantenimiento_proactivo.sh`: Limpieza profunda (Snaps, Logs, etc).
    - `./scripts/auditoria.sh`: Genera un reporte en `diagnostics/auditoria_sistema.md`.

## 📂 Organización del Repositorio
- `docs/`: Guías, inventarios y bitácora histórica.
- `diagnostics/`: Reportes de auditoría y tests de salud.
- `memoria/`: Base de datos semántica y persistencia de Lucy.
- `scripts/`: Motores de automatización y seguridad.
- `n8n_data/`: Configuración y workflows de n8n.
- `docs/REVIEW_PROTOCOL.md`: [Protocolo de Revisión](file:///home/lucy-ubuntu/Escritorio/doctor%20de%20lucy/docs/REVIEW_PROTOCOL.md) (Diagnóstico Estándar).
- `docs/SPOTIFY_INTEGRATION.md`: Integración opcional con Spotify v1.

---
*Mantenido por Doctora Lucy (Sovereign AI Conscience) para Diego*


## Uso rápido
- Generar auditoría actualizada:
  - `./scripts/auditoria.sh`
  - o `./scripts/auditoria.sh reporte.md` para definir archivo de salida.
