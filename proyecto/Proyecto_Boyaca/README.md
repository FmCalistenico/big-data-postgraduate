# Proyecto final Boyacá · Big Data

Pipeline reproducible bronze → silver → gold para los 123 municipios de Boyacá: población, producción agrícola, capacidad de uso de las tierras y desempeño municipal.

## Empiece aquí

- Ejecutar: docs/GUIA_EJECUCION.md
- Explicar cada parte: docs/GUIA_EXPLICACION.md
- Tablas y columnas: docs/diccionario_datos.md
- Herramientas y particionamiento: docs/justificacion_herramientas.md
- Informe: docs/informe_final.md
- Resultados publicados: carpeta site/ (GitHub Pages)

Ejecución:

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    bash run_pipeline.sh
    python -m src.publicar_sitio

## Estructura

    Proyecto_Boyaca/
    ├── staging/       los 6 archivos originales
    ├── data_lake/     bronze (CSV + manifiesto), silver y gold (Parquet), rejects
    ├── src/           toda la lógica
    ├── notebooks/     01 … 08, en orden
    ├── tests/         pytest
    ├── outputs/       calidad, estadística, figuras y mapas
    ├── site/          página de resultados (GitHub Pages)
    └── docs/          guías e informe

## Responsables

| Rol | Archivos |
|---|---|
| P1 Población y desempeño | silver_poblacion.py, silver_desempeno.py |
| P2 Producción agrícola | silver_agricola.py, gold_agricola.py |
| P3 Cartografía | geo.py, silver_municipios.py, mapas.py |
| P4 Suelo IGAC | silver_suelo.py, gold_suelo.py |
| P5 Estadística | estadistica.py, graficos.py |
| P6 Plataforma y calidad | config.py, calidad.py, contratos.py, mocks.py, ingesta_bronze.py, gold_integracion.py, publicar_sitio.py |

## Resultado principal

En 2020, la proporción de población de 18 a 44 años se asocia positivamente con el desempeño municipal: Spearman r = 0,24 (IC 95 % 0,06–0,40), p = 0,004, n = 123. La asociación es débil, se mantiene en los tres análisis de sensibilidad y no demuestra causalidad.

## Decisiones clave

- No hay un año común: la hipótesis principal usa 2020 (MDM) y las agrícolas 2023 (EVA).
- Población oficial: poblacion_dane; del archivo por áreas se usan cabecera y rural, nunca las tres filas.
- MDM: 246 filas en dos bloques; el oficial está en config.MDM_BLOQUE_OFICIAL.
- Suelo: clases III–VIII + ZU + CA; áreas en EPSG:9377.
- Faltante = null, nunca 0. Rendimiento = suma de producción / suma de área.
- Sin particionamiento.
