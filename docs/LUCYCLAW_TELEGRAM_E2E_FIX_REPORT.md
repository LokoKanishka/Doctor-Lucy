# Fix: Browser Routing for Telegram E2E (AG-TELEGRAM-E2E1-FIX)

## Diagnóstico
El fallo en la prueba **D (leer pestaña adjunta)** se debió a que el agente (vía Telegram) carecía de un contexto determinístico sobre la pestaña activa. Al no recibir información fresca sobre los targets disponibles, el modelo tendía a:
1. Alucinar que no había pestañas.
2. Usar identificadores antiguos (YouTube) de su memoria persistente.
3. Interpretar acciones de navegación/escritura en el contexto equivocado.

## Cambios Realizados

### 1. Script de Preflight Determinístico
Se creó `scripts/lucy_browser_preflight.py`. Este script:
- Lista las pestañas del perfil `chrome`.
- Identifica automáticamente la pestaña que contiene `127.0.0.1:8772/diagnostics/browser_telegram_e2e`.
- Realiza un `focus` y toma un `snapshot --interactive`.
- Devuelve el contexto (ID, URL, Título y Snapshot) en formato JSON.

### 2. Integración en el Puente (Bridge)
Se modificó `scripts/lucy_openclaw_bridge.py` para inyectar este contexto de forma automática:
- Si el mensaje de Diego contiene palabras clave como *pestaña, browser, navegador, chrome, panel, local, e2e, mirá, escribí, click*, el puente ejecuta el preflight.
- El resultado del snapshot se añade como contexto previo a la misión enviada al modelo.
- Esto garantiza que el modelo "vea" la página E2E local antes de decidir qué herramienta usar.

### 3. Actualización del Router
Se añadieron las palabras clave correspondientes a `scripts/lucy_machine_nl_router.py` para asegurar que el ruteo hacia el modelo sea invocado correctamente ante consultas de navegación.

## Próximos Pasos
1. Diego debe abrir/enfocar la página local y asegurar `Browser Relay: ON`.
2. Repetir prueba **D** desde Telegram.
3. Si **D** pasa, continuar con **E/F/G**.
