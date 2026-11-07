# Guía de ejecución

Esta guía lleva el proyecto desde cero hasta las figuras y mapas. Siga los pasos en orden; la primera vez, lo que más demora es instalar las dependencias.

## 1. Requisitos

| Herramienta | Versión | Para qué |
|---|---|---|
| Ubuntu 22.04+ o WSL2 ([guía del curso](https://github.com/eshernan/big-data-course/blob/main/docs/instalacion-wsl.md)) | — | Sistema recomendado por el docente |
| Python | 3.10 a 3.12 | Todo el pipeline |
| Git | 2.30+ | Control de versiones |
| Espacio en disco | ~ 300 MB | Datos, entorno y salidas |

No se necesita Java ni Spark.

## 2. Preparar el entorno (una sola vez)

```bash
git clone <URL-del-repo-del-grupo> proyecto_boyaca
cd proyecto_boyaca
python3 -m venv .venv
source .venv/bin/activate          # en Windows sin WSL: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name boyaca --display-name "Python (boyaca)"
pip freeze > requirements-lock.txt # registra las versiones exactas (entregable)
```

Comprobar que todo quedó instalado:

```bash
python -c "import polars, geopandas, scipy, statsmodels, mapclassify; print('ok')"
```

## 3. Poner los datos de entrada

Copie los **6 archivos originales, con el nombre exacto con que se descargaron**, en la carpeta `staging/`:

| Archivo | Fuente |
|---|---|
| `EVALUACIONES_AGROPECUARIAS_MUNICIPALES_-_DEPARTAMENTO_DE_BOYAC_.csv` | [datos.gov.co sn28-aa8q](https://www.datos.gov.co/api/views/sn28-aa8q/rows.csv?accessType=DOWNLOAD) |
| `POBLACI_N_DE_LOS_DIFERENTES_CENTROS_POBLADOS_EN_LOS_MUNICIPIOS_DE_BOYAC__-_DEPARTAMENTO_DE_BOYAC_.csv` | [datos.gov.co seua-4ze8](https://www.datos.gov.co/api/views/seua-4ze8/rows.csv?accessType=DOWNLOAD) |
| `Medici_n_del_Desempe_o_Municipal_por_Municipio_-_DEPARTAMENTO_DE_BOYAC_.csv` | [datos.gov.co 665j-iwk5](https://www.datos.gov.co/api/views/665j-iwk5/rows.csv?accessType=DOWNLOAD) |
| `poblacion_boyaca_dane_2020_2025.csv` | Carpeta `proyecto/datos` del repositorio del curso |
| `municipios_boyaca_mgn_2025.geojson` | Carpeta `proyecto/datos` del repositorio del curso |
| `capacidad_uso_tierras_boyaca.geojson` | Servicio IGAC exportado a GeoJSON |

Si un archivo tiene otro nombre, ajústelo en `src/config.py` → `FUENTES`, no renombre a mano.

## 4. Antes de la primera corrida: dos decisiones

1. **Bloque del desempeño municipal.** En `src/config.py`, `MDM_BLOQUE_OFICIAL = "B"`. El bloque B es el que coincide con los nombres DANE. Confirme en el portal cuál bloque corresponde a 2020 y cámbielo si hace falta.
2. **Fecha de descarga.** Tras el paso 5, complete `fecha_descarga` en cada `data_lake/bronze/<fuente>/manifest.json`.

## 5. Ejecutar el pipeline completo

```bash
./run_pipeline.sh
```

Ejecuta los notebooks `01` a `08` en orden y después las pruebas. Si un notebook falla, el proceso se detiene ahí y el error queda en `outputs/logs/pipeline.log`. Los notebooks quedan guardados **con sus resultados**, listos para mostrar en la sustentación.

## 6. Ejecutar paso a paso (para desarrollar o explicar)

```bash
jupyter lab
```

Abra los notebooks de `notebooks/` en este orden; cada uno depende de los anteriores:

| Orden | Notebook | Responsable | Requiere |
|---|---|---|---|
| 1 | `01_ingesta_bronze` | P6 | Archivos en `staging/` |
| 2 | `02_silver_poblacion` | P1 | 01 |
| 3 | `03_silver_desempeno` | P1 | 02 |
| 4 | `04_agricola` | P2 | 01 |
| 5 | `05_geo_suelo` | P3 + P4 | 02 |
| 6 | `06_gold_integracion` | P6 | 02, 03, 04, 05 |
| 7 | `07_estadistica` | P5 + P2 + P4 | 06 |
| 8 | `08_mapas` | P3 | 06 |

Los notebooks 02, 04 y 05 no dependen entre sí: tres personas pueden ejecutarlos al mismo tiempo en sus máquinas.

## 7. Trabajar sin datos reales (mocks)

```bash
python -m src.mocks
```

Escribe en `tests/fixtures/` una tabla ficticia por cada contrato (`src/contratos.py`). Por ejemplo, P3 puede probar los mapas con `tests/fixtures/silver__municipios.geoparquet` antes de que exista la tabla real.

## 8. Solo las pruebas

```bash
python -m pytest -q tests
```

- Las pruebas de `test_calidad.py`, `test_estadistica.py` y `test_contratos.py` corren siempre, sin datos.
- Las de `test_bronze.py`, `test_silver.py` y `test_gold.py` se saltan (`skipped`) hasta que el pipeline haya creado esas tablas.

## 9. Dónde quedan los resultados

| Carpeta | Contenido |
|---|---|
| `data_lake/bronze/` | CSV de entrada + `manifest.json` por fuente + `manifest_bronze.json` |
| `data_lake/silver/` | Parquet y GeoParquet limpios |
| `data_lake/gold/` | Tablas analíticas |
| `data_lake/rejects/` | Registros rechazados, con la columna `motivo_rechazo` |
| `outputs/quality/` | `metricas_bronze.csv`, `metricas_silver.csv`, `metricas_gold.csv`, diagnósticos, conciliaciones y no vinculados |
| `outputs/stats/` | `resultados_hipotesis.csv`, regresiones y normalidad |
| `outputs/figures/`, `outputs/maps/` | Gráficos y mapas en PNG |

## 10. Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `FileNotFoundError ... staging/...` | Falta un archivo o tiene otro nombre | Revisar el paso 3 |
| `ValidacionError: regla 'clave_unica'...` | Datos repetidos en la fuente | Es una regla "detener": revisar el archivo, no la regla |
| `CRSError: EPSG:9377` | PROJ desactualizado | `pip install --upgrade pyproj` |
| `ModuleNotFoundError: src` | Jupyter abierto fuera del proyecto | Abrir `jupyter lab` desde la raíz del repo |
| El notebook 05 tarda | Overlay de polígonos | Es el paso más pesado; el timeout por notebook es de 20 minutos |
| `pip install geopandas` falla en Windows | Dependencias nativas | Usar WSL, como recomienda el docente |

## 11. Flujo de Git del equipo

```bash
git checkout dev && git pull
git checkout -b feature/p2-rendimientos     # rama corta por tarea
# ... trabajar SOLO en sus archivos ...
python -m pytest -q tests                    # antes de subir
git add src/silver_agricola.py src/gold_agricola.py
git commit -m "P2: reglas de calidad de la EVA"
git push -u origin feature/p2-rendimientos
# abrir PR hacia dev; lo aprueba quien consume su tabla
```

- `main` solo recibe lo que pasa `./run_pipeline.sh` completo.
- **No suban** `data_lake/` ni `outputs/` (están en `.gitignore`): se regeneran.
- Para la entrega final, generen una corrida limpia y comprímanla junto con el repositorio.
