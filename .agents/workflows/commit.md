---
description: Protocolo de cierre de sesión - commit de memoria y push a la nube
---

# Commit Protocol — Cierre de Sesión 🧠💾

// turbo-all

## Cuando el usuario dice "commit", "guardá", "hacé push", o señal de cierre:

### Paso 1: Compilar Resumen de Sesión
- Resumí: quién sos, qué hiciste en esta sesión, qué quedó pendiente, qué MCP/tools tenés.

### Paso 2: Escribir en Bóveda SQLite
```bash
sqlite3 "/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/boveda_lucy.sqlite" "INSERT INTO memoria_core (rol, contenido_memoria, metadatos) VALUES ('lucy_agent', '<resumen_compilado>', '<metadatos_json>');"
```

### Paso 3: Sincronizar al Búnker JSONL
```bash
python3 "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/sync_memory_to_n8n.py"
```

### Paso 4: Git add + commit + push
```bash
cd "/home/lucy-ubuntu/Escritorio/doctor de lucy" && git add -A && git status
```
```bash
cd "/home/lucy-ubuntu/Escritorio/doctor de lucy" && git commit -m "🧠 sesión: <resumen_breve>"
```
```bash
cd "/home/lucy-ubuntu/Escritorio/doctor de lucy" && git push origin main
```

### Paso 5: Confirmar al usuario
- Informar que la bóveda fue actualizada, el búnker sincronizado y el push exitoso.
