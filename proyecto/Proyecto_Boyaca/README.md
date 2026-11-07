# Proyecto final Boyacá · Big Data

## Integrantes

- José Luis Gachagoque Sánchez
- Leibnitz Edison Andrés Rojas Castillo
- Juan Sebastián Sánchez López
- Deiver Torres Mariño
- Daniel Viasus Fuentes
- Stefany Pinto

## Informe y resultados

https://fmcalistenico.github.io/big-data-postgraduate/

## Guía de ejecución 1: todo el pipeline con un comando

Desde la carpeta Proyecto_Boyaca:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    bash run_pipeline.sh
    python -m src.publicar_sitio

run_pipeline.sh ejecuta los notebooks 01 a 08 en orden y luego las pruebas (26).
publicar_sitio genera la página de resultados en site/.

## Guía de ejecución 2: notebook por notebook

Abrir JupyterLab desde Proyecto_Boyaca (jupyter lab) y ejecutar en orden los notebooks
01 a 08 de la carpeta notebooks/, con Kernel -> Restart Kernel and Run All Cells.

## Estructura

    Proyecto_Boyaca/
    ├── staging/              # los 6 archivos originales
    ├── data_lake/
    │   ├── bronze/<fuente>/  # CSV sin modificar (GeoJSON -> CSV con WKT) + manifest.json
    │   ├── silver/           # Parquet / GeoParquet validados
    │   ├── gold/             # tablas analíticas
    │   └── rejects/          # filas rechazadas con su motivo
    ├── src/                  # toda la lógica del pipeline
    ├── notebooks/            # 01 … 08: llaman a src/ en orden
    ├── tests/                # pruebas con pytest
    ├── outputs/              # calidad, estadística, figuras y mapas
    ├── site/                 # página de resultados (GitHub Pages)
    ├── requirements.txt
    └── run_pipeline.sh
