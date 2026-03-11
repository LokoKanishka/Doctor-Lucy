# Workflow de Preservación de Memoria (Bunker)

Para evitar la contaminación de las ramas técnicas y Pull Requests con commits administrativos, el sistema utiliza un mecanismo de "Rama de Sombra" (Bunker Sidecar).

## Cómo funciona

El hook `.git/hooks/pre-push` intercepta cada intento de `git push` y realiza las siguientes acciones:

1. **Detección de Cambios:** Identifica si hay cambios en archivos de memoria vitales:
   - `data/lucy_bunker_log.jsonl`
   - `auditoria_sistema.md`
   - y otros archivos de bitácora.
2. **Aislamiento:** Extrae esos cambios de la rama actual (técnica) y los mueve temporalmente al `stash`.
3. **Persistencia Lateral:**
   - Salta a la rama `memoria/bunker`.
   - Aplica los cambios de memoria.
   - Crea un commit administrativo independiente.
   - Realiza un `push origin memoria/bunker`.
4. **Restauración:** Vuelve a la rama técnica original y restaura los archivos modificados localmente para que el usuario pueda seguir trabajando, pero **sin incluirlos en el commit técnico** que se está pusheando.

## Beneficios

- **Historial Limpio:** Los PRs solo muestran código funcional.
- **Memoria Continua:** La rama `memoria/bunker` mantiene una línea de tiempo ininterrumpida del estado del sistema.
- **Transparencia:** El desarrollador no tiene que preocuparse por commitear logs manualmente.

---
*Mecanismo implementado por Antigravity — TICKET ANTIGRAVITY*
