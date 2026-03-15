# Music Brain Local Query Layer

## Propósito
Esta capa provee un mecanismo rápido, local y sin dependencias externas (sin API calls, sin vectores/embeddings, sin RAG) para consultar y analizar el núcleo del perfil musical. Lee directamente de los artefactos curados (`core_profile_report.json`), consolidando y resumiendo la información para que Lucy (o el usuario) pueda extraer respuestas concretas en tiempo real.

## Fuentes de Datos
El script lee la información pre-computada desde `data/music_brain/core_profile_report.json`. Esta fuente es óptima para consultas de lectura locales en Python ya que contiene la información taxonómica y demográfica pre-consolidada y cacheada.

## Limitaciones Actuales
- **Alcance Base**: Solo considera los artistas que forman parte de la clase `core` (el núcleo consolidado del perfil).
- **IA/Semántica**: No cuenta con entendimiento semántico fluido ni embeddings; las búsquedas funcionan basándose en "fuzzy matching" determinista (coincidencias de strings ignorando mayúsculas y espacios). 
- **Tiempo Real**: No desencadena nuevas búsquedas en Last.fm o Discogs. Si algo no está en el reporte, no existirá para esta capa de consulta.

## Subcomandos Disponibles

El CLI soporta múltiples niveles de agregación o búsqueda individual.

### Resúmenes Globales
```bash
python3 scripts/music_brain_query.py summary
python3 scripts/music_brain_query.py top-genres
python3 scripts/music_brain_query.py top-subgenres
python3 scripts/music_brain_query.py top-scenes
python3 scripts/music_brain_query.py top-countries
python3 scripts/music_brain_query.py top-decades
python3 scripts/music_brain_query.py top-artists
```

### Consultas de Entidad Específica
```bash
# Búsqueda difusa de artista (ej. "Pink Floyd")
python3 scripts/music_brain_query.py artist "pink floyd"

# Buscar qué artistas pertenecen a un género o escena
python3 scripts/music_brain_query.py genre "trip-hop"
python3 scripts/music_brain_query.py scene "madchester"

# Filtrar por país o década
python3 scripts/music_brain_query.py country "argentina"
python3 scripts/music_brain_query.py decade "1990s"
```

### Comparación Simple
Calcula el "peso total" (score consolidado) de los artistas que hacen match con los ejes indicados.
```bash
python3 scripts/music_brain_query.py compare "rock" "electronic"
python3 scripts/music_brain_query.py compare "uk" "usa"
```
