# LucyClaw — Migración de Providers API-first

> Documento generado en Tramo 11 (2026-04-28).
> **Corregido en Tramo 11.5** — Supuestos sobre providers calificados y proveedor nativo auditado.
> Rama: `memoria/bunker`

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

### Providers registrados

En `openclaw.json` → `models.providers`: solo **`ollama`**.

En `agents/main/agent/models.json` → `providers`: **`google`**, **`ollama`**, **`openai-codex`**, **`google-2`** a **`google-6`**. Este archivo contiene la configuración real de providers con baseURL y modelos.

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

## 2. Auth/API keys detectadas (sin imprimir valores)

> [!WARNING]
> **Corrección Tramo 11.5:** La presencia de keys en archivos de configuración NO significa que sean funcionales ni confiables. Varias fueron creadas en intentos anteriores de Lucy y presentaron problemas de cuota, rotación y estabilidad. Ninguna está validada como producción.

| Provider | Keys detectadas | Fuente | Estado real |
|---|---|---|---|
| **Google/Gemini** | 6 perfiles | `auth-profiles.json` + `models.json` | ⚠️ **NO VALIDADO.** Historial de fallas: todas las 6 keys tienen `failure[rate_limit]` registrado. Diego reporta cuotas agotadas sin uso claro, rotación inestable, posible duplicación de cuentas. |
| **OpenAI** | 1 key | `auth-profiles.json` + `.env` | ⚠️ **NO VALIDADO.** Tiene `failure[rate_limit]: 1` registrado. |
| **OpenAI Codex** | OAuth activo | OAuth flow | ⚠️ **Parcialmente funcional.** OAuth activo, cuota 74% left, expira en 2d. Tiene `failure[rate_limit]: 2`. Historial de sesiones muestra uso real con `gpt-5.1-codex-mini`. Es el único provider con evidencia de funcionamiento previo real. |
| **Anthropic** | 1 key | `auth-profiles.json` | ⚠️ **NO VALIDADO.** Sin failure counts registrados, pero tampoco evidencia de uso exitoso. |
| **Ollama** | marker local | `models.json` | ✅ Funcional en máquina grande (requiere GPU). |

> [!CAUTION]
> Las "6 keys rotativas de Gemini" fueron un experimento anterior de Lucy. No son un pool de producción validado. Antes de confiar en ellas hay que probar cada una individualmente.

---

## 3. Proveedor nativo de OpenClaw/Clawbot

### Hallazgo crítico — OpenAI Codex como proveedor integrado

La auditoría de sesiones históricas y configuración revela que **OpenClaw tiene un mecanismo nativo de IA basado en OpenAI Codex**:

| Evidencia | Detalle |
|---|---|
| **Provider integrado** | `openai-codex` con API `openai-codex-responses` |
| **Base URL** | `https://chatgpt.com/backend-api` (endpoint propio de Codex) |
| **Auth** | OAuth nativo (no API key personal de Diego) |
| **Account ID** | `458bb91f-...` (cuenta vinculada por login OAuth) |
| **Modelo usado** | Historial muestra `gpt-5.1-codex-mini` y `gpt-5.4` |
| **Cuota actual** | 5h 74% left, semanal 96% left |
| **Expiración OAuth** | 2 días (renovable) |
| **Uso real confirmado** | Sesiones en `.openclaw/agents/main/sessions/` muestran interacciones reales con costos calculados |

**Conclusión:** Esto es lo que Diego recordaba: Clawbot/OpenClaw funcionaba "con su propia IA" porque viene con integración OAuth a OpenAI Codex. Diego no tuvo que cargar API keys personales porque el login OAuth vinculó su cuenta ChatGPT directamente.

### Implicaciones para la arquitectura

1. **OpenAI Codex (OAuth) es el proveedor nativo de OpenClaw.** No es una key personal pegada: es un flujo OAuth integrado en el producto.
2. **Las 6 keys de Google fueron agregadas después**, probablemente por Lucy en intentos de rotación/fallback.
3. **La key de OpenAI (`sk-proj-...`) es personal** y separada del OAuth de Codex.
4. **La key de Anthropic también es personal** y fue agregada manualmente.

---

## 4. Objetivo de la migración (revisado)

### Antes (local-heavy)
```
Primary:    ollama/qwen2.5-coder:14b        [LOCAL]
Fallback 1: ollama/qwen3-coder:30b-a3b-q8_0 [LOCAL]
Fallback 2: ollama/devstral-small-2:latest   [LOCAL]
Fallback 3: google/gemini-2.5-flash          [CLOUD — no validado]
```

### Después (API-first — pendiente validación)
```
Primary:    [POR DETERMINAR — requiere validación controlada]
Fallback 1: [POR DETERMINAR — requiere validación controlada]
Fallback 2: ollama/qwen2.5-coder:14b        [LOCAL — solo PC grande]
```

> [!IMPORTANT]
> **No se puede definir el primary cloud hasta validar qué provider realmente responde.** El candidato más fuerte es `openai-codex/gpt-5.4` (proveedor nativo con evidencia de uso), pero requiere renovación de OAuth y prueba controlada.

---

## 5. Perfil máquina grande / casa (BORRADOR — pendiente validación)

| Campo | Valor | Estado |
|---|---|---|
| Primary | `openai-codex/gpt-5.4` *(candidato)* | Requiere validación |
| Fallback 1 | `google/gemini-2.5-flash` *(candidato)* | Requiere validación por key |
| Fallback 2 | `ollama/qwen2.5-coder:14b` (local) | ✅ Funcional |
| Nota | Ollama como safety net. APIs cloud como primarias. |

## 6. Perfil notebook vieja / 24-7 (BORRADOR — pendiente validación)

| Campo | Valor | Estado |
|---|---|---|
| Primary | `openai-codex/gpt-5.4` *(candidato)* | Requiere validación |
| Fallback 1 | `google/gemini-2.5-flash` *(candidato)* | Requiere validación |
| Fallback 2 | *(ninguno local)* | — |
| Nota | Sin Ollama. Solo APIs cloud. |

---

## 7. Decisiones pendientes para Diego

1. **¿OpenAI Codex como primary?** Es el proveedor nativo de OpenClaw con OAuth integrado. Evidencia de uso real previo. Limitación: cuota semanal con renovación y expiración de OAuth cada ~2 días.
2. **¿Gemini como fallback 1?** Hay keys, pero todas tienen historial de rate limit. Requiere validación individual antes de confiar.
3. **¿Limpiar las 6 keys duplicadas de Google?** O validar cuáles funcionan y quedarse solo con las buenas.
4. **¿Anthropic como alternativa?** 1 key disponible, sin historial de fallas pero sin evidencia de uso.
5. **¿Mantener Ollama solo en PC grande?** Propuesto como fallback final.
6. **¿Permisos operator.write desde el inicio?** ¿O arrancar solo con chat/razonamiento?
7. **¿Telegram habla con LucyClaw directa o puenteada por Doctora Lucy?**

---

## 8. Plan de migración propuesto (revisado)

> [!WARNING]
> **Antes de cualquier migración de routing, se debe ejecutar Tramo 12: Validación Controlada de Providers.**

### Fase 0 — Validación controlada (Tramo 12)
- Probar `openai-codex/gpt-5.4` con una llamada mínima.
- Probar `google/gemini-2.5-flash` con UNA key, sin ráfagas.
- Probar `anthropic` si se desea.
- Registrar cuál responde, cuál falla, con qué error.
- No hacer rotación automática hasta saber qué rota.

### Fase 1 — Backup (Tramo 12b)
```bash
mkdir -p ~/.openclaw/backups-tramo12
cp ~/.openclaw/openclaw.json ~/.openclaw/backups-tramo12/openclaw.json.pre-migration.bak
cp ~/.openclaw/agents/main/agent/auth-profiles.json ~/.openclaw/backups-tramo12/auth-profiles.json.pre-migration.bak
cp ~/.openclaw/agents/main/agent/models.json ~/.openclaw/backups-tramo12/models.json.pre-migration.bak
```

### Fase 2 — Cambiar routing (solo después de validación exitosa)
```bash
# Cambiar primary al provider validado
openclaw models set [PROVIDER_VALIDADO]

# Limpiar fallbacks actuales
openclaw models fallbacks clear

# Agregar fallbacks en orden API-first
openclaw models fallbacks add [SEGUNDO_PROVIDER_VALIDADO]
openclaw models fallbacks add ollama/qwen2.5-coder:14b
```

### Fase 3-5 — Validar gateway, Telegram, exoesqueleto
(Sin cambios respecto al plan anterior)

---

## 9. Herramientas CLI disponibles para la migración

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

## 10. No hacer todavía

- No poner Gemini primary hasta ver una respuesta real estable.
- No confiar en "6 keys rotativas" sin validación individual.
- No tocar tokens ni scopes (tramo separado).
- No cambiar providers sin backup previo.
- No ejecutar `operator.write`.
- No mover config a notebook hasta validar en máquina grande.
- No eliminar fallback local hasta tener API estable.
- No hacer rotación automática hasta saber qué rota.
- No reiniciar gateway hasta aplicar cambios.

---

## 11. Corrección de supuestos — Tramo 11.5

### Keys Gemini: no son automáticamente confiables

- Las 6 keys/perfiles de Google fueron creadas en intentos previos de Lucy.
- **Todas** tienen `failure[rate_limit]` registrado en `auth-profiles.json → usageStats`.
- Diego reporta: cuotas agotadas sin uso claro, rotación que no resolvía límites, posible duplicación de cuentas, comportamiento inestable.
- Los modelos registrados en `models.json` usan nombres artificiales (`gemini-2.0-flash-2`, `gemini-2.0-flash-3`, etc.) que parecen clones del mismo modelo renombrados para simular rotación.
- No hay evidencia de que la rotación multi-key haya funcionado de forma estable.

### Antes de elegir Gemini como primary hay que validar:
1. Si cada key responde individualmente.
2. Si son keys de cuentas/proyectos distintos o la misma key duplicada.
3. Si la cuota de cada una está realmente disponible.
4. Si OpenClaw rota correctamente entre ellas.
5. Si el error de cuota persiste con una sola key sin ráfagas.

### OpenClaw tiene proveedor nativo (OpenAI Codex)
- El sistema **no requiere obligatoriamente keys personales de Diego** para funcionar.
- OpenAI Codex via OAuth es el mecanismo integrado.
- El login OAuth vincula la cuenta ChatGPT de Diego directamente.
- Tiene cuota semanal renovable (actualmente 96% disponible).
- Es el único provider con evidencia de uso real exitoso en sesiones históricas.

---

## 12. Plan de validación antes de migrar routing

### Paso 1 — Validar proveedor nativo (OpenAI Codex)
- Verificar que OAuth sigue activo: `openclaw models status`.
- Si expiró: renovar con `openclaw models auth login` (requiere TTY).
- Hacer UNA llamada mínima para confirmar respuesta.
- Registrar resultado.

### Paso 2 — Validar Gemini con UNA sola key
- Usar `google:default` (la key principal).
- Hacer UNA llamada mínima, sin ráfagas.
- Si falla con rate limit, registrar y NO probar más keys aún.
- Si funciona, probar una segunda key para comparar.

### Paso 3 — Validar OpenAI personal (si se desea)
- Usar la key `sk-proj-...` con una llamada mínima.
- Registrar resultado.

### Paso 4 — Validar Anthropic (si se desea)
- Usar la key `sk...ey` con una llamada mínima.
- Registrar resultado.

### Paso 5 — Decidir routing basado en evidencia
- Solo después de validación, definir primary y fallbacks.
- No asumir que un provider funciona solo porque existe una key.

---

## 13. Riesgos identificados (revisados)

| Riesgo | Severidad | Mitigación |
|---|---|---|
| Keys Gemini con rate limit previo | 🟡 Media | Validar individualmente antes de confiar |
| OAuth Codex expira en 2 días | 🟡 Media | Renovar antes de expiración |
| "6 keys rotativas" pueden ser la misma cuenta | 🔴 Alta | Verificar hashes de keys — si son distintas |
| Service Token gateway sigue en 401 | 🟡 Media | Tramo separado; no bloquea validación de providers |
| Rollback | 🟢 Baja | Backup pre-migración permite restaurar con `cp` |
| Modelos renombrados artificialmente | 🟡 Media | Los `gemini-2.0-flash-N` en models.json parecen clones; validar si OpenClaw los reconoce como un solo modelo real |
