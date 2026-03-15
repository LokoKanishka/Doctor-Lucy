# Lucy Music Brain - Normalización y Scoring (Fase 2)

## ¿Qué resuelve esta fase?
El **Bootstrap bruto** bajó miles de archivos JSON sueltos conteniendo apariciones literales de los endpoins de Spotify. Esta fase se encarga de unificar de manera inteligente esos miles de JSONs en perfiles consolidados por artista, agruparlos y dotarlos de un **Score de Relevancia** que clasifique qué artistas son importantes y cuáles son incidentales para la historia musical del usuario.

## Fórmula de Scoring
A cada artista se le asigna un puntaje base dependiendo de dónde fue encontrado, sumado a un "bonus de persistencia" (`cantidad_de_apariciones * 0.5`) que premia a los artistas que dominan los historiales.

**Pesos base por fuente:**
* `followed_artists` (Seguidos activamente) = **20 puntos**
* `top_artists_long` (Histórico a años vista) = **20 puntos**
* `top_tracks_long` (Temas quemados históricamente) = **15 puntos**
* `top_artists_medium` = **15 puntos**
* `saved_albums` (Discos guardados completos) = **15 puntos**
* `saved_tracks` (Corazones en temas sueltos) = **10 puntos**
* `top_tracks_medium` = **10 puntos**
* `top_artists_short` = **10 puntos**
* `top_tracks_short` = **5 puntos**
* `recently_played` = **5 puntos**
* `playlists` = **5 puntos**

## Clasificación Semántica
Dependiendo del puntaje final obtenido, el artista cae en uno de estos estratos:
- **Core (>= 50)**: Artistas fundamentales de la vida del usuario.
- **Recurrent (20 - 49)**: Artistas importantes o escuchados frecuentemente, músicos que gustan pero no definen fuertemente su núcleo total.
- **Satellite (5 - 19)**: Canciones guardadas sueltas o artistas ocasionales descubiertos en reproducciones recientes.
- **Incidental (< 5)**: Artistas de relleno que solo aparecieron perdidos en playlists.

## Archivos Generados
- `data/music_brain/artist_profiles.json`: Ficha completa por artista con conteo exacto de repeticiones en endpoints, puntajes y etiquetas funcionales.
- `data/music_brain/artist_rankings.json`: La misma información ordenada puramente por puntaje de Relevancia de mayor a menor.
- `data/music_brain/profile_summary.json`: Metadatos del estado sociológico de la cuenta, tamaño del núcleo vs periferia y observaciones simples por reglas.
- *`music_brain.sqlite`*: Actualización de la base, añadiendo campos de clase y conteos métricos por fuente en tablas como `artist_source_metrics` y `artist_profiles`.

## Limitaciones
- **Determinismo riguroso**: El score es 100% matemático y local. No posee todavía IA que entienda si un "Incidental" es un genio incomprendido o si merece subir de rango por parentesco de género con un "Core".
- Sin extracción de audios (RAG) o playlists tracks sueltas en este paso.

## Siguiente Fase
Con esta base perfilada matemáticamente, el siguiente paso (Fase 3 o "Music Agent") será enchufarle un modelo de LLM inteligente / n8n, capaz de razonar sobre este gran cerebro musical recién creado, armando constelaciones por géneros y preparando curadurías complejas hiper-personalizadas.
