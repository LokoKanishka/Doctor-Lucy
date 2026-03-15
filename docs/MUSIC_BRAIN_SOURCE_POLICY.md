# Music Brain Source Policy & Health

## Propósito
Esta capa de política y métricas de salud existe para controlar estrictamente de dónde obtiene información el Music Brain. Su objetivo principal es evitar que Lucy intente utilizar fuentes ineficaces o inapropiadas para ciertas tareas, basándose en la experiencia previa. Una capa explícita garantiza que estas decisiones sean auditables, persistentes y ejecutables por los scripts.

## Diferencia entre Policy y Source Health
- **Source Policy (`source_policies.json`)**: Reglas estáticas y deterministas creadas por diseño. Define qué fuente (`source_name`) está permitida (`allowed`: true/false) para un tipo de entidad (`entity_type`) y tarea específica (`job_type`).
- **Source Health (`source_health.json`)**: Estado operacional dinámico. Rastrea el éxito y fracaso histórico de una fuente para una tarea. Si una fuente falla repetidamente, su `status` se degrada o deshabilita, impidiendo transitoriamente su uso aunque la política lo permita.

## Caso Discogs
Discogs ha sido **deshabilitado** intencionalmente para la tarea de enriquecimiento básico de artistas (`artist_enrichment_basic`). 
**Razón:** A nivel de *artist* en su API, Discogs no devuelve estilos musicales útiles de forma consistente (generalmente devuelve un array vacío). Los estilos y géneros en Discogs se acoplan fuertemente a las entidades *release* (lanzamientos) o *master* (álbumes principales). Por lo tanto, intentar enriquecer perfiles de artistas consultando Discogs genera llamadas inútiles y consume rate limits sin aportar valor. Discogs queda reservado como candidato para futuras fases de `release_master_enrichment`.

## Permisos Actuales
- **MusicBrainz**: Permitido y saludable para `artist_enrichment_basic`.
- **Wikipedia**: Permitido y saludable para `artist_enrichment_basic`.
- **Last.fm**: Permitido y saludable para `artist_enrichment_basic`, `artist_similarity`, y `artist_tags`.
- **Discogs**: Denegado para `artist_enrichment_basic`. Permitido para `release_master_enrichment` (entidades `release` y `master`).

## Cómo reactivar una fuente en el futuro
Si Discogs (u otra fuente denegada/fallida) cambia su API o se vuelve relevante para una tarea previamente bloqueada, se debe:
1. Actualizar `data/music_brain/source_policies.json` cambiando `allowed: false` a `allowed: true`.
2. Opcionalmente usar el script CLI o modificar SQLite `source_policies` para reflejar el cambio.
3. Actualizar el estado de salud en `source_health.json` pasándolo de `disabled` a `healthy`.

## Uso del Script CLI
El script principal para interactuar con esta capa es `scripts/music_brain_source_policy.py`.

```bash
# Mostrar todas las políticas estáticas actuales
python3 scripts/music_brain_source_policy.py show

# Comprobar si Discogs puede usarse para un job de artista (esperado: DENIED)
python3 scripts/music_brain_source_policy.py check discogs artist artist_enrichment_basic

# Comprobar si Last.fm puede usarse para un job de artista (esperado: ALLOWED)
python3 scripts/music_brain_source_policy.py check lastfm artist artist_enrichment_basic

# Mostrar el estado de salud de todas las fuentes
python3 scripts/music_brain_source_policy.py health
```
