# Guía rápida de DuckDB con comparaciones con pandas

SQL analítico con tablas pequeñas, resultados esperados y operaciones equivalentes en pandas. Los ejemplos usan ventas ficticias y no requieren descargar datos.

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

**DuckDB** es un motor SQL analítico que funciona dentro del proceso de Python, sin levantar un servidor. Su utilidad frente a pandas es expresar consultas, uniones y ventanas en SQL, incluso sobre archivos. También puede consultar un DataFrame de pandas y devolver el resultado a pandas: ambas herramientas pueden complementarse. [SQL sobre pandas](https://duckdb.org/docs/current/guides/python/sql_on_pandas).

Las comparaciones usan **DuckDB 1.4.1 y pandas 2.2.3**. Instalación en la terminal:

```bash
python -m pip install duckdb==1.4.1 pandas==2.2.3
```

Ejecutar los bloques Python en orden, en cualquier notebook o carpeta. No se requieren datos del curso. Se registra una tabla de cuatro ventas ficticias para consultar exactamente los mismos datos con ambas herramientas.

```python
import duckdb
import pandas as pd

pdf = pd.DataFrame({
    "id": [1, 2, 3, 4],
    "producto": ["A", "B", "A", "C"],
    "cantidad": [2, 1, 3, 1],
    "precio": [10.0, 20.0, 10.0, None],
})
con = duckdb.connect()
con.register("ventas", pdf)
con.sql("SELECT * FROM ventas ORDER BY id").show()
```

| id | producto | cantidad | precio |
|---:|:---:|---:|---:|
| 1 | A | 2 | 10 |
| 2 | B | 1 | 20 |
| 3 | A | 3 | 10 |
| 4 | C | 1 | ausente |

> **📘 Frente a pandas:** `register` expone el DataFrame a SQL, sin crear una tabla persistente. `con.sql` devuelve una relación; `.show()` muestra filas y `.df()` devuelve un DataFrame de pandas. La conexión es en memoria y se cierra al final de la guía.

> **Comparación práctica:** pandas es directo para explorar estas cuatro filas. La ventaja de DuckDB aparece cuando conviene usar SQL o consultar archivos sin cargar primero toda la entrada en pandas. El ejemplo pequeño no mide velocidad.

## 2. Leer datos

Se crea un archivo de dos filas para explicar lectura y conservación de códigos:

```python
from pathlib import Path

salida = Path("ejemplo_duckdb")
salida.mkdir(exist_ok=True)
ruta_csv = salida / "codigos.csv"
ruta_csv.write_text("codigo,valor\n001,10\n002,20\n", encoding="utf-8")
leida = con.execute(
    "SELECT * FROM read_csv(?, header=true, all_varchar=true)",
    [str(ruta_csv)],
).fetchall()
leida_pd = pd.read_csv(ruta_csv, dtype=str)
assert leida == list(leida_pd.itertuples(index=False, name=None)) == [("001", "10"), ("002", "20")]
```

| Necesidad | DuckDB | pandas |
|---|---|---|
| Separador | `delim=';'` | `sep=';'` |
| Todo como texto | `all_varchar=true` | `dtype=str` |
| Elegir columnas | `SELECT codigo` | `usecols=["codigo"]` |
| Explorar pocas filas | `LIMIT 5` | `nrows=5` |

> **Ventaja frente a pandas:** SQL puede filtrar y resumir directamente desde `read_csv` antes de traer el resultado a Python. pandas también permite leer columnas concretas y CSV por bloques; para combinar los resultados parciales hay que definir el procedimiento.

> **⚠️ Parámetros:** `?` representa un valor, como una ruta o un umbral; no sustituye nombres de columnas. Volver a ejecutar este bloque reemplaza el CSV de ejemplo.

## 3. Inspeccionar

```python
con.sql("DESCRIBE ventas").show()
con.sql("SELECT * FROM ventas ORDER BY id LIMIT 2").show()
perfil = con.sql("""
    SELECT count(*) AS filas, count(precio) AS con_precio,
           count(*) FILTER (WHERE precio IS NULL) AS sin_precio
    FROM ventas
""").fetchone()
assert perfil == (len(pdf), pdf["precio"].count(), pdf["precio"].isna().sum()) == (4, 3, 1)
```

| Necesidad | DuckDB | pandas |
|---|---|---|
| Tipos | `DESCRIBE ventas` | `pdf.dtypes` |
| Resumen | `SUMMARIZE ventas` | `pdf.describe()` |
| Filas | `count(*)` | `len(pdf)` |
| Presentes | `count(precio)` | `pdf["precio"].count()` |
| Distintos sin nulos | `count(DISTINCT producto)` | `pdf["producto"].nunique()` |

> **Ventaja frente a pandas:** un perfil SQL puede ejecutarse sobre una fuente grande y devolver solo unos pocos números. Si el DataFrame ya está cargado, pandas ofrece una inspección igualmente sencilla.

## 4. Convertir tipos y tratar ausencias

```python
numeros = con.sql("""
    SELECT original, TRY_CAST(original AS INTEGER) AS numero
    FROM (VALUES (1, '10'), (2, 'error'), (3, NULL)) AS t(orden, original)
    ORDER BY orden
""").fetchall()
numeros_pd = pd.to_numeric(pd.Series(["10", "error", None]), errors="coerce").astype("Int64")
assert numeros == [("10", 10), ("error", None), (None, None)]
assert numeros_pd.isna().sum() == 2
```

`VALUES` define una tabla dentro de SQL. `TRY_CAST` devuelve `NULL` si no puede convertir; `CAST` genera un error ante una conversión incompatible.

| Necesidad | DuckDB | pandas |
|---|---|---|
| Detectar ausencia | `precio IS NULL` | `pdf["precio"].isna()` |
| Sustituir ausencia | `coalesce(precio, 0)` | `pdf["precio"].fillna(0)` |
| Vacío a nulo | `nullif(texto, '')` | `.replace('', pd.NA)` |
| Fecha con formato | `try_strptime(texto, '%Y-%m-%d')` | `pd.to_datetime(..., format='%Y-%m-%d', errors='coerce')` |

> **Ventaja frente a pandas:** SQL permite convertir y auditar datos dentro de la consulta, antes de materializarlos en Python. pandas ofrece conversiones equivalentes; no hace falta migrar solo para convertir tres valores.

> **⚠️ Ausencias:** usar `IS NULL`, nunca `= NULL`. Un precio desconocido no es cero. Un `NaN` flotante nativo de DuckDB tampoco es lo mismo que `NULL`; al consultar esta columna de pandas, su ausencia se representa como `NULL`.

## 5. Seleccionar y filtrar

```python
seleccion = con.execute("""
    SELECT id, producto FROM ventas
    WHERE cantidad >= ? ORDER BY id
""", [2]).fetchall()
seleccion_pd = pdf.loc[pdf["cantidad"] >= 2, ["id", "producto"]]
assert seleccion == list(seleccion_pd.itertuples(index=False, name=None)) == [(1, "A"), (3, "A")]
```

| Necesidad | SQL | pandas |
|---|---|---|
| Igualdad | `producto = 'A'` | `pdf["producto"] == "A"` |
| Pertenencia | `producto IN ('A', 'B')` | `pdf["producto"].isin(["A", "B"])` |
| Intervalo inclusivo | `cantidad BETWEEN 1 AND 3` | `pdf["cantidad"].between(1, 3)` |
| Condiciones | `AND`, `OR`, `NOT` | `&`, `\|`, `~` y paréntesis |

> **Ventaja frente a pandas:** SQL reúne selección, filtro y orden en una consulta declarativa. pandas permite hacer lo mismo con `loc` y `sort_values`; elegir SQL puede facilitar la lectura para quien ya trabaja con bases de datos.

> **⚠️ Comillas:** `'A'` es un valor de texto; `"producto"` es un nombre de columna. Sin `ORDER BY`, no se debe asumir el orden del resultado.

## 6. Crear y transformar columnas

```python
con.execute("""
    CREATE OR REPLACE VIEW calculada AS
    SELECT *, cantidad * precio AS importe,
           CASE WHEN cantidad >= 2 THEN 'varias' ELSE 'una' END AS tipo
    FROM ventas
""")
pdf_calculada = pdf.assign(importe=pdf["cantidad"] * pdf["precio"], tipo="una")
pdf_calculada.loc[pdf_calculada["cantidad"] >= 2, "tipo"] = "varias"
assert con.sql("SELECT importe FROM calculada ORDER BY id").fetchall() == [(20.0,), (20.0,), (30.0,), (None,)]
```

> **📘 Vista:** guarda una consulta, no una copia de los resultados. `AS` nombra una columna calculada y `CASE` aplica una condición. `calculada` depende de la fuente `ventas`.

> **Ventaja frente a pandas:** una vista nombra una transformación reutilizable en consultas posteriores. `assign` de pandas crea otro DataFrame con las columnas calculadas. Ambas multiplicaciones operan sobre columnas; ninguna requiere una función Python por fila.

## 7. Claves y duplicados

```python
con.execute("""
    CREATE OR REPLACE VIEW repetida AS
    SELECT * FROM ventas
    UNION ALL
    SELECT * FROM ventas WHERE id = 1
""")
sin_repetidas = con.sql("SELECT DISTINCT * FROM repetida ORDER BY id").fetchall()
repetida_pd = pd.concat([pdf, pdf.head(1)], ignore_index=True)
sin_repetidas_pd = repetida_pd.drop_duplicates()
assert con.sql("SELECT count(*) FROM repetida").fetchone()[0] == 5
assert len(sin_repetidas) == len(sin_repetidas_pd) == 4
```

`UNION ALL` apila conservando repeticiones. `UNION` elimina filas idénticas. Dos ventas de A no son duplicados: tienen identificadores y cantidades distintos.

> **Ventaja frente a pandas:** `DISTINCT` puede aplicarse directamente sobre consultas de archivos. Para datos ya cargados, `drop_duplicates` es igual de expresivo. `DISTINCT producto` devuelve productos únicos, no ventas únicas: seleccionar columnas cambia qué se deduplica en ambas herramientas.

## 8. Ordenar, agrupar y resumir

```python
resumen = con.sql("""
    SELECT producto, count(*) AS ventas, count(importe) AS con_importe,
           sum(importe) AS importe_total
    FROM calculada GROUP BY producto ORDER BY producto
""").fetchall()
resumen_pd = pdf_calculada.groupby("producto", dropna=False).agg(
    ventas=("id", "size"),
    con_importe=("importe", "count"),
    importe_total=("importe", lambda s: s.sum(min_count=1)),
).reset_index()
assert resumen == [("A", 2, 2, 50.0), ("B", 1, 1, 20.0), ("C", 1, 0, None)]
assert resumen_pd["ventas"].sum() == 4
```

| producto | ventas | con_importe | importe_total |
|:---:|---:|---:|---:|
| A | 2 | 2 | 50 |
| B | 1 | 1 | 20 |
| C | 1 | 0 | ausente |

> **Ventaja frente a pandas:** DuckDB optimiza la consulta completa y puede aprovechar ejecución paralela. En pandas, `groupby` es cómodo cuando la tabla cabe en memoria. Para filtrar grupos en SQL se usa `HAVING`, por ejemplo `HAVING count(*) > 1`.

> **⚠️ Comparación de nulos:** SQL conserva el grupo con clave nula; pandas necesita `dropna=False`. `sum` de DuckDB devuelve `NULL` si no hay valores presentes; pandas necesita `min_count=1` para conservar esa ausencia. Sin igualar estas reglas, las comparaciones pueden ser engañosas.

## 9. Combinar tablas

```python
catalogo_pd = pd.DataFrame({"producto": ["A", "B"], "familia": ["hogar", "oficina"]})
con.register("catalogo", catalogo_pd)
assert con.sql("SELECT count(*) = count(DISTINCT producto) FROM catalogo").fetchone()[0]
unida = con.sql("""
    SELECT v.*, c.familia
    FROM ventas v LEFT JOIN catalogo c USING (producto)
    ORDER BY id
""").df()
unida_pd = pdf.merge(catalogo_pd, on="producto", how="left", validate="many_to_one")
sin_catalogo = con.sql("""
    SELECT v.producto FROM ventas v ANTI JOIN catalogo c USING (producto)
""").fetchall()
assert len(unida) == len(unida_pd) == 4
assert sin_catalogo == [("C",)]
```

| Necesidad | DuckDB | pandas 2.2.3 |
|---|---|---|
| Coincidencias | `INNER JOIN` | `merge(..., how="inner")` |
| Todas las ventas | `LEFT JOIN` | `merge(..., how="left")` |
| Sin correspondencia | `ANTI JOIN` | `merge(..., indicator=True)` y filtrar `left_only` |
| Validar cardinalidad | Consultar unicidad antes del join | `validate="many_to_one"` |

> **Ventaja frente a pandas:** SQL expresa directamente anti-joins y consultas entre varias fuentes. pandas tiene la comodidad de validar cardinalidad dentro de `merge`; con DuckDB se añade un control explícito como el del ejemplo.

> **⚠️ Nulos:** una igualdad SQL no empareja dos claves `NULL`; pandas sí puede emparejar claves ausentes en `merge`. Las claves repetidas pueden multiplicar filas en ambas herramientas.

## 10. Guardar y procesar archivos grandes

Se escribe un Parquet pequeño para entender una consulta que también puede aplicarse a archivos mayores:

```python
def literal_sql(valor):
    return "'" + str(valor).replace("'", "''") + "'"

ruta_parquet = literal_sql(salida / "ventas.parquet")
con.execute(f"COPY calculada TO {ruta_parquet} (FORMAT PARQUET)")
consulta = f"""
    SELECT producto, sum(importe) AS importe_total
    FROM read_parquet({ruta_parquet})
    WHERE cantidad >= 2 GROUP BY producto ORDER BY producto
"""
resultado = con.sql(consulta).fetchall()
assert resultado == [("A", 50.0)]
con.sql("EXPLAIN " + consulta).show()

# pandas: cálculo equivalente sobre la tabla ya cargada
resultado_pd = pdf_calculada.loc[pdf_calculada["cantidad"] >= 2].groupby("producto")["importe"].sum()
assert resultado_pd.to_dict() == {"A": 50.0}
```

> **Ventaja frente a pandas:** DuckDB consulta el Parquet y trae solo el resumen. Puede usar disco temporal en numerosas operaciones que superan la memoria disponible. pandas también puede leer Parquet con columnas y filtros, usando un motor compatible; después materializa un DataFrame. [Rendimiento y límites de memoria](https://duckdb.org/docs/current/guides/performance/how_to_tune_workloads).

| Necesidad | DuckDB | pandas |
|---|---|---|
| Guardar CSV | `COPY ... TO ... (FORMAT CSV, HEADER true)` | `to_csv(..., index=False)` |
| Guardar Parquet | `COPY ... TO ... (FORMAT PARQUET)` | `to_parquet(..., index=False)`; requiere motor como PyArrow |
| Revisar ejecución | `EXPLAIN`, `EXPLAIN ANALYZE` | Medir los pasos del código |
| Devolver a pandas | `.df()` sobre el resultado | El resultado ya es un DataFrame |

> **⚠️ Memoria y medición:** `.df()` y `.fetchall()` traen el resultado a Python y este debe caber en memoria. `COPY` permite escribir sin traerlo completo. No todas las consultas pueden desbordar todos sus estados a disco. Los cuatro registros enseñan el mecanismo, no prueban superioridad de velocidad. Reejecutar el bloque reemplaza el Parquet de ejemplo.

## 11. Recetas para problemas comunes

### Total del grupo en cada fila

```python
con_total = con.sql("""
    SELECT id, sum(cantidad) OVER (PARTITION BY producto) AS cantidad_producto
    FROM ventas ORDER BY id
""").fetchall()
con_total_pd = pdf.groupby("producto")["cantidad"].transform("sum")
assert [fila[1] for fila in con_total] == con_total_pd.tolist() == [5, 1, 5, 1]
```

> **Ventaja frente a pandas:** `OVER` reúne ventanas en la misma consulta; `transform` resuelve el mismo patrón en pandas. Ninguno reduce las cuatro filas a una por producto.

### Venta anterior dentro del producto

```python
anterior = con.sql("""
    SELECT id, lag(cantidad) OVER (PARTITION BY producto ORDER BY id) AS cantidad_anterior
    FROM ventas ORDER BY id
""").fetchall()
anterior_pd = pdf.sort_values("id").groupby("producto")["cantidad"].shift(1)
assert anterior == [(1, None), (2, None), (3, 2), (4, None)]
assert anterior_pd.iloc[2] == 2
```

> **Ventaja frente a pandas:** SQL especifica el grupo y el orden dentro de la ventana; pandas ordena y después aplica `groupby(...).shift(...)`. En ambos, fila anterior no significa fecha anterior.

### Consulta SQL y continuación en pandas

```python
para_grafico = con.sql("""
    SELECT producto, sum(cantidad) AS unidades
    FROM ventas GROUP BY producto ORDER BY producto
""").df()
assert isinstance(para_grafico, pd.DataFrame)
assert para_grafico["unidades"].tolist() == [5, 1, 1]
```

> **Ventaja al combinar herramientas:** DuckDB hace la consulta y pandas recibe una tabla pequeña para continuar el análisis o crear gráficos. No hace falta reemplazar todo el trabajo existente en pandas.

## 12. Errores frecuentes

| Problema al venir de pandas | En DuckDB |
|---|---|
| Escribir `= NULL` | Usar `IS NULL`. |
| Usar comillas dobles para valores | Texto entre comillas simples; dobles para nombres. |
| Esperar orden implícito | Declarar `ORDER BY`. |
| Apilar con `UNION` y perder filas | Usar `UNION ALL` si se conservan repeticiones. |
| Esperar `validate` dentro del join | Comprobar unicidad y conteos explícitamente. |
| No encontrar la tabla | Usar la misma conexión y registrar la fuente. |
| Traer millones de filas con `.df()` | Agregar antes o escribir con `COPY`. |
| Comparar sumas diferentes | Igualar el tratamiento de nulos con `min_count=1` en pandas. |

> **Comparación práctica:** pandas suele ser más simple para editar unas pocas celdas o trabajar con bibliotecas que esperan sus objetos. DuckDB aporta SQL analítico, consultas sobre archivos y un optimizador; migrar solo tiene sentido si esas capacidades ayudan al flujo.

## 13. Resumen de funciones

| Tarea | DuckDB | pandas |
|---|---|---|
| Leer | `read_csv`, `read_parquet` | `read_csv`, `read_parquet` |
| Seleccionar | `SELECT`, `WHERE` | `[]`, `loc`, `query` |
| Transformar | `CASE`, `AS` | `assign`, `loc`, `where` |
| Convertir | `TRY_CAST`, `try_strptime` | `to_numeric`, `to_datetime` |
| Ausencias | `IS NULL`, `COALESCE` | `isna`, `fillna` |
| Duplicados | `DISTINCT` | `drop_duplicates` |
| Resumir | `GROUP BY`, `HAVING` | `groupby`, filtros sobre el resumen |
| Combinar | `JOIN`, `UNION ALL` | `merge`, `concat` |
| Ventanas | `OVER`, `lag` | `transform`, `shift` |
| Guardar | `COPY` | `to_csv`, `to_parquet` |

**Cuándo aprovechar DuckDB:** consultas SQL, varias fuentes y resúmenes sobre archivos. **Cuándo conservar pandas:** exploración pequeña, operaciones por índice y compatibilidad con el análisis existente. **Cuándo combinarlos:** consultar con DuckDB y devolver solo el resultado necesario a pandas.

Al terminar todos los bloques, cerrar la conexión:

```python
con.close()
```

## 14. Referencias

- [SQL sobre pandas](https://duckdb.org/docs/current/guides/python/sql_on_pandas)
- [DuckDB desde Python](https://duckdb.org/docs/stable/clients/python/overview.html)
- [Conversión de tipos](https://duckdb.org/docs/stable/sql/expressions/cast.html)
- [Funciones de ventana](https://duckdb.org/docs/stable/sql/functions/window_functions.html)
- [Lectura y escritura de Parquet](https://duckdb.org/docs/stable/data/parquet/overview.html)
- [Rendimiento y límites de memoria](https://duckdb.org/docs/current/guides/performance/how_to_tune_workloads)
- [pandas 2.2: guía de usuario](https://pandas.pydata.org/pandas-docs/version/2.2/user_guide/index.html)
