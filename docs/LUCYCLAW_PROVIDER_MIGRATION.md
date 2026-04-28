# LucyClaw — Migración de Providers API-first

> Documento generado en Tramo 11 (2026-04-28).
> Rama: `memoria/bunker` · HEAD: `9f5f345`

---

## 1. Estado actual

### Modelo/provider routing

| Rol | Modelo | Tipo | Problema |
|---|---|---|---|
| **Primary** | `ollama/qwen2.5-coder:14b` | Local (Ollama) | Requiere GPU/VRAM |
| Fallback #1 | `ollama/qwen3-coder:30b-a3b-q8_0` | Local (Ollama) | Requiere aún más VRAM |
| Fallback #2 | `ollama/devstral-small-2:latest` | Local (Ollama) | Requiere GPU local |
| Fallback #3 | `google/gemini-2.5-flash` | Cloud/API | ✅ Correcto como concepto |

**Diagnóstico:** La cadena es **local-heavy**. Los tres primeros modelos dependen de Ollama local. Si Ollama no está activo o la máquina no tiene GPU suficiente, hay que fallar tres veces antes de llegar al único provider cloud.

### Provider registrado en `models.providers`

Solo **`ollama`** está registrado como bloque de provider formal en `openclaw.json`. No hay bloques `google`, `openai`, `anthropic` ni `openrouter` en esa sección.

### Agentes

| Agent ID | Modelo | Herencia |
|---|---|---|
| `main` | *(hereda defaults)* | Primary: `ollama/qwen2.5-coder:14b` |
| `fusion-research` | `google/gemini-2.5-flash` | Modelo propio (ya API-first) |

### Por qué contradice la arquitectura dual-host

- La notebook vieja no tiene RTX 5090 ni VRAM para correr Qwen 14B/30B.
- La cadena de fallback obliga a intentar 3 modelos locales imposibles antes de llegar a la API cloud.
- El agente `main` (que es LucyClaw) no puede funcionar sin Ollama pesado como está configurado.

---

## 2. Auth/API keys disponibles (sin imprimir valores)

> ⚠️ Hallazgo clave: Hay muchos más recursos cloud disponibles de lo que se veía en el JSON.

| Provider | API Keys disponibles | Fuente | Notas |
|---|---|---|---|
| **Google/Gemini** | **6 keys** | `auth-profiles.json` + `GEMINI_API_KEY` en `.env` | Pool rotativo listo para usar |
| **OpenAI** | 1 key | `auth-profiles.json` + `OPENAI_API_KEY` en `.env` | `sk-proj-...` |
| **OpenAI Codex** | OAuth activo | OAuth flow | 5h/75% left, expira en 2d |
| **Anthropic** | 1 key | `auth-profiles.json` | `sk...ey` |
| **Ollama** | marker local | `models.json` | Solo funciona en máquina grande |

**Conclusión:** Diego ya tiene las keys necesarias para Gemini (6 keys rotativas), OpenAI (1 key + OAuth Codex) y Anthropic (1 key). No hace falta generar ni pagar nada nuevo.

---

## 3. Objetivo de la migración

### Antes (local-heavy)
```
Primary:    ollama/qwen2.5-coder:14b        [LOCAL]
Fallback 1: ollama/qwen3-coder:30b-a3b-q8_0 [LOCAL]
Fallback 2: ollama/devstral-small-2:latest   [LOCAL]
Fallback 3: google/gemini-2.5-flash          [CLOUD]
```

### Después (API-first)
```
Primary:    google/gemini-2.5-flash          [CLOUD — 6 keys]
Fallback 1: openai-codex/gpt-5.4            [CLOUD — OAuth]
Fallback 2: ollama/qwen2.5-coder:14b        [LOCAL — solo PC grande]
```

---

## 4. Perfil máquina grande / casa

| Campo | Valor |
|---|---|
| Primary | `google/gemini-2.5-flash` |
| Fallback 1 | `openai-codex/gpt-5.4` |
| Fallback 2 | `ollama/qwen2.5-coder:14b` (local opcional) |
| Fallback 3 | `ollama/devstral-small-2:latest` (local opcional) |
| Nota | Ollama queda como safety net. Si las APIs cloud fallan, la PC grande puede responder localmente. |

## 5. Perfil notebook vieja / 24-7

| Campo | Valor |
|---|---|
| Primary | `google/gemini-2.5-flash` |
| Fallback 1 | `openai-codex/gpt-5.4` |
| Fallback 2 | *(ninguno local)* |
| Nota | Sin Ollama. Sin modelos locales. Consumo mínimo de CPU/RAM. Solo API cloud. |

---

## 6. Decisiones pendientes para Diego

1. **¿Gemini como primary?** Tiene 6 keys rotativas, 1M tokens de contexto, text+image. Parece la opción más fuerte y sin costo inmediato.
2. **¿OpenAI Codex como fallback 1?** Tiene OAuth activo con cuota semanal. Es potente pero la cuota se renueva semanalmente.
3. **¿Anthropic como alternativa?** Hay 1 key disponible. Se puede agregar como fallback adicional si se desea.
4. **¿Mantener Ollama solo en PC grande?** Lo propuesto es que quede como fallback #2/#3 solo cuando hay GPU disponible.
5. **¿Permisos operator.write desde el inicio?** ¿O arrancar solo con chat/razonamiento?
6. **¿Telegram habla con LucyClaw directa o puenteada por Doctora Lucy?**
7. **¿Cuándo preparar perfil notebook?** ¿Después de validar en PC grande?

---

## 7. Plan de migración propuesto

### Fase 1 — Backup (Tramo 12a)
```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/backups-tramo12/openclaw.json.pre-migration.bak
cp ~/.openclaw/agents/main/agent/auth-profiles.json ~/.openclaw/backups-tramo12/auth-profiles.json.pre-migration.bak
```

### Fase 2 — Cambiar routing del agente main (Tramo 12b)
Usando CLI de OpenClaw (no edición manual de JSON):
```bash
# Cambiar primary a Gemini
openclaw models set google/gemini-2.5-flash

# Limpiar fallbacks actuales
openclaw models fallbacks clear

# Agregar fallbacks en orden API-first
openclaw models fallbacks add openai-codex/gpt-5.4
openclaw models fallbacks add ollama/qwen2.5-coder:14b
```

### Fase 3 — Validar gateway (Tramo 12c)
```bash
# Health check
curl http://127.0.0.1:18789/health

# Listar modelos con token válido
curl -H "Authorization: Bearer $(cat ~/.openclaw/lucy-bridge-token)" http://127.0.0.1:18789/v1/models

# Test bridge HTTP
OPENCLAW_BRIDGE_MODE=http python3 scripts/lucy_openclaw_bridge.py "ping diagnóstico: respondé OK"
```

### Fase 4 — Validar Telegram (Tramo 12d)
Enviar mensaje de prueba desde Telegram y verificar que LucyClaw responda usando Gemini, no Ollama.

### Fase 5 — Validar exoesqueleto (Tramo 12e)
Desde Doctora Lucy/Antigravity, delegar una tarea a LucyClaw y verificar que el resultado vuelve.

### Fase 6 — Preparar perfil notebook (Tramo 13)
Crear config separada o script de perfilado que elimine fallbacks locales para la notebook.

---

## 8. Herramientas CLI disponibles para la migración

| Comando | Función | Seguro |
|---|---|---|
| `openclaw models set <model>` | Cambia el modelo primary | Sí (reversible) |
| `openclaw models fallbacks clear` | Limpia la cadena de fallback | Sí (con backup) |
| `openclaw models fallbacks add <model>` | Agrega un fallback | Sí |
| `openclaw models fallbacks remove <model>` | Quita un fallback específico | Sí |
| `openclaw models status` | Muestra estado actual | Solo lectura |
| `openclaw models list` | Lista modelos configurados | Solo lectura |

> **Ventaja:** La migración se puede hacer completamente vía CLI sin editar JSON a mano. Cada paso es atómico y reversible.

---

## 9. No hacer todavía

- No tocar tokens ni scopes (eso es un tramo separado).
- No cambiar providers sin backup previo.
- No ejecutar `operator.write`.
- No mover config a notebook hasta validar en máquina grande.
- No eliminar fallback local hasta tener API estable.
- No reiniciar gateway hasta aplicar cambios.

---

## 10. Riesgos identificados

| Riesgo | Mitigación |
|---|---|
| Keys de Gemini pueden tener rate limits | Hay 6 keys rotativas; OpenClaw puede manejar rotación |
| OAuth Codex expira en 2 días | Renovar antes de expiración |
| Service Token sigue en 401 | Resolver en tramo token separado, pero la migración de modelo no depende del token del gateway |
| Rollback | Backup pre-migración permite restaurar en un `cp` |
