---
description: Protocolo de arranque obligatorio - carga contexto desde bóveda SQLite
---

# Boot Protocol — Memoria Incorruptible 🧠🛡️

// turbo-all

## Al inicio de CADA conversación nueva, ejecutá estos pasos EN ORDEN:

### Paso 1: Leer la Bóveda
```bash
sqlite3 "/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/boveda_lucy.sqlite" "SELECT contenido_memoria, metadatos FROM memoria_core ORDER BY id DESC LIMIT 1;"
```

### Paso 2: Cargar Contexto
- Parseá el resultado del paso anterior.
- `contenido_memoria` = tu identidad, estado, capacidades y trabajo pendiente.
- `metadatos` = JSON con sesión, usuario, skills MCP activos.
- Usá esta información como tu **verdad absoluta** de contexto.

### Paso 3: Saludar con Contexto
- Saludá al usuario **mencionando lo que sabés** de la sesión anterior.
- NO preguntes "¿en qué proyecto trabajamos?" si la bóveda tiene datos.
- Si la bóveda está vacía, ahí sí preguntá.

---

## Al FINAL de cada conversación (cuando el usuario dice "commit"/"guardá"/"chau"):

### Paso 4: Compilar Resumen
- Resumí: quién sos, qué hiciste, qué quedó pendiente, qué MCP/tools tenés disponibles.

### Paso 5: Escribir en Bóveda
```bash
sqlite3 "/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/boveda_lucy.sqlite" "INSERT INTO memoria_core (rol, contenido_memoria, metadatos) VALUES ('lucy_agent', '<resumen>', '<metadatos_json>');"
```

### Paso 6: Confirmar
- Decile al usuario que la memoria fue grabada exitosamente.
