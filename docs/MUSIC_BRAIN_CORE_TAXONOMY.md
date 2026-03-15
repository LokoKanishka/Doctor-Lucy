# Lucy Music Brain - Taxonomía Semántica Core (Fase 3B)

## ¿Qué resuelve esta fase?
La Fase 3A nos dejó semántica cruda: tags en inglés sin normalizar, países como código ISO, décadas sin extraer. Esta fase convierte esa semántica en una **ontología musical usable**: géneros canónicos, subgéneros, países en español, décadas, y un "perfil musical de Diego" que Lucy puede interpretar y verbalizar.

## Enriquecimiento bruto vs Taxonomía consolidada

| Enriquecimiento bruto (3A) | Taxonomía consolidada (3B) |
|---|---|
| `"tags": ["trip-hop", "triphop", "trip rock"]` | `"canonical_genres": ["Electronic"]`, `"canonical_subgenres": ["Trip-Hop"]` |
| `"country": "GB"` | `"country_name": "Reino Unido"` |
| Wikipedia sin procesar | `"decades": ["1980s", "1990s"]` |

## Reglas de normalización de géneros/tags
El script usa un mapa de ~100+ reglas explícitas (`GENRE_MAP`) donde cada tag crudo se traduce a un par `(género canónico, subgénero canónico)`. Ejemplos clave:

- `"triphop"` → `(Electronic, Trip-Hop)`
- `"progressive rock"` / `"prog rock"` → `(Rock, Progressive Rock)`
- `"darkwave"` / `"gothic rock"` → `(Rock, Gothic / Darkwave)`
- `"film score"` / `"soundtrack"` → `(Classical / Cinematic, OST / Soundtrack)`
- `"griot"` / `"kora"` → `(World, Griots / Kora)`

### Géneros canónicos resultantes
`Rock`, `Pop`, `Electronic`, `Blues`, `Jazz`, `Metal`, `Rap / Hip-Hop`, `Classical / Cinematic`, `Folk / Acoustic`, `Ambient / Drone`, `Reggae / Dub`, `World`, `Soul / R&B`, `Traditional / Rioplatense`, `Experimental`

## Archivos generados
- `data/music_brain/core_taxonomy.json`: taxonomía por artista. 403 items con géneros, subgéneros, country_name, décadas, confianza.
- `data/music_brain/core_profile_report.json`: perfil musical agregado de Diego — top géneros, subgéneros, países, décadas, emblemáticos por género, observaciones automáticas.
- `music_brain.sqlite`: tablas `artist_taxonomy`, `canonical_tags`, `taxonomy_runs`.

## Limitaciones
- Las décadas se extraen del texto de Wikipedia con búsqueda de año numérico — es heurístico y puede sobre-generar ("1980" aparece en una bio no musical).
- Los artistas sin Wikipedia (parciales de Fase 3A) no tienen decades ni escenas.
- Los artistas locales menos conocidos (Uruguay, Argentina underground) tienen menor cobertura de tags.

## Qué prepara para la siguiente fase
Con la ontología en su lugar, el siguiente paso natural es enriquecer a los artistas **Recurrent** (1440 artistas) usando el mismo pipeline, y eventualmente conectar todo esto a un LLM (via n8n o Ollama local) para que Lucy pueda razonar sobre el grafo musical de Diego de forma semántica.
