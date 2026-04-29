# OpenClaw / LucyClaw — Plan de rebuild controlado

## 1. Motivo

La recuperación del sistema de autorización del gateway de OpenClaw ha fallado de forma persistente tras agotar todas las vías de reparación disponibles (sincronización de tokens, parches manuales de identidad y reparación forzada `doctor --force`). El error `403 missing scope: operator.read` persiste a pesar de contar con tokens que declaran dichos scopes, indicando una corrupción estructural en el store interno de permisos que no es accesible mediante edición de JSONs ni herramientas oficiales de CLI.

## 2. Qué se debe conservar

Para garantizar la continuidad de la conciencia de Doctor-Lucy y sus capacidades, se debe asegurar el acceso a:
* **Backup total FORCE-GATE**: Localizado en `/home/lucy-ubuntu/OpenClaw_Backups/force_gate/20260429_125405`. Es el "seguro de vida" del sistema actual.
* **`auth-profiles.json`**: Contiene las API keys y perfiles de providers (Google, Anthropic, etc.).
* **`models.json`**: Contiene la definición de modelos y providers configurados.
* **Providers/Modelos**: La configuración que ya sabemos que funciona (Gemini cloud y Ollama local).
* **Documentación del repo**: Todos los archivos en `docs/` que registran el progreso arquitectónico.
* **Scripts Doctor-Lucy**: Los scripts locales de integración y automatización.
* **Memoria/n8n**: Toda la infraestructura externa a OpenClaw que reside en `n8n_data`.

## 3. Qué NO migrar a ciegas

Para evitar importar el problema de autorización a la nueva instalación, se deben descartar o auditar estrictamente:
* **`gateway.auth`**: La configuración de autenticación del gateway en `openclaw.json`.
* **`lucy-bridge-token`**: El archivo de token sospechoso de carecer de scopes válidos.
* **`identity/device-auth.json`**: El store de identidad del dispositivo que parece estar "anclado" a un estado sin permisos.
* **`devices/paired.json`**: La lista de dispositivos emparejados.
* **Caches de Dashboard**: Evitar arrastrar cookies o sesiones de la UI anterior.

## 4. Perfil objetivo

El nuevo despliegue debe adherirse a la visión establecida en [LUCYCLAW_ARCHITECTURE.md](file:///home/lucy-ubuntu/Escritorio/doctor%20de%20lucy/docs/LUCYCLAW_ARCHITECTURE.md):
* **Dual-host / API-first**: Capacidad de operar en PC grande y Notebook.
* **Codex/OpenAI como Primary**: Es el objetivo final para maximizar la integración nativa.
* **Gemini como Fallback Cloud**: Ya validado y funcional.
* **Ollama como Fallback Local**: Para procesamiento pesado offline en PC grande.

## 5. Fases propuestas

1. **Snapshot total**: Confirmar que el backup de Force-Gate es íntegro (Ya realizado ✅).
2. **Instalación limpia**: Desplegar OpenClaw en un directorio o perfil de usuario paralelo para no interferir con la instancia actual.
3. **Verificación básica**: Validar `/health` en la nueva instancia.
4. **Generación de token**: Crear un Service Token limpio mediante el primer arranque y verificar que `/v1/models` responde con 200 de forma nativa.
5. **Validación Codex OAuth**: Realizar el login de Codex en la instancia limpia.
6. **Migración selectiva**: Importar `auth-profiles.json` y `models.json` desde el backup.
7. **Integración de Bridge**: Reconfigurar `lucy_openclaw_bridge.py` para apuntar a la nueva instancia.
8. **Pruebas de estrés**: Validar la cadena de providers (Codex -> Gemini -> Ollama).
9. **Despliegue final**: Migrar el daemon v2 y Telegram a la nueva instancia.

## 6. Rollback

La instancia actual en `~/.openclaw` se mantendrá intacta (renombrada o mediante aislamiento de perfil) hasta que la nueva instalación demuestre 100% de operatividad en `/v1/models` y Codex OAuth.

## 7. Decisiones pendientes

* **Notebook vieja**: Evaluar si la reinstalación se realiza directamente en el entorno de la notebook para simplificar la migración API-first.
* **OAuth Codex**: Decidir si se intenta conservar la sesión actual o si se realiza un relogueo limpio.
