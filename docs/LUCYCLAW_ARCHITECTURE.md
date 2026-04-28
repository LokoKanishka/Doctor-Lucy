# LucyClaw — Arquitectura dual-host / API-first

## 1. Nombres correctos
- **Doctora Lucy**: La entidad central/cerebro en la máquina grande. Supervisa hardware, n8n, voz y memoria local.
- **OpenClaw**: La capa técnica, plataforma y gateway que permite la ejecución de agentes y puentes (Telegram/API).
- **LucyClaw**: La personalidad/agente Lucy dentro de OpenClaw. Es la encarnación cloud/API de Doctora Lucy.
- **Aclaración**: Si aparece “OpenCloud” en transcripciones por error, debe interpretarse siempre como OpenClaw/LucyClaw.

## 2. Problema que se quiere resolver
La configuración previa tendía a priorizar modelos locales pesados (Ollama/Local-GPU). Esto genera una dependencia obligatoria de la potencia de la máquina grande, contradiciendo el objetivo de portabilidad y disponibilidad 24/7 en hardware liviano (notebook vieja).

## 3. Objetivo de LucyClaw
LucyClaw debe ser:
- Extensión cloud/API de Doctora Lucy.
- Usable desde Telegram y delegable desde Antigravity.
- Liviana: debe poder correr en hardware restringido (notebook vieja).
- Potente: puede usar recursos locales si están disponibles, pero no debe depender de ellos.
- Portable y API-first.

## 4. Dos escenarios de uso

### Escenario A — Máquina grande / casa
Diego trabaja en la PC principal. Doctora Lucy es la interfaz primaria en Antigravity. Doctora Lucy puede delegar tareas a LucyClaw como un "brazo externo" cloud/API o para interacción vía Telegram.

### Escenario B — Notebook vieja / fuera de casa
La notebook funciona como servidor liviano 24/7. LucyClaw opera principalmente vía Telegram. Debe usar APIs cloud para razonamiento, manteniendo un consumo local mínimo de CPU/GPU.

## 5. Modos funcionales de LucyClaw

### Modo 1 — LucyClaw directa desde Telegram
Interacción directa Diego <-> LucyClaw. Uso de APIs cloud y herramientas de búsqueda/ejecución permitidas.

### Modo 2 — Exoesqueleto de Doctora Lucy
Doctora Lucy (Antigravity) delega en LucyClaw. LucyClaw procesa externamente y devuelve el resultado al cerebro central.

## 6. Restricciones de infraestructura
- Sin costos fijos de servidor (reutilizar lo disponible).
- Sin requisitos obligatorios de GPU/VRAM.
- Uso de APIs cloud como motor principal.
- Fallback local opcional solo si hay potencia disponible.

## 7. Antipatrón detectado (Errores a evitar)
- Configurar modelos locales pesados como default para el agente.
- Depender de la RTX 5090 para que el bot responda en Telegram.
- Mezclar lógicas de máquina grande con requisitos de notebook vieja sin distinción de perfiles.

## 8. Arquitectura deseada

**Flujo fuera de casa:**
Diego (Celular) -> Telegram -> LucyClaw (Gateway en notebook) -> Proveedor Cloud/API -> Respuesta.

**Flujo en casa:**
Diego (PC) -> Doctora Lucy (Antigravity) -> Bridge -> LucyClaw -> Proveedor Cloud/API (o local opcional) -> Respuesta.

## 9. Regla de providers
Prioridad:
1. Provider cloud/API principal (Gemini/OpenAI).
2. Provider cloud/API alternativo.
3. Modelo local (Fallback opcional, solo en PC grande).

## 10. Requisitos técnicos para el próximo tramo
Auditoría pendiente:
- Identificar providers configurados en `openclaw.json`.
- Detectar si el `main agent` depende de Ollama.
- Definir cómo desactivar `local-heavy` como default.
- Preparar perfiles diferenciados por host.

## 11. Decisiones pendientes para Diego
- Prioridad de proveedores API (¿Gemini primero, ChatGPT después?).
- Alcance de permisos iniciales (`operator.write` vs `chat-only`).
- Diferencias específicas de comportamiento entre perfiles.
