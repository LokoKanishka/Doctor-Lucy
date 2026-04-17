---
description: Protocolo de arranque obligatorio - carga contexto desde bóveda SQLite
---

# Boot Protocol — Memoria Incorruptible 🧠🛡️

// turbo-all

## Al inicio de CADA conversación nueva, ejecutá estos pasos EN ORDEN:

### Paso 0: Verificar y Activar Voz (SIEMPRE PRIMERO)
```bash
ss -tunlp | grep 7851 || (cd /home/lucy-ubuntu/Archivo_proyectos/Taverna/Taverna-legacy/alltalk_tts && ./launch.sh > alltalk.log 2>&1 & sleep 30)
```
- Si el puerto 7851 no responde, lanzar AllTalk en background y esperar 30 segundos.
- Una vez activo, disparar **saludo de voz obligatorio** al finalizar el boot:
```bash
bash "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_announcer.sh" "Lucy en línea. Sistema de voz activo. Memoria cargada y lista para operar."
```

### Paso 1: Leer la Bóveda (fuente primaria)
```bash
sqlite3 "/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/boveda_lucy.sqlite" "SELECT contenido_memoria, metadatos FROM memoria_core ORDER BY id DESC LIMIT 1;"
```

### Paso 1b: Leer el Búnker JSONL (fuente secundaria)
```bash
tail -1 "/home/lucy-ubuntu/Escritorio/doctor de lucy/data/lucy_bunker_log.jsonl" 2>/dev/null || echo "{}"
```

### Paso 2: Cargar Contexto
- Parseá el resultado del paso anterior.
- `contenido_memoria` = tu identidad, estado, capacidades y trabajo pendiente.
- `metadatos` = JSON con sesión, usuario, skills MCP activos.
- El búnker JSONL complementa con stats del Knowledge Graph y timestamps de sync.
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
