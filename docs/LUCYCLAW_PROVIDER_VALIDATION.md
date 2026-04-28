# LucyClaw — Validación controlada de providers

> Tramo 12 (2026-04-28)
> Rama: `memoria/bunker` · HEAD: `b62ef21`

---

## 1. Fecha y contexto

- **Tramo:** 12 — Validación controlada
- **Sin cambio de routing.** El primary sigue siendo `ollama/qwen2.5-coder:14b`.
- **Sin token/API key impresa.** Las llamadas se hicieron leyendo keys de `auth-profiles.json` programáticamente.
- **Método:** Llamadas HTTP directas a las APIs de cada provider (sin pasar por OpenClaw CLI/gateway para evitar el bloqueo del Service Token 401).

---

## 2. Routing actual (sin cambios)

| Rol | Modelo |
|---|---|
| Primary | `ollama/qwen2.5-coder:14b` |
| Fallback #1 | `ollama/qwen3-coder:30b-a3b-q8_0` |
| Fallback #2 | `ollama/devstral-small-2:latest` |
| Fallback #3 | `google/gemini-2.5-flash` |

---

## 3. Providers probados

| Provider/Modelo | Tipo | Status HTTP | Resultado | Detalle | ¿Primary? |
|---|---|---|---|---|---|
| `google/gemini-2.5-flash` | API key personal | `200 OK` | ✅ **FUNCIONA** | Respondió "OK". 1 token output, 15 thinking. Key default válida. | ✅ Candidato |
| `openai/gpt-4o-mini` | API key personal | `429` | ❌ **SIN CUOTA** | `insufficient_quota` — la key `sk-proj-...` no tiene créditos. | ❌ Descartado |
| `anthropic/claude-sonnet-4` | API key personal | `401` | ❌ **KEY INVÁLIDA** | `invalid x-api-key` — la key almacenada no es válida o fue revocada. | ❌ Descartado |
| `ollama/qwen2.5-coder:14b` | Local | `200 OK` | ✅ **FUNCIONA** | Respondió "OK". Funcional en máquina grande. | Solo fallback |
| `openai-codex/gpt-5.4` | OAuth nativo (gateway) | `401` | ⚠️ **BLOQUEADO** | El gateway rechaza con `Unauthorized`. El OAuth de Codex podría funcionar, pero el Service Token del gateway bloquea toda comunicación HTTP. No se pudo validar Codex directamente. | ⚠️ Pendiente |

---

## 4. Conclusiones

### Funciona HOY:
- **Google Gemini (`gemini-2.5-flash`)**: La key `google:default` responde correctamente. A pesar de los `failure[rate_limit]` históricos, una llamada individual funciona. Esto no garantiza estabilidad bajo carga, pero confirma que la key es válida y tiene cuota disponible.
- **Ollama local**: Funcional en la máquina grande (como se esperaba).

### No funciona HOY:
- **OpenAI personal (`sk-proj-...`)**: Sin créditos. La cuenta no tiene plan activo. Descartado como provider hasta que Diego cargue créditos.
- **Anthropic (`sk...ey`)**: Key inválida o revocada. Descartado hasta obtener una key válida.

### Bloqueado por Service Token (no validable aún):
- **OpenAI Codex OAuth**: El mecanismo de OAuth Codex existe y tiene cuota (74% diaria, 96% semanal), pero el gateway de OpenClaw rechaza toda comunicación HTTP con `401 Unauthorized` porque el Service Token actual no tiene los scopes correctos. Para validar Codex se necesita primero resolver el token del gateway.

### Hallazgo importante sobre Codex:
El proveedor nativo `openai-codex` **no se puede validar vía API directa** como los otros providers porque:
1. Su `baseURL` es `https://chatgpt.com/backend-api` — un endpoint que requiere OAuth cookie/session, no una simple API key.
2. Solo funciona a través del gateway de OpenClaw (que gestiona el OAuth internamente).
3. El gateway está bloqueado por el Service Token 401.
4. **Para desbloquear Codex, primero hay que resolver el Service Token.**

---

## 5. Recomendación de routing basada en evidencia

> [!IMPORTANT]
> **No aplicar todavía.** Esta es la recomendación basada en la validación realizada.

### Opción A — Migrar ahora con lo que funciona:
```
Primary:    google/gemini-2.5-flash          [CLOUD — validado ✅]
Fallback 1: ollama/qwen2.5-coder:14b        [LOCAL — validado ✅]
```
- **Pro:** Se puede hacer inmediatamente sin resolver el Service Token.
- **Contra:** Sin segundo provider cloud como fallback. Si Gemini entra en rate limit, solo queda Ollama local (no portable a notebook).

### Opción B — Resolver Service Token primero, luego migrar con Codex:
```
Primary:    openai-codex/gpt-5.4             [CLOUD — nativo, pendiente validación]
Fallback 1: google/gemini-2.5-flash          [CLOUD — validado ✅]
Fallback 2: ollama/qwen2.5-coder:14b        [LOCAL — solo PC grande]
```
- **Pro:** Codex es el proveedor nativo de OpenClaw con mayor integración. La cadena tiene dos providers cloud.
- **Contra:** Requiere resolver el Service Token del gateway antes.

---

## 6. Próximo tramo

### Si se elige Opción A (migrar ya con Gemini):
**TRAMO 13A — Migrar routing a Gemini primary (sin resolver token gateway)**
- Hacer backup, ejecutar `openclaw models set google/gemini-2.5-flash`, validar.
- El gateway sigue en 401, pero el CLI local con `--local` podría funcionar.

### Si se elige Opción B (resolver token primero):
**TRAMO 13B — Resolver Service Token del gateway OpenClaw**
- Usar `scripts/openclaw_install_lucy_token.py` con Diego presente.
- Validar que el gateway responde con 200 en `/v1/models`.
- Luego validar Codex OAuth vía gateway.
- Luego migrar routing con evidencia completa.

### Recomendación del agente:
**Opción B es más sólida.** Resolver el Service Token desbloquea tanto Codex como toda la funcionalidad del gateway (Telegram, bridge, exoesqueleto). Sin el token, la mitad de la arquitectura LucyClaw queda inoperante sin importar qué provider se elija como primary.
