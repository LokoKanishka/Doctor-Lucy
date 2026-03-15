# Lucy Music Brain - Bootstrap

## ¿Qué hace esta fase?
Este es el primer paso ("bootstrap") para construir el proyecto **Memoria Musical de Diego / Lucy Music Brain**. Su meta es auditar el acceso a la cuenta de Spotify, recolectar en crudo toda la historia musical posible, y preparar una persistencia local reutilizable mediante JSON y SQLite.

## Datos que extrae de Spotify
- **Artistas Seguidos** (`followed_artists`)
- **Playlists** públicas, privadas y colaborativas (`playlists`)
- **Canciones Guardadas** ("Me Gusta") (`saved_tracks`)
- **Álbumes Guardados** (`saved_albums`)
- **Top Artistas** (Corto, mediano y largo plazo) (`top_artists_*`)
- **Top Canciones** (Corto, mediano y largo plazo) (`top_tracks_*`)
- **Recién Escuchados** (`recently_played`)

## Scopes Necesarios (Permisos)
El script audita el refresh token de Spotify actual. Para funcionar completamente necesita estos recortes:
* `user-follow-read`
* `user-library-read`
* `playlist-read-private`
* `playlist-read-collaborative`
* `user-top-read`
* `user-read-recently-played`
* `user-read-playback-state`
* `user-read-currently-playing`

## Archivos Generados
- `data/music_brain/raw/`: Snapshots JSON crudos directamente desde los endpoints de Spotify (`raw_*.json`).
- `data/music_brain/music_brain.sqlite`: Esqueleto local SQLite para estructurar persistencia (Tablas `artists_raw`, `playlists_raw`, `tracks_raw`, etc.) y seguimiento de errores/auditorías (`audit_runs`, `audit_errors`).
- `data/music_brain/artist_inventory.json`: Un índice de todos los artistas musicales únicos encontrados y la fuente de dónde provinieron.
- `data/music_brain/bootstrap_summary.json`: Reporte del éxito, limitaciones, o scopes faltantes encontrados.

## Limitaciones y Re-Ejecución
Esto es **solamente** una auditoría bruta. No representa todavía relaciones enriquecidas de la base final, no conecta con n8n ni usa bases remotas todavía.

Si al correr el script `scripts/spotify_music_audit.py` falla la mayoría de los endpoints por un `403 Forbidden ("Insufficient client scope")`, debes ir a tu portal de desarrollador de Spotify, generar una nueva URL de autorización solicitando estrictamente la lista de permisos en el `.env.example`, y reemplazar el `SPOTIFY_REFRESH_TOKEN` de acceso con el nuevo token obtenido.

**¿Faltaron Scopes?**
Sí, probablemente falte todo lo referente a datos del histórico musical (sólo tenías control de reproducción `user-modify-playback-state` y `user-read-playback-state`). ¡Sigue las instrucciones de reautorización y vuelve a ejecutar el script!
