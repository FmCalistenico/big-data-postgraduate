# Proyecto final: municipios de Boyacá

**Análisis de población, producción agrícola, capacidad de uso de las tierras y desempeño municipal**

Curso: ______ · Grupo: ______ · Docente: ______ · Fecha: ______

| N.º | Nombre completo | Código | Rol |
|---|---|---|---|
| 1 | | | P1 · Población y desempeño |
| 2 | | | P2 · Producción agrícola |
| 3 | | | P3 · Cartografía |
| 4 | | | P4 · Suelo IGAC |
| 5 | | | P5 · Estadística |
| 6 | | | P6 · Plataforma, calidad e integración |

> Plantilla. Cada `[COMPLETAR]` se llena con los archivos de `outputs/` después de ejecutar `./run_pipeline.sh`. Cada persona redacta su sección; P6 edita el conjunto.

## 1. Resumen (P6, al final)

[COMPLETAR: 5–6 líneas con la pregunta, los datos, el resultado de la hipótesis principal con r, IC y p, y la principal limitación.]

## 2. Planteamiento, objetivos y preguntas

Se integran cuatro dimensiones de los 123 municipios de Boyacá (población, producción agrícola, capacidad de uso de las tierras y desempeño municipal) en un pipeline reproducible, para explorar si la proporción de población de 18 a 44 años se asocia con el desempeño municipal.

Preguntas: las seis de la sección 3 del enunciado. Cada una se responde en la sección 6.

## 3. Hipótesis

- **Principal.** H0: no existe asociación positiva entre la proporción de población de 18–44 años y el puntaje MDM. H1: existe una asociación positiva. Prueba unilateral, α = 0,05.
- **Complementarias (exploratorias, con Holm):**
  - A: asociación entre la producción agrícola total y la población de 18–64 años.
  - B: asociación entre la composición de clases de capacidad de uso (% clases III–IV) y el rendimiento de papa.
  - D: patrones de mujeres y hombres de 18–44 años frente al desempeño.

## 4. Fuentes y vigencias (P6)

Ver el inventario en `docs/diccionario_datos.md` y los manifiestos en `data_lake/bronze/`.

**No existe un año común entre las fuentes.** El MDM solo trae 2020 y la EVA solo 2023. Por eso:

- la hipótesis principal se evalúa con MDM 2020 y población 2020;
- las hipótesis agrícolas, con EVA 2023 y población 2023.

Efecto sobre los resultados: no se puede combinar desempeño y producción en un mismo año; las asociaciones son entre municipios y en un solo corte.

## 5. Metodología

### 5.1 Data lake y calidad (P6)

- Bronze: CSV sin modificar más un manifiesto con hash.
- Silver: Parquet y GeoParquet validados.
- Gold: tablas analíticas.
- Reglas por capa y acciones (rechazar, alertar, detener) en `src/calidad.py`.

| Capa | Reglas | Registros revisados | Afectados | Rechazados |
|---|---|---|---|---|
| Bronze | [COMPLETAR desde `metricas_bronze.csv`] | | | |
| Silver | [COMPLETAR desde `metricas_silver.csv`] | | | |
| Gold | [COMPLETAR desde `metricas_gold.csv`] | | | |

Particionamiento: no se particiona (ver `docs/justificacion_herramientas.md`).

### 5.2 Población (P1)

- Dos fuentes: `poblacion_dane` (oficial) y la proyección por áreas.
- Cabecera + rural = total, y solo se cargan cabecera y rural.
- Conciliación entre fuentes: [COMPLETAR mínimo, mediana y máximo de `conciliacion_poblacion_fuentes.csv`].

### 5.3 Desempeño municipal (P1)

- 246 filas en dos bloques; códigos cruzados en el bloque A ([COMPLETAR con `desempeno_nombres_incoherentes.csv`]).
- Bloque usado: [COMPLETAR], verificado en el portal el [COMPLETAR fecha].
- Diferencia entre bloques: [COMPLETAR resumen de `desempeno_comparacion_bloques.csv`].

### 5.4 Producción agrícola (P2)

- Reglas y alertas aplicadas, con su conteo: [COMPLETAR].
- El rendimiento se calcula como Σ producción / Σ área cosechada.
- Advertencia sobre sumar toneladas de cultivos con distinto estado físico.

### 5.5 Análisis espacial (P3, P4)

- Reparación de geometrías: [COMPLETAR conteos].
- CRS: EPSG:4326 de origen; EPSG:9377 para áreas.
- Overlay con disolución previa por clase.
- Municipios con más de 5 % sin clasificar: [COMPLETAR].

### 5.6 Integración (P6)

- Uniones LEFT sobre población.
- No vinculados por fuente: [COMPLETAR desde `no_vinculados_*.csv`].
- Municipios incluidos en la hipótesis principal: [COMPLETAR n]. En las agrícolas: [COMPLETAR n].

### 5.7 Estadística (P5)

Plan fijado antes de ver los datos; ver `docs/GUIA_EXPLICACION.md`, sección P5.

## 6. Resultados

### 6.1 Población y grupos de edad (P1)

[Figura `outputs/figures/p1_piramide_*.png` y mapa `outputs/maps/m1_poblacion_joven.png`. COMPLETAR: 3 líneas de interpretación.]

### 6.2 Producción y rendimiento por cultivo (P2)

[Figuras `p2_produccion_rendimiento_cultivos_*.png` y `p2_produccion_por_1000_*.png`, mapas `m3` y `m4`. COMPLETAR.]

### 6.3 Capacidad de uso de las tierras (P4)

[Figura `p4_distribucion_clases.png` y mapa `m5_clase_predominante.png`. COMPLETAR.]

### 6.4 Hipótesis principal (P5)

| Análisis | Método | n | r | IC 95 % | p | Conclusión |
|---|---|---|---|---|---|---|
| Principal | Pearson | | | | | |
| Principal | Spearman | | | | | |
| Sin influyentes | Spearman | | | | | |
| Bloque alterno MDM | Spearman | | | | | |
| Población fuente alterna | Spearman | | | | | |

[COMPLETAR desde `outputs/stats/h_principal_correlaciones.csv`.]

- Normalidad: [COMPLETAR desde `h_principal_normalidad.csv`].
- Regresión con controles: coeficiente de `prop_18_44_pct` = [COMPLETAR], IC = [COMPLETAR], tipo de errores = [COMPLETAR], R² ajustado = [COMPLETAR].

Figuras: `p5_dispersion_joven_mdm.png`, `m6_bivariado_joven_mdm.png` y `m7_lado_a_lado.png`.

### 6.5 Hipótesis complementarias (P2, P4, P5)

[COMPLETAR desde `outputs/stats/resultados_hipotesis.csv`: r, p y p de Holm de A, B y D.]

## 7. Limitaciones

- Las asociaciones son entre municipios y de un solo año: no permiten afirmar causalidad ni medir "disposición al cambio".
- Años distintos entre fuentes (MDM 2020, EVA 2023).
- La población es una proyección, no un conteo; las dos fuentes de población difieren.
- El MDM publicado tiene dos bloques para la misma vigencia.
- El mapa IGAC es de 2004 a escala 1:100.000: mide capacidad de uso, no fertilidad actual.
- La producción total suma toneladas de cultivos no comparables y no es valor económico.
- Las geometrías municipales están simplificadas a 75 m.

## 8. Conclusiones y recomendaciones

[COMPLETAR: conclusión de la hipótesis principal en una de tres formas: "hay evidencia de asociación positiva", "no se rechaza H0" o "datos insuficientes"; con magnitud e incertidumbre.]

Para estudiar la disposición al cambio o una relación causal se necesitaría:

- medición directa de actitudes;
- un panel de varios años por municipio;
- controles adicionales: educación, ingreso, migración y transferencias;
- un diseño de identificación.

## 9. Reproducibilidad

Ver `docs/GUIA_EJECUCION.md`. Comando: `./run_pipeline.sh`. Versiones: `requirements-lock.txt`.
