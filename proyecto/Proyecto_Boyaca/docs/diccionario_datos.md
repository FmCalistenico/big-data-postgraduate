# Inventario de fuentes y diccionario de datos

El esquema exacto (tipos y claves) vive en `src/contratos.py`; este documento lo explica.

## Inventario de fuentes

| Fuente (bronze) | Entidad | Unidad de observación | Vigencia | Filas | Notas |
|---|---|---|---|---|---|
| `evaluaciones_agropecuarias` | UPRA / MADR | municipio × cultivo × periodo × estado físico | 2023 (2023A, 2023B, 2023) | 2.613 | 96 cultivos, 6 estados físicos |
| `centros_poblados` | Gobernación de Boyacá, con base en DANE | municipio × año × área | 2020–2024 | 1.845 | Edad simple 0–85+ por sexo; áreas Cabecera / Rural / Total |
| `desempeno_municipal` | DNP | municipio | 2020 | 246 | Dos bloques de 123; códigos 15022/15047 cruzados en el bloque A |
| `poblacion_dane` | DANE (recorte del curso) | municipio × año | 2020–2025 | 738 | Fuente municipal oficial; proyecciones, no conteos |
| `municipios_mgn` | DANE MGN 2025 | municipio | 2025 | 123 | Geometría simplificada 75 m; `area_km2` oficial |
| `capacidad_uso_igac` | IGAC | polígono | 2004 | 958 | Escala 1:100.000; sin CRS declarado (se asume EPSG:4326) |

Fecha de descarga, hash, tamaño y codificación de cada una: `data_lake/bronze/<fuente>/manifest.json`.

## Convenciones

- `codigo_municipio`: texto de 5 dígitos DIVIPOLA ("15001"), clave de integración.
- Unidades en el nombre: `_ha` hectáreas, `_t` toneladas, `_km2` kilómetros cuadrados, `_pct` porcentaje (0–100).
- null = dato no disponible. 0 = valor observado igual a cero.

## Silver

### `silver/poblacion.parquet` (P1) · clave: codigo_municipio + anio

| Columna | Tipo | Descripción |
|---|---|---|
| codigo_municipio | texto | DIVIPOLA de 5 dígitos |
| municipio | texto | Nombre oficial DANE |
| anio | entero | 2020–2025 |
| poblacion_total, hombres, mujeres | entero | Personas (proyección DANE, área Total) |
| pob_18_44, pob_18_64 | entero | Personas en esos rangos de edad, extremos incluidos |
| hombres_18_44, mujeres_18_44 | entero | Personas de 18 a 44 por sexo |

### `silver/poblacion_area.parquet` (P1) · clave: codigo_municipio + anio + area + sexo + edad

| Columna | Tipo | Descripción |
|---|---|---|
| area | texto | `cabecera` o `rural`; la fila Total se descarta para no duplicar |
| sexo | texto | H / M |
| edad | entero | 0–85 (85 = 85 y más) |
| personas | entero | Personas |

### `silver/desempeno.parquet` (P1) · clave: codigo_municipio + anio + bloque

| Columna | Tipo | Descripción |
|---|---|---|
| municipio_fuente | texto | Nombre tal como viene en el MDM |
| bloque | texto | A (filas 1–123) o B (124–246) |
| es_bloque_oficial | booleano | Bloque usado en el análisis principal (`config.MDM_BLOQUE_OFICIAL`) |
| nombre_coherente | booleano | El nombre corresponde al código DANE (sin tildes) |
| grupo_capacidad | texto | Grupo de capacidades iniciales del DNP (G1–G6) |
| movilizacion_recursos … seguridad_convivencia | decimal | Componentes de gestión y resultados (0–100) |
| gestion, resultados | decimal | Subtotales (0–100) |
| ajuste_resultados | decimal | Factor de ajuste por resultados (~1) |
| puntaje_mdm | decimal | Puntaje MDM (0–100) |

### `silver/agricola.parquet` (P2) · clave: codigo_municipio + codigo_cultivo + periodo + estado_fisico

| Columna | Tipo | Descripción |
|---|---|---|
| anio, periodo | entero, texto | 2023; periodo 2023A, 2023B o 2023 (anual, para permanentes) |
| ciclo | texto | Transitorio o permanente |
| cultivo, codigo_cultivo, desagregacion_cultivo, grupo_cultivo | texto | Identificación del cultivo |
| estado_fisico | texto | En fresco, grano seco, pergamino… |
| area_sembrada_ha, area_cosechada_ha | decimal | ha |
| produccion_t | decimal | t |
| rendimiento_fuente_t_ha | decimal | t/ha reportado por la fuente (solo para contrastar) |
| alerta_cosechada_mayor | booleano | Área cosechada > sembrada |
| alerta_produccion_sin_area | booleano | Producción > 0 con área cosechada 0 |

### `silver/municipios.geoparquet` (P3) · clave: codigo_municipio

`municipio`, `area_km2` (oficial), `area_simplificada_km2` (de la geometría de 75 m), `geometry` (EPSG:4326).

### `silver/capacidad_uso.geoparquet` (P4) · clave: polígono

`objectid`, `ucs_cp`, `clase` (III–VIII, ZU, CA), `subclase`, `grupo_manejo`, `ucs`, textos descriptivos del IGAC, `area_ha` (calculada en EPSG:9377), `geometry` (EPSG:4326).

## Gold

### `gold/cultivo_municipio.parquet` (P2) · clave: codigo_municipio + anio + cultivo + estado_fisico

`produccion_t`, `area_sembrada_ha`, `area_cosechada_ha` (suma de periodos) y `rendimiento_t_ha` = Σ producción / Σ área cosechada (null si el área es 0).

### `gold/suelo_municipio.parquet` (P4) · clave: codigo_municipio + clase

`area_ha` de la clase dentro del municipio; `pct_area` = área de la clase / área del municipio cubierta por la capa × 100.

### `gold/suelo_resumen.parquet` (P4) · clave: codigo_municipio

`area_municipio_ha`, `area_clasificada_ha`, `pct_sin_clasificar`, `clase_predominante` (solo clases agrológicas), `pct_clase_predominante`, `pct_clases_iii_iv`.

### `gold/municipio_anio.parquet` (P6) · clave: codigo_municipio + anio · 738 filas

| Columna | Fórmula / origen | Disponible en |
|---|---|---|
| prop_18_44_pct | pob_18_44 / poblacion_total × 100 | 2020–2025 |
| prop_18_64_pct | pob_18_64 / poblacion_total × 100 | 2020–2025 |
| prop_mujeres_18_44_pct, prop_hombres_18_44_pct | grupo / poblacion_total × 100 | 2020–2025 |
| pct_rural | personas rurales / total × 100 (fuente por áreas) | 2020–2024 |
| grupo_capacidad, puntaje_mdm | MDM, bloque oficial | 2020 |
| produccion_total_t | Σ toneladas de todos los cultivos (no comparable entre cultivos) | 2023 |
| produccion_papa_t, area_cosechada_papa_ha, rendimiento_papa_t_ha | Cultivo "Papa"; null si no hay registro | 2023 |
| produccion_1k_18_64 | produccion_total_t / pob_18_64 × 1.000 | 2023 |
| clase_predominante, pct_sin_clasificar, pct_clases_iii_iv | gold/suelo_resumen | Igual en todos los años |

### `gold/maestro_boyaca.geoparquet` (P6) · clave: codigo_municipio · 123 filas

Las variables de 2020 llevan el sufijo `_2020` y las de 2023 el sufijo `_2023`, más las de suelo y la `geometry`. Se usa para los mapas.

## Zonas de calidad

| Ruta | Contenido |
|---|---|
| `data_lake/rejects/<capa>_<fuente>.parquet` | Filas rechazadas con `motivo_rechazo` |
| `outputs/quality/metricas_<capa>.csv` | Una fila por regla: revisados, afectados, resultado, acción, fecha |
| `outputs/quality/diagnostico_<capa>_<fuente>.csv` | Perfil por columna antes (bronze) y después (silver) |
| `outputs/quality/no_vinculados_<fuente>.csv` | Claves que no cruzaron en cada unión |
| `outputs/quality/conciliacion_poblacion_fuentes.csv` | Diferencias entre las dos fuentes de población |
| `outputs/quality/desempeno_*.csv` | Nombres incoherentes y comparación entre bloques del MDM |
