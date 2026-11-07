# Guion de sustentación (máximo 12 minutos)

Sigue la plantilla del docente: 6 aportes de 2 minutos. Cada uno tiene una idea central y una evidencia en pantalla, repartidos en contexto (20 s), solución (60 s), evidencia (30 s) y aprendizaje (10 s). Expliquen con sus palabras: este guion es para ensayar, no para leer.

**Material en pantalla:** la página de GitHub Pages abierta. P6 hace la demostración en vivo en la terminal.

| Orden | Tema del docente | Quién | Qué muestra en pantalla |
|---|---|---|---|
| 1 | Problema, pregunta e hipótesis | P1 | Encabezado de la página y la pirámide (p1) |
| 2 | Fuentes y calidad de los datos | P2 | Sección "Calidad de datos por capa" |
| 3 | Integración y pipeline | P6 | Diagrama de arquitectura + demostración en terminal |
| 4 | Indicadores y análisis | P5 | Tabla de hipótesis y regresión con controles |
| 5 | Resultados y visualizaciones | P3 | Mapa bivariado (m6) y mapa de suelo (m5) |
| 6 | Aprendizajes y limitaciones | P4 | Sección "Limitaciones" |

Transición entre turnos: cada persona termina nombrando a la siguiente y su tema ("…y P2 les cuenta de dónde salen los datos").

---

## 1 · Problema, pregunta e hipótesis — P1

- **Contexto (20 s).** Boyacá tiene 123 municipios muy distintos: el departamento pasa de 1.248.977 habitantes en 2020 a 1.290.393 en 2025, y la mitad de los municipios tiene más de 69 % de su población fuera de la cabecera.
- **Solución (60 s).**
  - La pregunta del curso: ¿los municipios con más población de 18 a 44 años tienen mejor desempeño municipal?
  - H0: no hay asociación positiva. H1: sí la hay. Prueba unilateral con α = 0,05, fijado antes de ver los datos.
  - La proporción joven va de 25,0 % (Guayatá) a 47,3 % (Cómbita), así que hay variación suficiente para estudiarla.
  - Se usa la **proporción**, no el número de jóvenes, para no confundirla con el tamaño del municipio.
- **Evidencia (30 s).** La pirámide p1, con la franja de 20–44 años resaltada.
- **Aprendizaje (10 s).** Las fuentes no miden "disposición al cambio": solo podemos hablar de asociación.

## 2 · Fuentes y calidad de los datos — P2

- **Contexto (20 s).** Son seis fuentes de cuatro entidades (DANE, DNP, UPRA, IGAC), con formatos y años distintos.
- **Solución (60 s).**
  - Cada regla tiene una acción si falla: rechazar, alertar o detener. Resultado: 0 filas rechazadas y 9 hallazgos documentados.
  - **El MDM trae 246 filas** para 123 municipios: dos bloques rotulados 2020. En el bloque A, los códigos 15022 y 15047 tienen los nombres cruzados. Usamos el bloque B y el A en la sensibilidad.
  - **El archivo de "centros poblados"** en realidad son proyecciones por área. Sumar sus tres filas duplicaría la población, así que cargamos solo cabecera y rural.
  - **La EVA** trae 373 filas con área cosechada mayor que la sembrada. Se conservan marcadas, porque en cultivos permanentes es normal.
- **Evidencia (30 s).** La tabla de hallazgos en la página.
- **Aprendizaje (10 s).** Los datos públicos traen errores que un análisis apurado pasa por alto. Encontrarlos fue parte del resultado.

## 3 · Integración y pipeline — P6

- **Contexto (20 s).** Hay que unir fuentes que no comparten año ni formato, sin duplicar datos.
- **Solución (60 s).**
  - **Arquitectura medallón:**
    - bronze: CSV sin modificar, con manifiesto y hash;
    - silver: Parquet y GeoParquet validados;
    - gold: la tabla municipio-año (738 filas) y el maestro geográfico (123).
  - **Uniones LEFT** por código DIVIPOLA y año. El pipeline se detiene si una unión duplica filas o si cambia la población total.
  - **No hay un año común:** la hipótesis principal se hace con 2020 y las agrícolas con 2023.
  - **Herramientas:** Polars, porque el volumen cabe en memoria y Spark no aporta nada aquí. Sin particionar, porque crearía archivos de pocos KB.
- **Evidencia (30 s).** En vivo: `python -m pytest -q tests` (26 pruebas en verde). Si hay tiempo, mostrar `outputs/quality/metricas_gold.csv`.
- **Aprendizaje (10 s).** Un solo comando regenera todo desde los originales.

## 4 · Indicadores y análisis — P5

- **Contexto (20 s).** Indicadores: % de 18–44, % de 18–64, producción por 1.000 habitantes de 18–64 y rendimiento (Σ producción / Σ área).
- **Solución (60 s).**
  - **Hipótesis principal:** Spearman r = 0,24 (IC 95 % 0,06 a 0,40), p = 0,004, n = 123. Se rechaza H0, pero la asociación es débil: explica alrededor de un 6 % de las diferencias.
  - **Sensibilidad:** se mantiene sin los municipios influyentes, con el otro bloque del MDM y con la otra fuente de población (r entre 0,23 y 0,27).
  - **Con controles** (tamaño, % rural y grupo de capacidades del DNP), el efecto baja a 0,28 y deja de ser significativo (p = 0,21). Los municipios G1 tienen a la vez más jóvenes y mejor desempeño.
- **Evidencia (30 s).** La tabla de regresión con controles y la de grupos G1–G5.
- **Aprendizaje (10 s).** Una correlación significativa puede explicarse por una tercera variable. Por eso se controla.

## 5 · Resultados y visualizaciones — P3

- **Contexto (20 s).** Los mapas muestran **dónde** están los patrones, no solo si existen.
- **Solución (60 s).**
  - Siete mapas en EPSG:9377 (metros, sin deformar Boyacá).
  - Cortes por cuantiles: grupos de igual tamaño, y los cortes van en el pie de cada mapa.
  - Los municipios sin dato van en gris con trama, para no confundirlos con valores bajos.
  - **Mapa bivariado 3 × 3:** terciles de población joven × desempeño. Si los municipios se concentran en la diagonal, hay asociación positiva.
  - **Suelo:** el 78 % del área es de clases VII y VIII, con fuertes limitaciones. La papa (962.643 t en 92 municipios, 20,7 t/ha) rinde más donde hay más tierra III–IV (r = 0,41).
- **Evidencia (30 s).** Mapa m6 (bivariado) y mapa m5 (clase de suelo predominante).
- **Aprendizaje (10 s).** El mapa confirma visualmente lo que mide la correlación: un patrón real, pero débil.

## 6 · Aprendizajes y limitaciones — P4

- **Contexto (20 s).** Lo que el análisis no permite afirmar es tan importante como lo que sí.
- **Solución (60 s).** Las limitaciones:
  - Es una foto de un solo año entre municipios: no demuestra causalidad.
  - Con controles, el efecto desaparece.
  - El MDM es de 2020 y la EVA de 2023.
  - La población es una proyección.
  - El mapa del IGAC es de 2004, a escala 1:100.000: capacidad de uso, no fertilidad.
  - La producción por habitante la dominan los municipios cañeros, porque suma toneladas no comparables.
- **Evidencia (30 s).** La sección "Limitaciones" de la página.
- **Aprendizaje (10 s).** Para estudiar causalidad o "disposición al cambio" haría falta medir actitudes, tener varios años por municipio (un panel) y más controles.

---

## Respuestas cortas a las 9 preguntas del docente

| # | Pregunta | Responde | Respuesta en una frase |
|---|---|---|---|
| 1 | ¿Por qué pandas, Polars o Spark? | P6 | Polars: la tabla más grande ronda las 210.000 filas y cabe en memoria; Spark agregaría Java y un clúster sin beneficio. |
| 2 | ¿Qué validaciones por capa y por qué no particionar? | P6 | Bronze: integridad y esquema. Silver: tipos, claves, rangos y geometrías. Gold: conciliación y denominadores. No se particiona porque saldrían archivos de pocos KB. |
| 3 | ¿Por qué ese periodo y cuántos municipios? | P6 | No hay año común: 2020 para el desempeño y 2023 para la producción. Los 123 municipios en ambos. |
| 4 | ¿Centros poblados vs población municipal? | P1 | El archivo de "centros poblados" divide al municipio en cabecera y rural. La municipal oficial es la del DANE; difieren por ser versiones distintas de la proyección. |
| 5 | ¿Cómo evitaron duplicar? | P1 / P2 | Solo cabecera + rural, clave única, agregación antes de unir y conciliación de totales entre silver y gold. |
| 6 | ¿Qué significa el índice por población? | P2 | Toneladas por cada 1.000 personas de 18–64. No es productividad laboral ni valor económico. |
| 7 | ¿Qué representa la clase predominante? | P4 | La clase con más área del municipio, no la de todo el municipio. Es capacidad de uso de 2004, a escala 1:100.000. |
| 8 | ¿Magnitud y sensibilidad? | P5 | r = 0,24, débil. Se mantiene en las 3 sensibilidades y se pierde con controles (p = 0,21). |
| 9 | ¿Qué falta para estudiar causalidad? | P5 / P4 | Medir actitudes, tener un panel de varios años y un diseño de identificación. |
