# Notebooks vigentes

Preparado por el PhD Esteban Hernández, CyberColombia.

P01: 3 de octubre. P02: 9 de octubre. P03: 10 de octubre. P04: 23 de octubre. I01: 24 de octubre. Los notebooks acompañan los talleres y comparten las horas de clase; no añaden entregas obligatorias.

Preparar el único `.venv` de la raíz según la guía [Windows/WSL](../../docs/instalacion-wsl.md) o [Linux/macOS](../../docs/instalacion-linux-macos.md). En instalación nativa, adaptar `repositorio` o `REPO` a la ruta real como indica esa guía. Abrir desde `kit/` o `kit/Notebooks/`, usar el mismo entorno Python y ejecutar en orden. Los prerrequisitos son explícitos: P03 lee el Parquet producido por P02 y requiere DIVIPOLA; no ejecuta P02 ni descarga fuentes silenciosamente.

Los notebooks históricos se conservan en `supersalud/`, con su procedencia y limitaciones, y no son la guía de ejecución actual.

## Índice y propósito

Como referencia durante las prácticas, consultar la [guía práctica de pandas](../../docs/manual-pandas.md), con ejemplos sobre los CSV de DIVIPOLA, EVA y AGROSAVIA descargados con `kit/00_datos.py`.

| Notebook | Talleres y clases | Evidencia |
|---|---|---|
| [01 Perfil PQRS](01_Perfil_PQRS.ipynb) | P01 · clase 2 | Conteos, esquema, hashes y memoria por tamaño de bloque |
| [02 Parquet y contratos](02_Parquet_y_contratos.ipynb) | P02 · clase 3 | Proyección de 16 columnas, particiones, reejecución y fallo de contrato |
| [03 Calidad y consulta](03_Calidad_y_consulta.ipynb) | P03 · clase 4 | Calidad sin exclusiones arbitrarias y consulta diferida de 2024 |
| [04 Rendimiento y eventos](04_Rendimiento_y_eventos.ipynb) | P04 · clase 7; I01 · clase 8 | Equivalencia entre motores y traza finita NASA |

El notebook 04 se usa en dos momentos: detenerse tras el benchmark en clase 7 y ejecutar la sección de eventos en clase 8. Los eventos requieren `data/raw/nasa.json`, que se descarga desde el manifiesto agroambiental. Los notebooks no incorporan descargas de 1,816 GB como paso automático.

Seleccionar **BigData · WSL Ubuntu 26.04 · Python 3.12** en Windows/WSL o **BigData · Linux/macOS · Python 3.12** en instalación nativa. Instalar las dependencias mediante la guía correspondiente.

## Ruta y rama del curso

El clon se realiza desde `main`: `/mnt/c/Users/TUPTC/bigdata/big-data-postgraduate` en WSL o `~/bigdata/big-data-postgraduate` en Linux/macOS. El entorno está en `.venv` de la raíz; adaptar las rutas explícitas del notebook al clon local. Para actualizar, situarse en `main` y ejecutar `git pull --ff-only origin main` después de revisar los cambios locales.

## Ejercicios geoespaciales

| Notebook | Archivos requeridos | Productos |
|---|---|---|
| [E08 Geometrías e intersección](E08_Geoespacial.ipynb) | DANE departamentos y municipios; IGAC capacidad y química; AGROSAVIA y DIVIPOLA para unión tabular | Mapa, GeoPackage, CSV y controles |
| [E09 Suelo y profundidad](E09_Geoespacial.ipynb) | SoilGrids, WoSIS, IGAC química y correlación | Mapa, perfiles y control_suelo.json |
| [E11 Soporte climático](E11_Geoespacial.ipynb) | NASA y CHIRPS | Mapa, serie NASA y control_clima.json |

Los notebooks no descargan datos automáticamente. Preparar las fuentes según cada taller. Los datos originales se conservan; `kit/salidas/` se regenera. GeoPandas gestiona vectores y Rasterio los rásteres; Matplotlib produce los mapas. El notebook E11 cubre el soporte espacial: la reproducción Spark sigue en el enunciado E11.

## Enfoque de la clase 2

P01 declara una ruta WSL editable y utiliza `pd.read_csv`, inspección, filtros y comprobaciones visibles; no importa scripts del curso. Su solución de referencia conserva este desarrollo. Los bucles de lectura por bloques se introducen después de inspeccionar un bloque. P02 y P03 continúan con operaciones pandas explícitas; las funciones del kit quedan como referencia de automatización después de comprender los pasos. Las plantillas PD01–PD03 también declaran rutas explícitas y muestran cada lectura sin funciones auxiliares.

## P02 → P03: archivos y API visibles

P02 explica `read_csv`, selección y conversión, `concat`, `groupby`, `to_csv`, `to_parquet`, `read_parquet`, contrato defectuoso y comprobación de reejecución. P03 lee `kit/salidas/pandas/P02/pqrs.parquet` y muestra reglas, `merge`, cardinalidad, anti-joins y consultas equivalentes en pandas, Polars y DuckDB. Preparar DIVIPOLA antes de P03; las salidas de este notebook quedan en `kit/salidas/pandas/P03`. Las soluciones de referencia mantienen los mismos pasos.
