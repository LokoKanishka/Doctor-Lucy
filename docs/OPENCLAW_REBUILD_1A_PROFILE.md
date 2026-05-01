# REBUILD-1A — Bootstrap de perfil paralelo

## 1. Objetivo
Validar la creación de un entorno limpio mediante `--profile rebuild-test`.

## 2. Ejecución
- **Estado paralelo**: Creado en `~/.openclaw-rebuild-test`.
- **Aislamiento**: Confirmado. `~/.openclaw` original no fue modificado.
- **Gateway**: Levantado en puerto `18790`.
- **Autorización**: El nuevo `device-auth.json` ya contiene el scope `operator.read`.

## 3. Resultado
Exitoso. La instancia paralela nació con los permisos correctos que la instancia original perdió.
