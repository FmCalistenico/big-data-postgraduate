# Justificación de herramientas y de particionamiento

Responde la sección 9 del enunciado ("Justificación de la herramienta de procesamiento") y la sección 10.2 (particionamiento). Los campos marcados **[COMPLETAR]** se llenan después de ejecutar.

## 1. Herramienta de procesamiento elegida: Polars

| Criterio | Situación del proyecto | Implicación |
|---|---|---|
| Tamaño de los datos | Fuentes tabulares de 246 a 2.613 filas; población por edad ~ 210.000 filas en silver; capa de suelo de 958 polígonos. En disco: **[COMPLETAR con `du -sh data_lake/*`]** | Cabe en memoria muchas veces: no hace falta computación distribuida |
| Formato | CSV en bronze; Parquet y GeoParquet en silver y gold | Polars lee y escribe Parquet de forma nativa |
| Recursos | Portátiles personales, sin clúster | Spark agregaría Java, una JVM y una sesión local sin beneficio |
| Facilidad | Expresiones declarativas (`pl.col(...)`), tipos estrictos | Las reglas de calidad se escriben como expresiones reutilizables (`src/calidad.py`) |
| Tiempo y memoria observados | **[COMPLETAR: tiempo de `./run_pipeline.sh` y pico de memoria con `/usr/bin/time -v`]** | — |
| Compatibilidad | GeoPandas y statsmodels trabajan con pandas | Se convierte a pandas solo en esos dos puntos (`.to_pandas()`) |

**Para qué se usa cada biblioteca:**

| Biblioteca | Uso en el proyecto |
|---|---|
| Polars | Lectura de bronze, limpieza, reglas de calidad, agregaciones e integración |
| GeoPandas, Shapely, pyproj | Reconstrucción de WKT, reparación de geometrías, reproyección y overlay |
| pandas | Solo como puente hacia GeoPandas y statsmodels |
| SciPy, statsmodels | Correlaciones, IC, regresiones, diagnósticos y ajuste de Holm |
| Matplotlib, mapclassify | Gráficos y mapas, con cortes por cuantiles |
| pytest | Pruebas automatizadas |

### Alternativas consideradas

- **pandas solo.** Sería suficiente para este volumen. Se descartó como motor principal porque infiere tipos de forma silenciosa (por ejemplo, un código "15001" se vuelve entero y pierde el formato de 5 dígitos), y porque las reglas en Polars son expresiones que se pueden componer y probar.
- **Apache Spark (PySpark).** Su ventaja sería escalar a millones de filas o a un clúster. Su costo aquí es instalar Java y una combinación compatible de Spark y PySpark, y pagar el arranque de una sesión, para un volumen que no lo necesita. El enunciado aclara que Spark no da puntos por sí solo.

## 2. Particionamiento: no se particiona silver ni gold

| Criterio (sección 10.2) | Situación | Decisión |
|---|---|---|
| Volumen | La tabla más grande ronda las 210.000 filas y pocos MB | Un solo archivo se lee en milisegundos |
| Patrón de consulta | El análisis lee la tabla completa y filtra un año en memoria | Particionar no evita lecturas |
| Número y tamaño de archivos | Particionar por año daría 5–6 archivos de pocos KB por tabla | Problema de archivos pequeños: más metadatos que datos |
| Mantenimiento | Más rutas, más pruebas de que se leen todas las particiones | Costo sin beneficio |

**Cuándo sí convendría:** si se agregaran muchas vigencias del MDM y de la EVA, o todos los municipios del país, sería razonable particionar `silver/agricola` y `gold/municipio_anio` por `anio` y validar que la lectura recupere todas las particiones.

## 3. Versiones registradas

```text
[COMPLETAR con la salida de:]
python --version
pip freeze | grep -iE "polars|pandas|pyarrow|geopandas|shapely|pyproj|mapclassify|scipy|statsmodels|matplotlib|pytest"
```

Modo de ejecución: local, un solo proceso. Sistema: **[COMPLETAR: Ubuntu/WSL y versión]**.
