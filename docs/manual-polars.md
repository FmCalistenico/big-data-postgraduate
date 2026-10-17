# Guía rápida de Polars con comparaciones con pandas

Conceptos esenciales con tablas pequeñas, resultados esperados y la operación equivalente en pandas. Los ejemplos usan ventas ficticias y no requieren descargar datos.

> **Lectura relacionada:** [pandas](manual-pandas.md) · [Polars](manual-polars.md) · [DuckDB](manual-duckdb.md).

| Símbolo | Significado |
|:---:|---|
| 📘 | Concepto necesario para entender la operación. |
| ✅ | Control para comprobar el resultado. |
| ⚠️ | Error frecuente o límite de interpretación. |

```mermaid
flowchart LR
    A[Leer] --> B[Inspeccionar]
    B --> C[Convertir y limpiar]
    C --> D[Filtrar, agrupar o unir]
    D --> E[Comprobar totales]
    E --> F[Guardar]
```

> **📘 Idea central:** que una operación termine sin errores no significa que el resultado sea correcto. Después de cada paso se revisan las columnas, los tipos, la cantidad de filas y qué representa cada fila.

## Contenido

1. [Preparación y datos de ejemplo](#1-preparación-y-datos-de-ejemplo)
2. [Leer datos](#2-leer-datos)
3. [Inspeccionar](#3-inspeccionar)
4. [Convertir tipos y tratar ausencias](#4-convertir-tipos-y-tratar-ausencias)
5. [Seleccionar y filtrar](#5-seleccionar-y-filtrar)
6. [Crear y transformar columnas](#6-crear-y-transformar-columnas)
7. [Claves y duplicados](#7-claves-y-duplicados)
8. [Ordenar, agrupar y resumir](#8-ordenar-agrupar-y-resumir)
9. [Combinar tablas](#9-combinar-tablas)
10. [Guardar y procesar archivos grandes](#10-guardar-y-procesar-archivos-grandes)
11. [Recetas para problemas comunes](#11-recetas-para-problemas-comunes)
12. [Errores frecuentes](#12-errores-frecuentes)
13. [Resumen de funciones](#13-resumen-de-funciones)
14. [Referencias](#14-referencias)

## 1. Preparación y datos de ejemplo

**Polars** procesa tablas mediante expresiones sobre columnas. Su ventaja frente al flujo habitual de pandas aparece al encadenar transformaciones: permite construir un plan, optimizarlo y ejecutar muchas operaciones en paralelo. pandas sigue siendo cómodo para explorar tablas pequeñas y trabajar con bibliotecas que esperan sus DataFrames. Estos ejemplos enseñan la sintaxis; cuatro filas no sirven como prueba de velocidad. [Comparación oficial con pandas](https://docs.pola.rs/user-guide/migration/pandas/).

Las comparaciones usan **Polars 1.35.2 y pandas 2.2.3**. Instalación en la terminal:

```bash
python -m pip install polars==1.35.2 pandas==2.2.3
```

Ejecutar los bloques Python en orden, en cualquier notebook o carpeta. No se requieren archivos del curso. `df` es Polars y `pdf` es pandas; ambos parten de las mismas cuatro ventas ficticias.

```python
import polars as pl
import pandas as pd

datos = {
    "id": [1, 2, 3, 4],
    "producto": ["A", "B", "A", "C"],
    "cantidad": [2, 1, 3, 1],
    "precio": [10.0, 20.0, 10.0, None],
}
df = pl.DataFrame(datos)
pdf = pd.DataFrame(datos)
print(df)
```

| id | producto | cantidad | precio |
|---:|:---:|---:|---:|
| 1 | A | 2 | 10 |
| 2 | B | 1 | 20 |
| 3 | A | 3 | 10 |
| 4 | C | 1 | ausente |

> **📘 Frente a pandas:** Polars no tiene índice de filas. `id` es una columna explícita; pandas también conserva esta columna, además de su índice. Las operaciones siguientes relacionan registros mediante columnas.

## 2. Leer datos

Un CSV de dos filas basta para entender tipos y ceros iniciales:

```python
from io import StringIO

csv = "codigo,valor\n001,10\n002,20\n"
leida = pl.read_csv(StringIO(csv), schema_overrides={"codigo": pl.String})
leida_pd = pd.read_csv(StringIO(csv), dtype={"codigo": "string"})
assert leida["codigo"].to_list() == leida_pd["codigo"].tolist() == ["001", "002"]
```

| Necesidad | Polars | pandas |
|---|---|---|
| Separador | `separator=";"` | `sep=";"` |
| Elegir columnas | `columns=["codigo"]` | `usecols=["codigo"]` |
| Limitar filas | `n_rows=100` | `nrows=100` |
| Declarar tipos | `schema_overrides` | `dtype` |
| Planificar lectura | `scan_csv` | `read_csv` lee al ejecutarse |

> **Ventaja frente a pandas:** para combinar lectura, filtros y agregaciones en un plan optimizable, Polars ofrece `scan_csv`. En una lectura pequeña como esta, ambas opciones son sencillas. La sección 10 muestra la diferencia con un archivo.

## 3. Inspeccionar

```python
print(df.shape, df.schema)
print(df.head(2))
print(df.null_count())

# pandas
print(pdf.shape, pdf.dtypes)
print(pdf.head(2))
print(pdf.isna().sum())
```

> **✅ Resultado:** ambas tablas tienen cuatro filas y cuatro columnas; solo `precio` tiene un valor ausente.

| Operación | Polars | pandas |
|---|---|---|
| Dimensiones | `df.shape` | `pdf.shape` |
| Tipos | `df.schema` | `pdf.dtypes` |
| Resumen | `df.describe()` | `pdf.describe()` |
| Distintos sin nulos | `df["precio"].drop_nulls().n_unique()` | `pdf["precio"].nunique()` |

> **Comparación:** aquí no hace falta cambiar de herramienta por rendimiento. La utilidad de `schema` en Polars es ver los tipos que utilizarán las expresiones; `info()` de pandas añade un resumen cómodo de tipos y memoria. `n_unique()` de Polars cuenta el nulo como un valor distinto; `nunique()` de pandas lo excluye por defecto.

## 4. Convertir tipos y tratar ausencias

Un ejemplo aparte separa un texto incorrecto de una ausencia original:

```python
texto = ["10", "error", None]
numeros = pl.DataFrame({"original": texto}).with_columns(
    pl.col("original").cast(pl.Int64, strict=False).alias("numero")
)
numeros_pd = pd.DataFrame({"original": texto})
numeros_pd["numero"] = pd.to_numeric(numeros_pd["original"], errors="coerce").astype("Int64")
print(numeros)
assert numeros["numero"].to_list() == [10, None, None]
assert numeros_pd["numero"].isna().sum() == 2
```

| Necesidad | Polars | pandas |
|---|---|---|
| Detectar ausencias | `.is_null()` | `.isna()` |
| Sustituir ausencias | `.fill_null(0)` | `.fillna(0)` |
| Excluir filas sin precio | `df.drop_nulls("precio")` | `pdf.dropna(subset=["precio"])` |
| Convertir fecha | `.str.strptime(pl.Date, "%Y-%m-%d")` | `pd.to_datetime(..., format="%Y-%m-%d")` |

> **Ventaja frente a pandas:** Polars mantiene enteros con nulos usando su tipo entero habitual; en pandas 2.2.3 puede elegirse explícitamente el tipo anulable `"Int64"`. Ambas herramientas pueden representar el dato correctamente.

> **⚠️ Diferencia:** Polars distingue `null` de `NaN`; `fill_null` no reemplaza NaN. pandas reconoce ambos como ausencias mediante `isna()`. No convertir un precio desconocido en cero salvo que esa sea la regla del problema.

## 5. Seleccionar y filtrar

```python
seleccion = df.filter(pl.col("cantidad") >= 2).select("id", "producto")
seleccion_pd = pdf.loc[pdf["cantidad"] >= 2, ["id", "producto"]]
print(seleccion)
assert seleccion["id"].to_list() == seleccion_pd["id"].tolist() == [1, 3]
```

| Necesidad | Polars | pandas |
|---|---|---|
| Una condición | `df.filter(pl.col("cantidad") >= 2)` | `pdf.loc[pdf["cantidad"] >= 2]` |
| Varias columnas | `df.select("id", "producto")` | `pdf[["id", "producto"]]` |
| Pertenencia | `pl.col("producto").is_in(["A", "B"])` | `pdf["producto"].isin(["A", "B"])` |

> **Ventaja frente a pandas:** la misma expresión de Polars se reutiliza en un DataFrame y en un plan diferido. pandas ofrece filtros directos muy cómodos cuando la tabla ya está en memoria. En ambas bibliotecas se combinan condiciones con `&`, `|` y paréntesis.

## 6. Crear y transformar columnas

```python
df = df.with_columns(
    (pl.col("cantidad") * pl.col("precio")).alias("importe")
)
pdf = pdf.assign(importe=pdf["cantidad"] * pdf["precio"])

etiquetada = df.with_columns(
    pl.when(pl.col("cantidad") >= 2)
      .then(pl.lit("varias")).otherwise(pl.lit("una")).alias("tipo")
)
etiquetada_pd = pdf.assign(tipo="una")
etiquetada_pd.loc[etiquetada_pd["cantidad"] >= 2, "tipo"] = "varias"
assert df["importe"].to_list() == [20.0, 20.0, 30.0, None]
```

> **📘 Expresión:** `pl.col` selecciona una columna; `alias` nombra el resultado; `with_columns` añade o reemplaza columnas. `pl.lit` representa un valor literal, como `"varias"`.

> **Ventaja frente a pandas:** las expresiones de Polars se integran en el plan de cálculo. La multiplicación de pandas también es vectorizada: no necesita `apply` por fila. La comparación adecuada es entre operaciones vectorizadas de ambas herramientas.

> **⚠️ Dependencias:** si una expresión usa una columna recién creada, ponerla en otra llamada a `with_columns`.

## 7. Claves y duplicados

```python
repetida = pl.concat([df, df.head(1)])
repetida_pd = pd.concat([pdf, pdf.head(1)], ignore_index=True)
sin_repetidas = repetida.unique(maintain_order=True)
sin_repetidas_pd = repetida_pd.drop_duplicates()
assert repetida.height == 5
assert sin_repetidas.height == len(sin_repetidas_pd) == 4
```

`producto` aparece varias veces porque puede haber varias ventas del mismo producto. La repetición añadida es una fila idéntica; deduplicar solo por producto eliminaría una venta legítima.

> **Comparación con pandas:** `unique(subset=[...])` corresponde a `drop_duplicates(subset=[...])`. La ventaja de Polars es poder integrar esta operación en un flujo diferido; pandas resulta directo para una tabla pequeña. `maintain_order=True` conserva el orden, pero puede limitar optimizaciones.

## 8. Ordenar, agrupar y resumir

```python
resumen = df.group_by("producto").agg(
    pl.len().alias("ventas"),
    pl.col("importe").count().alias("con_importe"),
    pl.when(pl.col("importe").count() > 0)
      .then(pl.col("importe").sum()).otherwise(None).alias("importe_total"),
).sort("producto")
resumen_pd = pdf.groupby("producto", dropna=False).agg(
    ventas=("id", "size"),
    con_importe=("importe", "count"),
    importe_total=("importe", lambda s: s.sum(min_count=1)),
).reset_index()
print(resumen)
assert resumen["ventas"].sum() == len(pdf) == 4
```

| producto | ventas | con_importe | importe_total |
|:---:|---:|---:|---:|
| A | 2 | 2 | 50 |
| B | 1 | 1 | 20 |
| C | 1 | 0 | ausente |

El control de `count` y `min_count=1` conserva la ausencia de C. Sin ese control, la suma de un grupo sin valores presentes devuelve cero en estos ejemplos de Polars y pandas.

> **Ventaja frente a pandas:** Polars puede ejecutar agregaciones nativas en paralelo y optimizarlas dentro del plan. pandas ofrece agregaciones nombradas similares. Polars conserva grupos con clave nula; en pandas se pide `dropna=False`. Ordenar explícitamente permite comparar resultados.

## 9. Combinar tablas

```python
catalogo = pl.DataFrame({"producto": ["A", "B"], "familia": ["hogar", "oficina"]})
catalogo_pd = pd.DataFrame({"producto": ["A", "B"], "familia": ["hogar", "oficina"]})
unida = df.join(catalogo, on="producto", how="left", validate="m:1")
unida_pd = pdf.merge(catalogo_pd, on="producto", how="left", validate="many_to_one")
sin_catalogo = df.join(catalogo, on="producto", how="anti")
sin_catalogo_pd = pdf.merge(catalogo_pd, on="producto", how="left", indicator=True)
sin_catalogo_pd = sin_catalogo_pd.loc[sin_catalogo_pd["_merge"] == "left_only"]
assert unida.height == len(unida_pd) == 4
assert sin_catalogo["producto"].to_list() == sin_catalogo_pd["producto"].tolist() == ["C"]
```

> **Ventaja frente a pandas 2.2.3:** el anti-join se expresa directamente con `how="anti"`; en pandas se puede usar `indicator=True` y filtrar. Ambos permiten validar una relación de muchas ventas a un producto de catálogo.

> **⚠️ Nulos y claves:** Polars no une claves nulas por defecto; `merge` de pandas sí puede emparejarlas. En ambos, claves repetidas en el catálogo pueden multiplicar filas. `concat` apila filas; `join` o `merge` relacionan tablas por claves.

## 10. Guardar y procesar archivos grandes

Este archivo se genera con las cuatro ventas de ejemplo. Su tamaño es pequeño para entender el flujo; no es un benchmark.

```python
from pathlib import Path
from polars.testing import assert_frame_equal

salida = Path("ejemplo_polars")
salida.mkdir(exist_ok=True)
df.write_parquet(salida / "ventas.parquet")
assert_frame_equal(df, pl.read_parquet(salida / "ventas.parquet"))

plan = (
    pl.scan_parquet(salida / "ventas.parquet")
    .filter(pl.col("cantidad") >= 2)
    .select("producto", "importe")
    .group_by("producto").agg(pl.col("importe").sum())
)
print(plan.explain())
resultado = plan.collect(engine="streaming")
assert resultado.rows() == [("A", 50.0)]

# pandas: la tabla de ejemplo ya está en memoria
resultado_pd = pdf.loc[pdf["cantidad"] >= 2].groupby("producto")["importe"].sum()
assert resultado_pd.to_dict() == {"A": 50.0}
```

> **Ventaja frente a pandas:** `scan_parquet` permite optimizar conjuntamente lectura, selección y cálculo; `collect` ejecuta el plan. pandas también permite elegir columnas y aplicar filtros al leer Parquet con un motor compatible, pero sus transformaciones posteriores no constituyen un plan global diferido. [API diferida de Polars](https://docs.pola.rs/user-guide/lazy/using/).

| Necesidad | Polars | pandas |
|---|---|---|
| CSV | `df.write_csv(ruta)` | `pdf.to_csv(ruta, index=False)` |
| Parquet | `df.write_parquet(ruta)` | `pdf.to_parquet(ruta, index=False)`; requiere motor como PyArrow |
| Procesar por lotes | Motor `streaming` en un plan | `read_csv(..., chunksize=...)` y combinación manual de parciales |

> **⚠️ Memoria:** `read_csv(...).lazy()` ya cargó la entrada. `collect` devuelve un resultado que debe caber en memoria; el streaming no elimina todos los límites. `sink_parquet` permite escribir un plan directamente a disco. Reejecutar el ejemplo reemplaza su archivo de salida.

## 11. Recetas para problemas comunes

### Total del grupo en cada fila

```python
con_total = df.with_columns(pl.col("cantidad").sum().over("producto").alias("cantidad_producto"))
con_total_pd = pdf.assign(cantidad_producto=pdf.groupby("producto")["cantidad"].transform("sum"))
assert con_total["cantidad_producto"].to_list() == con_total_pd["cantidad_producto"].tolist() == [5, 1, 5, 1]
```

> **Ventaja frente a pandas:** `over` permite reutilizar expresiones como ventanas sin reducir filas; `groupby(...).transform(...)` es el equivalente habitual de pandas.

### Venta anterior dentro del producto

```python
anterior = df.sort("id").with_columns(
    pl.col("cantidad").shift(1).over("producto").alias("cantidad_anterior")
)
anterior_pd = pdf.sort_values("id").copy()
anterior_pd["cantidad_anterior"] = anterior_pd.groupby("producto")["cantidad"].shift(1)
assert anterior.filter(pl.col("id") == 3)["cantidad_anterior"].item() == 2
```

> **Comparación:** ambas herramientas requieren definir el orden antes del desplazamiento. `over` conserva la sintaxis de expresiones en Polars; pandas encadena `groupby` y `shift`. La fila anterior no implica un día anterior.

## 12. Errores frecuentes

| Problema al venir de pandas | En Polars |
|---|---|
| Buscar `.loc` o un índice implícito | Usar `filter`, `select` y claves explícitas. |
| Pasar `"texto"` a `then` | Usar `pl.lit("texto")`. |
| Usar `fill_null` para NaN | Distinguir `fill_null` y `fill_nan`. |
| Esperar idéntico conteo de distintos | Revisar si se cuenta el nulo. |
| Usar una columna recién creada en el mismo bloque | Encadenar otro `with_columns`. |
| Migrar todo a `map_elements` | Buscar primero expresiones nativas, como en pandas se prefiere vectorizar a `apply`. |
| Suponer una mejora de velocidad | Medir el flujo completo, incluidas lectura y conversiones. |

> **Comparación práctica:** la ventaja de migrar depende del trabajo. Para pocas filas, código ya probado y bibliotecas que esperan pandas, mantener pandas puede ser la opción más simple. Polars resulta atractivo cuando el flujo de transformaciones y el volumen justifican usar expresiones y planificación.

## 13. Resumen de funciones

| Tarea | Polars | pandas |
|---|---|---|
| Leer | `read_csv`, `scan_parquet` | `read_csv`, `read_parquet` |
| Seleccionar | `select`, `filter` | `[]`, `loc`, `query` |
| Transformar | `with_columns`, `when` | `assign`, `loc`, `where` |
| Ausencias | `is_null`, `fill_null` | `isna`, `fillna` |
| Duplicados | `unique` | `drop_duplicates` |
| Resumir | `group_by(...).agg(...)` | `groupby(...).agg(...)` |
| Combinar | `join`, `concat` | `merge`, `concat` |
| Ventanas | `over`, `shift` | `transform`, `shift` |
| Ordenar | `sort` | `sort_values` |
| Ejecutar plan | `collect`, `sink_parquet` | Sin equivalente directo en la API habitual |

**Cuándo aprovechar Polars:** transformaciones encadenadas, expresiones nativas y lectura diferida. **Cuándo conservar pandas:** exploración pequeña, uso del índice o integración que ya funciona. Comparar tiempos con los mismos datos, tipos, nulos y resultados; esta guía no afirma un factor universal de aceleración.

La ampliación opcional [Polars con GPU NVIDIA](polars-gpu.md) se instala por separado, después de preparar controlador y CUDA. Esta guía rápida utiliza CPU.

## 14. Referencias

- [Comparación oficial con pandas](https://docs.pola.rs/user-guide/migration/pandas/)
- [Expresiones y contextos](https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/)
- [Ejecución diferida](https://docs.pola.rs/user-guide/lazy/using/)
- [Datos ausentes](https://docs.pola.rs/user-guide/expressions/missing-data/)
- [Combinación de tablas](https://docs.pola.rs/user-guide/transformations/joins/)
- [pandas 2.2: guía de usuario](https://pandas.pydata.org/pandas-docs/version/2.2/user_guide/index.html)
