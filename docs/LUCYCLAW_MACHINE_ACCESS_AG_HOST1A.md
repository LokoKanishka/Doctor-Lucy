# LucyClaw Machine Access (AG-HOST1A)

## Objetivo
Proveer capacidad de observación de archivos en la máquina host en modo lectura.

## Comandos
- `/machine_downloads`: Lista archivos en la carpeta de Descargas del usuario.
- `/machine_ls <path>`: Lista el contenido de una carpeta permitida.
- `/machine_stat <path>`: Obtiene metadatos (tamaño, tipo, fecha) de un archivo o carpeta.

## Seguridad
- **Read-Only**: Solo lectura de metadatos de archivos.
- **Rutas Permitidas**: `/home/lucy-ubuntu` y subcarpetas estándar (Descargas, Escritorio, etc).
- **Rutas Prohibidas**: `.env`, `.ssh`, `n8n_data`, `memoria`, `boveda`, etc.
- **Sin Shell**: El plugin no permite ejecución de comandos arbitrarios.
- **Sin Lectura de Contenido**: En esta fase (AG-HOST1A), no se permite leer el contenido de los archivos, solo listarlos.

## Próximo Paso
- AG-HOST1B: Lectura de contenido de documentos seguros.
