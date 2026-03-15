# Lucy Music Brain - Enriquecimiento Semántico Core (Fase 3A)

## ¿Qué resuelve esta fase?
La **Fase 2** nos dio una normalización local basada enteramente en eventos de Spotify, dándonos el qué (qué escuchas) y el cuánto (el volumen matemático), pero no el **quién** ni el **cómo**.
Esta Fase 3A implementa un motor de enriquecimiento para conectar nuestros artistas `core` con el ecosistema global de conocimiento musical, dándoles género, país de origen, síntesis biográfica y taxonomía canónica.

## ¿Por qué empezamos por los artistas Core?
Porque el volumen de la biblioteca total es gigante (3876 artistas). Si lanzáramos el motor contra todos simultáneamente:
1. Agotaríamos las cuotas libres de las APIs (MusicBrainz, Wikipedia).
2. Gastaríamos procesamiento en analizar la biografía profunda de una banda de cumbia que apareció por accidente en una playlist de asado de 2018 (los *Incidentales* o *Satélites*).

Nos concentramos exclusivamente en los **403 artistas estructurales ("Core")** ya identificados. Si los entendemos a ellos, entendemos el 80% del alma musical del usuario.

## Fuentes de Conocimiento (Knowledge Graph)
En esta versión inicial, el script consulta secuencialmente (con sleep para respetar cuotas públicas):
- **MusicBrainz (XML/JSON API)**: Se extraen Tags/Géneros precisos (filtrando ruido orgánico), País de Origen, Tipo de Artista y Códigos Universales (MBID), útiles para deduplicar o buscar en otras APIs.
- **Wikipedia (REST API extracts)**: Se obtiene la síntesis biográfica (Summary) canónica del artista para dar contexto cultural humano.

> **Nota Técnica sobre n8n y Fuentes Privadas:** El diseño soporta orquestación híbrida y persistencia relacional. APIs fundamentales como **Last.fm** (para extraer artistas similares - vital para recomendaciones) y **Discogs** (escenas profundas) requieren registro y una Key Privada obligatoriamente, por ende quedaron como placeholders a la espera de credenciales o de la intervención directa de un Workflow de n8n orquestado por el usuario.

## Rejilla de Consolidación
El script `scripts/music_brain_prepare_core_enrichment.py` maneja:
- **Descubrimiento Inteligente**: Maneja errores de timeout, no-hits, o variaciones de nombres.
- **SQLite Persistencia**: Anota si cada enriquecimiento fue OK, PARCIAL o FALLIDO en `artist_enrichment`, y guarda en `enrichment_errors` todo fallo para reintento futuro.
- **Archivos Estáticos Exportados**: 
  - `data/music_brain/core_artists_queue.json` (Cola de trabajo inmutable)
  - `data/music_brain/core_artists_enriched.json` (Resultados semánticos)
  - `data/music_brain/core_enrichment_summary.json` (Visión sintética de la corrida)

## Límites Actuales
1. Faltan los "Artistas Similares", que son la clave de cualquier motor de recomendación de grafos.
2. Las bandas menos mainstream en inglés a veces carecen de extracto de Wikipedia si sus nombres colisionan con palabras genéricas sin la etiqueta "banda".

## Siguiente Fase
Con esta matriz rica en conceptos biográficos y géneros, el Cerebro está listo para:
a) Levantar n8n e inyectar apikeys de Last.fm.
b) Pasar toda esta base relacional e indexada a **Memoria Vectorial / RAG**. Una vez integrado con los LLMs centrales de Doctora Lucy, el usuario podrá pedir *"Armame una lista que transicione del Trip Hop de Bristol de los 90s hacia bandas atmosféricas orientales, usando lo que ya me gusta"*.
