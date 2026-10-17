# Controles y guía del docente

Preparado por el PhD Esteban Hernández, CyberColombia.

Los controles siguientes corresponden únicamente al corte fechado suministrado. Si cambia una fuente, volver a ejecutar los scripts y publicar otra versión del manifiesto. El número de registros no se impone como condición universal de calidad; sirve para comprobar que todos trabajan con la misma entrada.

| Control | Referencia |
| --- | --- |
| AGROSAVIA entrada | 92.738 |
| Duplicados exactos | 0 |
| Aptos para analizar pH | 92.727 |
| Revisión por pH no numérico | 11 |
| Territorio sin enlace exacto | 2.138 |
| EVA entrada | 166.732 |
| EVA apto para cociente | 159.616 |
| Grupos agrícolas | 107.620 |
| Grupos agrícolas con pH | 55.498 |
| Intersecciones de muestras IGAC | 15 |

## Respuestas orientadoras

- Duplicado no equivale a repetición legítima: dos análisis de una misma localidad pueden corresponder a fechas o parcelas diferentes. Solo se eliminan copias definidas y documentadas.
- Una fila con ND en una propiedad puede servir para otra pregunta. El estado de calidad depende del producto, por ejemplo análisis de pH o rendimiento.
- Una unión muchos-a-uno conserva filas; una unión entre muestras individuales y registros agrícolas puede inflar conteos. Agregar a la unidad común antes de unir.
- La media simple de rendimientos asigna el mismo peso a áreas distintas. El cociente de sumas utiliza la superficie cosechada como ponderador dentro de grupos compatibles.
- Un mapa de cinco polígonos describe esos polígonos. El espacio no cubierto no equivale a suelo sin problemas, ni a ausencia del atributo.
- Las mediciones WoSIS por horizonte y los píxeles SoilGrids solo se comparan después de alinear profundidad, posición, método y soporte. El kit permite demostrar por qué esa validación requiere más datos.
- NASA y CHIRPS combinan fuentes y resoluciones diferentes. Comparar unidades y períodos es necesario, pero no garantiza igualdad.
- La última ventana de un flujo puede seguir abierta aunque no entren más archivos. Fin de archivos y fin de tiempo de evento son conceptos distintos.

## Contingencias durante la clase

| Situación | Acción |
| --- | --- |
| Portal DANE lento o 403 | Usar ZIP verificado del kit; mantener la descarga manual como procedimiento documentado. |
| Hash de descarga cambió | Conservar .nueva, comparar con el corte y no mezclar cohortes. |
| Pocos recursos de RAM | Dos hilos, un departamento y muestras; cerrar kernels y figuras que no se utilicen al ejecutar Spark. |
| Ceros en SoilGrids sin NoData | Reportar y separar provisionalmente; no inventar corrección. |
| Código no encontrado | Registrar anti-join y revisar vigencia/nombre con evidencia. |
| Java ausente | Instalar JDK 21 dentro de Ubuntu-26.04 según la guía WSL; comprobar antes de E07. |
| Streaming no muestra ventana final | Inspeccionar watermark y modo append; no fabricar observaciones. |

## Fuentes técnicas y metodológicas

DuckDB, lectura CSV y tipos

[Fuente](<https://duckdb.org/docs/stable/data/csv/overview>)

Apache Spark 4.0.1, instalación

[Fuente](<https://spark.apache.org/docs/4.0.1/api/python/getting_started/install.html>)

Apache Spark 4.0.1, Structured Streaming

[Fuente](<https://spark.apache.org/docs/4.0.1/streaming/apis-on-dataframes-and-datasets.html>)

GeoPandas, intersección vectorial

[Fuente](<https://geopandas.org/en/stable/docs/user_guide/set_operations.html>)

ISRIC, propiedades y factores de SoilGrids

[Fuente](<https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html>)

ISRIC, WoSIS y licencias

[Fuente](<https://docs.isric.org/globaldata/wosis/faq-wosis.html>)

NASA POWER, API diaria

[Fuente](<https://power.larc.nasa.gov/docs/services/api/temporal/daily/>)

CHIRPS v3

[Fuente](<https://chc.ucsb.edu/data/chirps3>)

UPRA, metodología EVA

[Fuente](<https://upra.gov.co/es-co/eva>)

Citar entidad, nombre exacto del conjunto, versión/corte, fecha de descarga y URL. DIVIPOLA y EVA declaran CC BY-SA 4.0 en los metadatos descargados; revisar los términos de cada capa adicional y la licencia por registro de WoSIS. La copia local preserva trazabilidad y disponibilidad para la cohorte.

## Controles PQRS y preparación docente

| Comprobación | Referencia |
| --- | --- |
| CSV completos | 716.697 + 781.601 + 946.468 = 2.444.766 |
| Columnas originales | 38 por archivo |
| Muestras | 3.000 filas en total |
| Proyección del taller | 16 columnas; originales intactos |
| Muestras: mayores de 90 | 41, conservadas |
| Muestras: ubicación peticionario vacía | 3, conservadas |
| Muestras: códigos de afectado sin DIVIPOLA | 186, requieren revisión |
| I01 NASA | 13 entregas; 1 duplicado y 1 tardío |

Los valores anteriores corresponden a entradas concretas y no son umbrales de calidad. Los notebooks 1 y 2 históricos contenían los mismos ejercicios; la ruta nueva elimina esa repetición. Los notebooks actuales distribuyen perfil, formatos, calidad y eventos con dependencias explícitas. Comprobar las dependencias y el kernel antes de la clase.

## Fuentes técnicas añadidas

[Fuente](<https://docs.pola.rs/user-guide/concepts/streaming/>)

[Fuente](<https://docs.pola.rs/api/python/stable/reference/api/polars.scan_parquet.html>)

Las presentes guías usan Polars 1.35.2 y DuckDB 1.4.1, probados en CPU. Las alternativas gestionadas, Zarr y Dask son material conceptual de ampliación. GPU dispone de una [instalación opcional independiente](polars-gpu.md), con prerrequisitos NVIDIA y CUDA; su ejecución debe validarse en hardware compatible y no es obligatoria para los talleres.

## Correcciones editoriales y curriculares

- Identidad institucional única del curso, autoría y fechas consistentes.
- Incorporación de tres cortes PQRS, muestras y sus advertencias de tamaño.
- Tiempos de talleres reconciliados con los doce encuentros y los recesos.
- Parquet de P02 disponible antes de consultar; calidad de suelos se introduce después de sus reglas.
- Métricas compuestas históricas se estudian en gobernanza y no como puntuaciones calculadas con campos inexistentes.
- Ejemplos acotados con observaciones abiertas y comparación equivalente de motores.
