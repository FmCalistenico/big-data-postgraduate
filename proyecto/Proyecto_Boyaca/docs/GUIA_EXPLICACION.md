# Guía de explicación por persona

Sirve para explicar el proyecto **sin ejecutarlo**: qué hace cada archivo, por qué se tomó cada decisión y qué responder en la sustentación. Cada persona debe dominar su sección y la de la persona cuyo código revisa (ver "Revisa" en la tabla).

| Persona | Rol | Archivos | Notebook | Revisa |
|---|---|---|---|---|
| P1 | Población y desempeño | `silver_poblacion.py`, `silver_desempeno.py` | 02, 03 | P5 |
| P2 | Producción agrícola | `silver_agricola.py`, `gold_agricola.py` | 04 | P4 |
| P3 | Cartografía | `geo.py`, `silver_municipios.py`, `mapas.py` | 05 (parte 1), 08 | P4 |
| P4 | Suelo IGAC | `silver_suelo.py`, `gold_suelo.py` | 05 (parte 2) | P3 |
| P5 | Estadística | `estadistica.py`, `graficos.py` (dispersión) | 07 | P2 |
| P6 | Plataforma, calidad e integración | `config.py`, `calidad.py`, `contratos.py`, `mocks.py`, `ingesta_bronze.py`, `gold_integracion.py`, `tests/` | 01, 06 | P1 |

---

## La idea en 30 segundos (todos deben saber decirla)

> Construimos un data lake de tres capas para los 123 municipios de Boyacá. **Bronze** guarda los 6 archivos tal como llegaron, en CSV, con hash y manifiesto. **Silver** los limpia y valida con reglas explícitas: lo que falla va a una zona de rechazos y cada regla deja una métrica. **Gold** los integra por código DIVIPOLA y año en una tabla municipio-año, con los indicadores. Sobre gold probamos si la proporción de población de 18 a 44 años se asocia con el desempeño municipal. No encontrar asociación también es un resultado válido, y en ningún caso hablamos de causalidad.

## Cómo está organizado el código (P6, pero todos deben conocerlo)

- **`config.py`**: rutas, años de análisis, bloque oficial del MDM, CRS y catálogo de fuentes. Nadie escribe rutas a mano en otro archivo.
- **`calidad.py`**: el mismo mecanismo para todas las fuentes.
  - `Regla(nombre, expr, accion)`: `expr` es True cuando la fila cumple.
  - Acciones: `rechazar` (la fila va a `data_lake/rejects/` con su motivo), `alertar` (se cuenta, pero la fila se queda) y `detener` (el pipeline se para).
  - `validar()` aplica las reglas y escribe una fila por regla en `outputs/quality/metricas_<capa>.csv`: regla, revisados, afectados, resultado, acción y fecha. Eso es el "informe de métricas por capa" de la sección 10.1.
  - `diagnosticar()` hace un perfil por columna (tipo, nulos, únicos) en bronze y otra vez en silver: es el diagnóstico "antes y después".
- **`contratos.py`**: el esquema exacto de cada tabla (columnas, tipos y clave). Quien produce una tabla llama `cumplir()` antes de escribirla. Si falta una columna o la clave se repite, falla.
- **`mocks.py`**: genera tablas ficticias con ese mismo esquema. Así P3, P4 y P5 pudieron programar sin esperar los datos reales.
- **Notebooks delgados**: toda la lógica vive en `src/`; los notebooks solo llaman funciones y muestran tablas. Así el código se puede probar con pytest y Git no tiene conflictos en los `.ipynb`.

---

## P1 · Población y desempeño municipal

### Qué hace `silver_poblacion.py`

1. Lee el CSV de bronze **todo como texto**: bronze no se tipa, para no perder valores raros sin darse cuenta.
2. Normaliza `codigo_municipio` a texto de 5 dígitos con `zfill(5)` y convierte los conteos a enteros. Lo que no sea número queda null y una regla lo rechaza.
3. Reglas que rechazan:
   - código válido;
   - año entre 2020 y 2025;
   - conteos presentes y no negativos;
   - total > 0;
   - 18–44 ≤ 18–64 ≤ total.
4. Reglas que alertan: hombres + mujeres = total, y hombres + mujeres de 18–44 = 18–44. La regla de clave única municipio-año **detiene**.
5. Verifica 123 municipios por año.

### Qué hace `construir_poblacion_area()`

- El archivo llamado "centros poblados" **no son centros poblados**: son proyecciones DANE por área, con tres filas por municipio y año (Cabecera, Centros poblados y rural disperso, Total), por edad simple y sexo.
- Comprueba que cabecera + rural = total, y luego **descarta la fila Total**. Así es imposible sumar dos veces la misma población.
- Lo pasa a formato largo (municipio, año, área, sexo, edad, personas) para la pirámide y el % rural.
- Compara su total con `poblacion_dane` y guarda la diferencia en `conciliacion_poblacion_fuentes.csv`. Son dos versiones de la proyección.

### Qué hace `silver_desempeno.py`

- El archivo trae **246 filas para 123 municipios**: dos bloques con valores distintos, ambos rotulados 2020. Se marcan A (filas 1–123) y B (124–246) y se conservan los dos.
- Compara el nombre de cada fila con el nombre DANE de su código, sin tildes. En el bloque A, 15022 y 15047 tienen los nombres cruzados.
- El bloque oficial está en `config.MDM_BLOQUE_OFICIAL`. Allí un nombre incoherente se rechaza; el otro bloque se usa en la sensibilidad.

### Preguntas que le harán

- **¿Qué diferencia hay entre población de centros poblados y población municipal?** El archivo de "centros poblados" divide la población municipal en cabecera y resto rural. La población municipal es la suma de ambas, que ya viene en la fila Total. Usamos `poblacion_dane` como población municipal oficial y el archivo por áreas solo para el desglose. Las dos versiones difieren un poco y lo reportamos.
- **¿Cómo evitaron duplicar población?** Validando que cabecera + rural = total y cargando solo cabecera y rural, nunca las tres filas. En gold, una prueba compara la población total con la de silver: si cambia, el pipeline se detiene.
- **¿Por qué hay dos bloques de desempeño?** La fuente publica 246 filas para una sola vigencia. Lo documentamos, elegimos un bloque y medimos cuánto cambia el resultado con el otro.

---

## P2 · Producción agrícola

### Qué hace `silver_agricola.py`

1. Renombra a snake_case y descarta columnas duplicadas de la fuente (`Cultivo2`, `Periodo2`).
2. Antes de convertir números, **cuenta** los valores que no se pueden leer. Así se distingue "venía vacío" de "venía con texto raro". Acepta `1234.5` y `1.234,5`.
3. Reglas que **rechazan:**
   - departamento distinto de 15 o código inválido;
   - periodo mal escrito;
   - producción o área faltantes (faltante no es cero);
   - valores negativos;
   - filas repetidas por municipio-cultivo-periodo-estado.
4. Reglas que **solo alertan** y quedan marcadas en columnas `alerta_*`, sin borrar nada:
   - área cosechada > sembrada, que puede ser legítimo en cultivos permanentes;
   - producción sin área cosechada;
   - rendimientos extremos.

### Qué hace `gold_agricola.py`

- Suma los periodos A y B del año por municipio y cultivo.
- **Rendimiento = Σ producción / Σ área cosechada**, como pide la sección 6, nunca el promedio de rendimientos. Con área 0, el rendimiento queda null y se cuenta.
- Concilia: la producción total en gold debe ser igual a la de silver. Si no, el pipeline se detiene.
- `resumen_municipal()` deja por municipio la producción total, la de papa y el rendimiento de papa. Un municipio sin papa queda en null, no en 0.

### Hipótesis A (en el notebook 07)

Asociación entre la producción total y la población de 18–64 años. Usa Spearman porque la producción está muy sesgada, y también una regresión log-log.

### Preguntas que le harán

- **¿Cómo evitaron duplicar producción?** Clave única en silver, agregación a municipio-cultivo antes de unir y conciliación de totales entre silver y gold.
- **¿Qué significa la producción por 1.000 habitantes de 18–64 y qué no mide?** Toneladas de todos los cultivos por cada mil personas de ese rango de edad. No es productividad laboral, porque no todas esas personas trabajan en el campo. Tampoco es valor económico, porque suma toneladas de cultivos distintos.
- **¿Por qué 2023?** Es la única vigencia del archivo EVA.

---

## P3 · Cartografía

### Qué hace `geo.py` y `silver_municipios.py`

- `leer_csv_wkt()` reconstruye los polígonos desde la columna WKT de bronze con el CRS que quedó en el manifiesto.
- `reparar_geometrias()`:
  - cuenta las geometrías nulas, vacías e inválidas;
  - repara las inválidas con `make_valid`;
  - conserva solo las partes que son polígonos (a veces la reparación deja líneas sueltas).
- Valida 123 municipios únicos.
- Mide cuánto cambia el área por la simplificación a 75 m del docente, frente a la `area_km2` oficial.
- Pone el nombre oficial DANE (el MGN viene en mayúsculas).

### Qué hace `mapas.py`

- `coropleta()`:
  - cortes por cuantiles, declarados en el pie;
  - municipios sin dato en gris con trama y con su propia entrada en la leyenda;
  - fuente y unidad visibles;
  - dibujado en EPSG:9377 para no deformar.
- `categorico()`: la clase de suelo predominante.
- `bivariado()`: 3 × 3 por terciles de población joven y desempeño, con una paleta bivariada estándar y una leyenda en cuadrícula. El pie da los cortes exactos.
- `lado_a_lado()`: la misma comparación en dos paneles, más fácil de leer para quien no conoce los mapas bivariados.

### Preguntas que le harán

- **¿Por qué cuantiles?** Reparten los municipios en grupos de igual tamaño y así ningún color queda vacío. La desventaja es que dos municipios con valores muy parecidos pueden caer en clases distintas, y por eso el pie da los cortes.
- **¿Cómo se lee el bivariado?** La esquina azul oscura es joven alto con desempeño alto, y la gris claro, ambos bajos. Si los municipios se concentran en la diagonal, hay asociación positiva.

---

## P4 · Suelo IGAC

### Qué hace `silver_suelo.py`

- Asume EPSG:4326 porque el GeoJSON **no declara CRS** y sus coordenadas están en grados. Queda registrado en el manifiesto.
- Valida las clases (I–VIII, ZU y CA) y registra que en Boyacá no aparecen las clases I ni II.
- Repara las geometrías y calcula el área en EPSG:9377 (metros). La compara con el área que reporta el IGAC.

### Qué hace `gold_suelo.py` (el overlay)

1. Reproyecta municipios y suelo a **EPSG:9377 antes de intersectar**: un área en grados no tiene sentido.
2. **Disuelve** el suelo por clase, de cientos de polígonos a uno por clase. El overlay es mucho más rápido y el resultado por clase es idéntico.
3. `overlay(how="intersection", keep_geom_type=True)`: se queda solo con áreas y descarta las líneas de los bordes compartidos.
4. Calcula:
   - % de cada clase = área de la clase en el municipio / área municipal cubierta por la capa;
   - % sin clasificar = la parte del municipio que la capa no cubre;
   - la clase predominante, solo entre clases agrológicas: ZU y CA no cuentan como suelo.

### Hipótesis B (en el notebook 07)

Asociación entre el % de clases III–IV (las de menos limitaciones presentes en Boyacá) y el rendimiento de papa, solo en municipios con papa reportada.

### Preguntas que le harán

- **¿Qué representa la clase predominante y cuáles son sus limitaciones?** Es la clase con más área en el municipio, pero no significa que todo el municipio tenga ese suelo. El mapa es de 2004 y a escala 1:100.000: mide capacidad de uso, no fertilidad actual. Por eso usamos la composición en porcentaje y no solo la clase predominante.
- **¿Por qué EPSG:9377?** Es el sistema oficial de Colombia (MAGNA-SIRGAS Origen Nacional), en metros, con poca distorsión de áreas en todo el país.

---

## P5 · Estadística

### Plan fijado antes de ver los datos (`estadistica.py`)

- **H0:** no hay asociación positiva entre `prop_18_44_pct` y `puntaje_mdm`. **H1:** sí la hay. Es unilateral, con α = 0,05, en 2020 y con hasta 123 municipios.
- **Correlaciones:** Pearson y Spearman, cada una con su intervalo de confianza del 95 % (transformación z de Fisher; para Spearman, con el error estándar de Bonett-Wright) y su valor p.
  - Shapiro-Wilk revisa la normalidad.
  - Si se rechaza, o si hay observaciones influyentes, la medida principal es Spearman, que se basa en rangos.
- **Regresión simple:** MDM = β0 + β1 · prop_18_44.
- **Regresión con controles:**
  - log de la población, porque el tamaño cambia la capacidad administrativa;
  - % rural;
  - grupo de capacidades iniciales G1–G6, que el mismo DNP usa para comparar municipios parecidos.
- **Diagnósticos:**
  - Breusch-Pagan; si detecta heterocedasticidad, se usan errores robustos HC3;
  - distancia de Cook > 4/n para las observaciones influyentes;
  - VIF para la colinealidad entre controles.
- **Sensibilidad:**
  - (a) sin las observaciones influyentes;
  - (b) con el otro bloque del MDM;
  - (c) con la proporción joven calculada desde la fuente por áreas.
- **Comparaciones múltiples:** la hipótesis principal se lee con α = 0,05. Las complementarias son exploratorias y su valor p se ajusta por Holm, para no "encontrar" algo solo porque se probaron muchas cosas.

### Cómo se concluye

Solo una de tres frases: "hay evidencia de asociación positiva", "no se rechaza H0" o "datos insuficientes". Siempre va con r y su intervalo, y nunca habla de causalidad.

### Preguntas que le harán

- **¿Cuál fue la magnitud y qué pasó en la sensibilidad?** Leer de `outputs/stats/h_principal_correlaciones.csv`: el r de Spearman, su IC, el p y si la conclusión se mantiene en las tres variantes.
- **¿Qué información haría falta para estudiar la "disposición al cambio" o la causalidad?**
  - Una medición directa de actitudes, como encuestas.
  - Datos de varios años del mismo municipio (panel), para ver cambios y no solo diferencias.
  - Variables que hoy no controlamos: educación, ingresos, migración, transferencias.
  - Un diseño que aísle el efecto, como un experimento natural.
- **¿Por qué una correlación entre municipios no es causalidad?** Puede haber una tercera variable que mueve las dos (por ejemplo, ser municipio urbano), la causalidad puede ir al revés y, además, es una foto de un solo año.

---

## P6 · Plataforma, calidad e integración

### Qué hace `ingesta_bronze.py`

- Los CSV se copian **byte a byte**.
- Los GeoJSON se exportan a CSV con WKT, como exige la sección 4.
- Manifiesto por fuente con URL, entidad, hash SHA-256 del original y del CSV, tamaño, codificación, filas, columnas, CRS y pasos de conversión.
- Una prueba verifica que el hash no cambie: bronze nunca se toca.

### Qué hace `gold_integracion.py`

- Parte de la población (123 × 6 años) y une con **LEFT JOIN**: el desempeño (2020), la producción (2023), el % rural y el suelo.
- Cada fuente llega ya agregada a su grano, así que una unión no puede multiplicar filas.
  - Si el número de filas cambia, el pipeline se detiene.
  - Si la población total cambia, también se detiene.
- En cada unión registra las coincidencias y guarda los **no vinculados** en `no_vinculados_<fuente>.csv` (sección 7.3).
- Cada variable vive en su año: `puntaje_mdm` solo en 2020 y la producción solo en 2023. En los demás años quedan null, nunca 0. Una regla lo verifica.

### Justificación de herramientas y particionamiento

Ver `docs/justificacion_herramientas.md`.

### Preguntas que le harán

- **¿Por qué Polars y no Spark?** Las fuentes tabulares tienen entre 246 y 2.613 filas, y la capa de suelo 958 polígonos; la tabla más grande que generamos (población por edad, sexo y área) ronda las 210.000 filas. Spark necesitaría Java y una sesión distribuida para un volumen que cabe en memoria muchas veces. Polars es rápido, tiene tipos estrictos y su sintaxis de expresiones se parece a Spark. Pandas se usa solo donde lo exigen GeoPandas y statsmodels.
- **¿Qué validaciones hay en cada capa?**
  - Bronze: integridad (hash), esquema observado y duplicados exactos.
  - Silver: tipos, claves, rangos, unidades, coherencia de códigos y nombres, y geometrías.
  - Gold: clave municipio-año, conciliación con silver, denominadores, ausencia de divisiones por cero, porcentajes entre 0 y 100, y cada variable en su año.
- **¿Por qué no particionaron?** La tabla más grande ronda las 210.000 filas y ocupa pocos megabytes en Parquet. Particionar por año crearía archivos de unos pocos kilobytes (el "problema de archivos pequeños"), sin ganancia en las consultas, que siempre leen la tabla completa.
- **¿Por qué se eligió el periodo y cuántos municipios quedaron?** No hay un año común: el desempeño solo es de 2020 y la producción solo de 2023. Los municipios incluidos se leen en `metricas_gold.csv` (reglas `mdm_disponible_en_2020` y `produccion_disponible_en_2023`).

---

## Las 9 preguntas de la sustentación (sección 13) → quién responde

| # | Pregunta | Responde | Dónde está la respuesta |
|---|---|---|---|
| 1 | ¿Por qué pandas, Polars o Spark? | P6 | Sección P6 y `justificacion_herramientas.md` |
| 2 | ¿Qué validaciones por capa y por qué no particionar? | P6 | Sección P6 y `outputs/quality/` |
| 3 | ¿Por qué ese periodo y cuántos municipios? | P6 / P5 | Sección P6 |
| 4 | ¿Centros poblados vs población municipal? | P1 | Sección P1 |
| 5 | ¿Cómo evitaron duplicar producción o población? | P1 / P2 | Secciones P1 y P2 |
| 6 | ¿Qué significa el índice por población? | P2 | Sección P2 |
| 7 | ¿Qué representa la clase predominante? | P4 | Sección P4 |
| 8 | ¿Magnitud de la asociación y sensibilidad? | P5 | `outputs/stats/` |
| 9 | ¿Qué falta para estudiar disposición al cambio o causalidad? | P5 | Sección P5 |
