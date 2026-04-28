# Doctor-Lucy — Política de Memoria Viva

Este documento establece la política oficial de versionado y respaldo para la memoria central de Doctora Lucy (`n8n_data/boveda_lucy.sqlite`).

---

## 1. Qué es `boveda_lucy.sqlite`

Es la base de datos SQLite activa que almacena la memoria, registros y contexto a largo plazo de la agente Lucy. Opera como el núcleo cognitivo persistente y cambia de manera constante con cada interacción.

## 2. Por qué no debe trackearse como archivo vivo en Git

Git está diseñado para código fuente, no para bases de datos transaccionales en tiempo de ejecución. Mantener la base viva en Git provoca:
- Constantes conflictos de *merge* y archivos marcados como modificados (`M`).
- Hinchazón del repositorio local y remoto al almacenar versiones binarias completas.
- Riesgo de sobrescribir memoria reciente al cambiar de rama o revertir commits.

Por lo tanto, la base de datos se mantiene ignorada en Git, pero el archivo local **NUNCA DEBE SER BORRADO** del servidor.

## 3. Dónde se guarda el backup externo

Los respaldos de la memoria se almacenan fuera del repositorio de código, en la siguiente ruta por defecto:
```text
$HOME/Doctor_Lucy_Backups/boveda/
```
Cada backup genera un subdirectorio con la marca de tiempo (ej. `20260427_235510`).

## 4. Cómo ejecutar el backup

Utilice el script oficial provisto en el repositorio. Este script valida la integridad de la base (`PRAGMA quick_check`) antes de realizar la copia de seguridad.

```bash
./scripts/backup_boveda_lucy.sh
```

## 5. Qué archivos se preservan

El script de backup guarda de forma atómica:
- `boveda_lucy.sqlite`
- `boveda_lucy.sqlite-wal` (si existe)
- `boveda_lucy.sqlite-shm` (si existe)
- `SHA256SUMS.txt` (firmas criptográficas de los archivos respaldados)

## 6. Qué NO hacer

- **NO** ejecute `git add n8n_data/boveda_lucy.sqlite`.
- **NO** ejecute `git clean -fd` si no está 100% seguro de tener exclusiones adecuadas.
- **NO** ejecute `rm n8n_data/boveda_lucy.sqlite`.
- **NO** intente hacer un restore de backup mientras el daemon de Lucy o `n8n` estén operando sobre la base.

## 7. Cómo restaurar conceptualmente

Si la memoria se corrompe y necesita restaurarse desde un backup externo:
1. **Apagar servicios:** Detener daemons de Lucy, n8n y cualquier bridge.
2. **Renombrar actual:** Mover la base corrupta y sus archivos WAL/SHM a una ubicación temporal.
3. **Validar backup:** Ejecutar `sha256sum -c SHA256SUMS.txt` en la carpeta de backup.
4. **Copiar:** Copiar el archivo `.sqlite` (y WAL/SHM si aplican) a `n8n_data/`.
5. **Reiniciar:** Levantar servicios.

## 8. Relación con `docs/ARCHITECTURE.md`

Este documento detalla el cumplimiento del punto dictado en `ARCHITECTURE.md` (Sección 6) sobre el manejo de la memoria persistente viva. Ambos documentos son la referencia canónica del estado estructural del proyecto.
