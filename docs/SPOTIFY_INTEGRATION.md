# Integración Spotify v1 para Doctor-Lucy

Esta integración permite a Doctor-Lucy controlar de manera básica la reproducción musical en la cuenta de Spotify del usuario. 
Está diseñada como una periferia opcional, sin dependencias complejas (usa sólo la librería estándar de Python) y aislada del núcleo clínico de Lucy.

> **Importante**: Requiere una cuenta de **Spotify Premium** para controlar la reproducción activa y dispositivos.

## 1. Variables de Entorno (`.env`)

Para que la integración funcione, debes configurar las siguientes variables en tu archivo `.env`:

```env
SPOTIFY_CLIENT_ID=tu_client_id_aqui
SPOTIFY_CLIENT_SECRET=tu_client_secret_aqui
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
SPOTIFY_REFRESH_TOKEN=tu_refresh_token_aqui
```

Los tres primeros (`CLIENT_ID`, `CLIENT_SECRET` y el `REDIRECT_URI` configurado a `http://127.0.0.1:8888/callback`) se obtienen creando una aplicación desde el [Spotify for Developers Dashboard](https://developer.spotify.com/dashboard).

## 2. Obtener el `SPOTIFY_REFRESH_TOKEN` (Bootstrap OAuth)

Si aún no tienes un `SPOTIFY_REFRESH_TOKEN`, puedes usar el propio script para generarlo a través de un flujo OAuth local:

1. Asegúrate de tener al menos `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` y `SPOTIFY_REDIRECT_URI` en tu archivo `.env`.
2. Ejecuta el comando de autorización:
   ```bash
   python3 scripts/spotify_cli.py auth
   ```
3. Sigue las instrucciones en la terminal:
   - Abre la URL generada en tu navegador.
   - Concede permisos a tu aplicación ("Aceptar").
   - El script levantará un servidor local temporal (`http://127.0.0.1:8888`) que atrapará el callback de Spotify.
   - El script imprimirá en la terminal el valor final de tu `SPOTIFY_REFRESH_TOKEN`.
4. Copia ese valor y añádelo en tu archivo `.env`. ¡Listo!

## 3. Comandos Disponibles

Todos los comandos se ejecutan a través de `scripts/spotify_cli.py`:

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `auth` | Inicia el flujo OAuth para obtener tokens | `python3 scripts/spotify_cli.py auth` |
| `status` | Muestra estado de la reproducción actual | `python3 scripts/spotify_cli.py status` |
| `devices` | Lista los dispositivos activos en Spotify | `python3 scripts/spotify_cli.py devices` |
| `play` | Reanuda la reproducción pausada | `python3 scripts/spotify_cli.py play` |
| `pause` | Pausa la reproducción actual | `python3 scripts/spotify_cli.py pause` |
| `next` | Salta a la siguiente pista | `python3 scripts/spotify_cli.py next` |
| `previous` | Vuelve a la pista anterior | `python3 scripts/spotify_cli.py previous` |
| `volume` | Fija el nivel de volumen (0-100) | `python3 scripts/spotify_cli.py volume 50` |
| `play_uri`| Reproduce una URI específica de Spotify | `python3 scripts/spotify_cli.py play_uri spotify:track:xxx` |
