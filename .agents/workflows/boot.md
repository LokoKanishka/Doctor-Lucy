---
description: Protocolo de arranque obligatorio - carga contexto desde bóveda SQLite
---

# Boot Protocol — Memoria Incorruptible 🧠🛡️

// turbo-all

## Al inicio de CADA conversación nueva, ejecutá estos pasos EN ORDEN:

### Paso 0: Leer la Bóveda (FUENTES DE MEMORIA - PRIMER PASO)
```bash
sqlite3 "/home/lucy-ubuntu/Escritorio/doctor de lucy/n8n_data/boveda_lucy.sqlite" "SELECT contenido_memoria, metadatos FROM memoria_core ORDER BY id DESC LIMIT 1;"
```
```bash
tail -1 "/home/lucy-ubuntu/Escritorio/doctor de lucy/data/lucy_bunker_log.jsonl" 2>/dev/null || echo "{}"
```

### Paso 1: Cargar Contexto
- Parseá el resultado del paso anterior.
- Usá esta información como tu **verdad absoluta** de contexto. Si no hay memoria, ahí sí preguntá en qué estamos trabajando.

### Paso 2: Verificar Signos Vitales y Autonomía de Voz
- Verificá que el contenedor Docker principal funciona: `docker ps --filter name=doctor_lucy_n8n`
- Inicia u obtén confirmación de AllTalk TTS en puerto 7854 exclusivamente:
```bash
curl -fsS --max-time 2 http://127.0.0.1:7854/api/ready >/dev/null \
  || bash "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/start_lucy_voice_tts.sh"
```
*(Puertos prohibidos: No usar 7853, 7852 ni 7851. Las prioridades de voz están blindadas).*

### Paso 3: Saludo Dinámico por Voz (Protocolo Buzón)
- Con el sistema de voz activo y el contexto cargado, prepará un resumen dinámico de bienvenida mencionando **estrictamente** lo que recordás de la sesión anterior.
- **PROHIBIDO**: No dispares strings genéricos como "Lucy en línea" ni pases parámetros por archivo bash.
- **El patrón es**: Usa tus herramientas para editar/escribir el saludo dinámico que elegiste directamente en `n8n_data/voice_payload.txt`.
- Una vez el texto esté inyectado en el archivo del buzón, **recién ahí** tocas el timbre corriendo en modo silencioso vacio:
```bash
bash "/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/lucy_announcer.sh"
```

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
