# Proyecto final: municipios de Boyacá

**Análisis de población, producción agrícola, capacidad de uso de las tierras y desempeño municipal**

Curso: Big Data · Especialización en Bases de Datos · Fecha: 2026-11-07

| N.º | Nombre completo | Código | Rol |
|---|---|---|---|
| 1 | | | P1 · Población y desempeño |
| 2 | | | P2 · Producción agrícola |
| 3 | | | P3 · Cartografía |
| 4 | | | P4 · Suelo IGAC |
| 5 | | | P5 · Estadística |
| 6 | | | P6 · Plataforma, calidad e integración |

## 1. Resumen

Se construyó un pipeline reproducible bronze → silver → gold con seis fuentes públicas (DANE, DNP, UPRA e IGAC) para los 123 municipios de Boyacá. En 2020, los municipios con mayor proporción de población de 18 a 44 años tienen, en promedio, mejor desempeño municipal: Spearman r = 0,24 (IC 95 % 0,06 a 0,40), p = 0,004, n = 123. Se rechaza H0, pero la asociación es débil. Al controlar por tamaño, % rural y grupo de capacidades, el efecto deja de ser significativo (coeficiente 0,28, IC 95 % -0,16 a 0,73, p = 0,214): buena parte de la asociación la explica el grupo de capacidades iniciales del municipio. No demuestra causalidad ni mide disposición al cambio.

## 2. Planteamiento y objetivo

Los municipios de Boyacá difieren en estructura poblacional, producción agrícola, capacidad de uso de las tierras y desempeño. El objetivo es integrar estas dimensiones en un proceso trazable y evaluar si la proporción de población adulta joven se asocia con el desempeño municipal, sin atribuir causalidad.

## 3. Hipótesis

- **Principal.** H0: no existe asociación positiva entre la proporción de población de 18 a 44 años y el puntaje MDM. H1: existe una asociación positiva. Prueba unilateral, α = 0,05 fijado antes del análisis.
- **Complementarias (exploratorias, p ajustado por Holm):** A, producción agrícola total vs población de 18–64; B, % de clases III–IV vs rendimiento de papa; D, proporciones de mujeres y hombres de 18–44 vs desempeño.

## 4. Fuentes y vigencias

| Fuente | Entidad | Vigencia | Filas |
|---|---|---|---|
| Evaluaciones Agropecuarias Municipales | UPRA / MADR | 2023 | 2.613 |
| Población por área ("centros poblados") | Gobernación con base en DANE | 2020–2024 | 1.845 |
| Medición del Desempeño Municipal | DNP | 2020 | 246 |
| Proyecciones de población municipal | DANE | 2020–2025 | 738 |
| Límites municipales MGN | DANE | 2025 | 123 |
| Capacidad de uso de las tierras 1:100.000 | IGAC | 2004 | 958 |

**No existe un año común.** El MDM solo trae 2020 y la EVA solo 2023. La hipótesis principal se evalúa con MDM y población de 2020; las agrícolas, con EVA y población de 2023. La población existe para todos los años, así que cada indicador usa el denominador de su mismo año. Efecto: desempeño y producción no se comparan en un mismo año.

## 5. Metodología

### 5.1 Data lake y calidad

- **Bronze:** los 6 archivos en CSV sin modificar; los GeoJSON se exportaron a CSV con la geometría en WKT. Manifiesto con hash SHA-256, filas, columnas, codificación y CRS.
- **Silver:** tipos, claves DIVIPOLA de 5 dígitos, rangos, coherencia código-nombre y geometrías reparadas, en Parquet y GeoParquet.
- **Gold:** tabla municipio-año, indicadores y tablas para mapas, con conciliación contra silver.
- Cada regla tiene una acción si falla: rechazar (la fila va a rejects), alertar (se conserva y se anota) o detener (el pipeline se para).

| Capa | Reglas evaluadas | OK | Con hallazgos |
|---|---|---|---|
| bronze | 7 | 6 | 1 |
| silver | 72 | 67 | 5 |
| gold | 30 | 27 | 3 |

**Filas rechazadas en total: 0.** Hallazgos documentados (todos con acción "alertar"):

| Capa | Fuente | Regla | Revisados | Afectados | Acción si falla |
|---|---|---|---|---|---|
| bronze | desempeno_municipal | dos_bloques_misma_vigencia | 246 | 123 | alertar |
| silver | centros_poblados | total_vs_poblacion_dane | 615 | 614 | alertar |
| silver | desempeno | nombre_coherente_con_codigo | 246 | 2 | alertar |
| silver | agricola | cosechada_no_mayor_sembrada | 2613 | 373 | alertar |
| silver | capacidad_uso | clases_ausentes | 8 | 2 | alertar |
| silver | capacidad_uso | geometrias_invalidas_reparadas | 958 | 2 | alertar |
| gold | cultivo_municipio | rendimiento_division_por_cero | 1731 | 56 | alertar |
| gold | suelo | pct_sin_clasificar_mayor_5 | 123 | 7 | alertar |
| gold | integracion | union_pct_rural_sin_vincular_izq | 738 | 123 | alertar |

Particionamiento: no se particiona. La tabla más grande ronda las 210.000 filas y pocos MB; particionar por año crearía archivos de pocos KB sin beneficio de consulta.

### 5.2 Población

`poblacion_dane` es la fuente municipal oficial. El archivo de "centros poblados" son proyecciones por área (cabecera, centros poblados y rural disperso, total); se cargan solo cabecera y rural para no duplicar. Su total difiere de la fuente oficial entre -1.679 y 2.880 personas por municipio-año (mediana 106): son versiones distintas de la proyección y la diferencia se reporta en `outputs/quality/conciliacion_poblacion_fuentes.csv`.

### 5.3 Desempeño municipal

El archivo trae 246 filas para 123 municipios: dos bloques rotulados 2020. En el bloque A, 15022 figura como Aquitania (DANE: Almeida), 15047 figura como Almeida (DANE: Aquitania). Se usó el bloque B, cuyos 123 nombres coinciden con el DANE. Los bloques difieren en promedio 7,0 puntos (máximo 20,6; correlación 0,41); el otro bloque se usó en el análisis de sensibilidad.

### 5.4 Producción agrícola

La EVA 2023 trae 96 cultivos y seis estados físicos. Los periodos A y B se suman por municipio y cultivo; el rendimiento es Σ producción / Σ área cosechada, y con área 0 queda nulo. Las 373 filas con área cosechada mayor que la sembrada se conservaron con una marca, porque en cultivos permanentes es posible. Sumar toneladas de cultivos distintos no representa valor económico.

### 5.5 Análisis espacial

El GeoJSON del IGAC no declara CRS; sus coordenadas están en grados y se asumió EPSG:4326. Se repararon 2 geometrías inválidas. Las áreas y el overlay se calcularon en EPSG:9377 tras disolver el suelo por clase. La simplificación del MGN a 75 m cambia el área municipal en promedio menos de 0,1 %. 7 municipios tienen más de 5 % de su área sin clasificar.

### 5.6 Integración

Uniones LEFT sobre la población (123 municipios × 6 años = 738 filas); el pipeline se detiene si una unión duplica filas o cambia la población total. Registros no vinculados: agricola: 0, desempeno: 0, pct_rural: 123, suelo: 0. Los 123 sin % rural corresponden a 2025, año que la fuente por áreas no cubre. Municipios incluidos: 123 en la hipótesis principal y 123 en la agrícola.

### 5.7 Estadística

Pearson y Spearman con IC 95 % (z de Fisher) y valor p. Shapiro-Wilk: no se rechaza la normalidad de ninguna de las dos variables. Regresión simple y con controles (log de población, % rural, grupo de capacidades); Breusch-Pagan, distancia de Cook y VIF. Sensibilidad sin influyentes, con el otro bloque del MDM y con la otra fuente de población. Holm para las complementarias.

## 6. Resultados

### 6.1 Respuestas a las preguntas de investigación

**1. ¿Cómo se distribuyen la población y los grupos de edad entre los municipios?**

Boyacá pasa de 1.248.977 habitantes en 2020 a 1.290.393 en 2025. La población de 18 a 44 años sube de 38,0 % a 39,3 % del total departamental, y la de 18 a 64 de 59,6 % a 61,4 %. Entre municipios la proporción joven varía mucho: mediana 34,1 %, desde 25,0 % en Guayatá hasta 47,3 % en Cómbita. Es un departamento rural: la mitad de los municipios tiene más de 69 % de su población fuera de la cabecera.

*Evidencia: Pirámide p1, mapa m1, distribución rural p1.*

**2. ¿Cuáles municipios presentan mayor producción y cuáles mayor rendimiento por cultivo?**

La EVA 2023 registra 96 cultivos. Por toneladas dominan caña (2.078.348 t), papa (962.643 t), tomate (183.196 t). La papa, cultivo seleccionado, se reporta en 92 municipios con un rendimiento departamental de 20,7 t/ha; los mayores productores son Siachoque (125.540 t), Saboyá (100.170 t), Ventaquemada (98.742 t). En producción por 1.000 habitantes de 18–64 lideran Chitaraque, San José de Pare, Togüí, pero más del 99 % de su producción es caña: el indicador suma toneladas no comparables (mediana departamental 2.879 t).

*Evidencia: Gráficos p2, mapas m3 y m4, gold/cultivo_municipio.*

**3. ¿Cómo se distribuyen las clases de capacidad de uso de las tierras en cada municipio?**

El 78 % del área es de clases VII y VIII (VIII 41,8 %, VII 36,4 %): tierras con fuertes limitaciones, aptas sobre todo para conservación y uso forestal. Solo el 10,7 % es de clases III–IV, las de menos limitaciones presentes (no hay I ni II). Clase predominante por municipio: VIII en 51, VII en 51, VI en 13, IV en 8. 7 municipios tienen más de 5 % de su área sin clasificar.

*Evidencia: Gráfico p4, mapa m5, gold/suelo_municipio (IGAC 1:100.000, 2004).*

**4. ¿Existe una asociación entre la proporción de población de 18 a 44 años y el desempeño municipal?**

Sí, positiva y débil. Spearman r = 0,24 (IC 95 % 0,06 a 0,40, p = 0,004); Pearson r = 0,25 (IC 0,08 a 0,41, p = 0,002); n = 123. Cada punto porcentual más de población joven se asocia con 0,52 puntos más de MDM (IC 0,16 a 0,88); la proporción joven explica un 6 % de las diferencias. Se rechaza H0 con α = 0,05.

*Evidencia: Dispersión p5, mapas m6 y m7, outputs/stats/h_principal_correlaciones.csv.*

**5. ¿Cómo se relacionan la producción agrícola y la población de 18 a 64 años?**

Asociación positiva moderada: Spearman r = 0,50 (IC 0,35 a 0,63), p ajustado por Holm < 0,001; en escala logarítmica r = 0,42. Los municipios con más población en edad de trabajar producen más toneladas, en buena parte por tamaño. Además, en los 92 municipios con papa, más área de clases III–IV se asocia con mayor rendimiento (r = 0,41, p Holm < 0,001).

*Evidencia: Dispersión p5 (producción vs población), resultados_hipotesis.csv.*

**6. ¿Cómo cambian los resultados al considerar el tamaño poblacional y otras variables?**

La asociación se mantiene en las tres sensibilidades: sin influyentes r = 0,25, con el otro bloque del MDM r = 0,24 y con la otra fuente de población r = 0,23 (todas p < 0,01). Pero con controles (log de población, % rural y grupo de capacidades G1–G5) el coeficiente baja a 0,28 (IC -0,16 a 0,73, p = 0,214) y deja de ser significativo. Los municipios G1, de mayores capacidades, tienen a la vez más población joven y mejor MDM. Por sexo: mujeres de 18–44 r = 0,33 (p Holm < 0,001); hombres r = 0,17 (p Holm 0,059, no significativo).

*Evidencia: outputs/stats/regresion_h_principal_controles_*, tabla de grupos de capacidad.*

### 6.2 Hipótesis principal y complementarias

| Tipo | Análisis | Método | n | r | IC inf. | IC sup. | p | p Holm | Conclusión |
|---|---|---|---|---|---|---|---|---|---|
| principal | principal | pearson | 123 | 0,252 | 0,078 | 0,411 | 0,002 | — | Hay evidencia de asociación positiva |
| principal | principal | spearman | 123 | 0,241 | 0,064 | 0,403 | 0,004 | — | Hay evidencia de asociación positiva |
| principal | sensibilidad_sin_influyentes | pearson | 119 | 0,270 | 0,095 | 0,429 | 0,001 | — | Hay evidencia de asociación positiva |
| principal | sensibilidad_sin_influyentes | spearman | 119 | 0,247 | 0,067 | 0,411 | 0,003 | — | Hay evidencia de asociación positiva |
| principal | sensibilidad_bloque_alterno_mdm | spearman | 123 | 0,242 | 0,065 | 0,404 | 0,004 | — | Hay evidencia de asociación positiva |
| principal | sensibilidad_poblacion_fuente_alterna | spearman | 123 | 0,234 | 0,057 | 0,397 | 0,005 | — | Hay evidencia de asociación positiva |
| exploratoria | A_produccion_vs_pob_18_64 | spearman | 123 | 0,502 | 0,348 | 0,631 | < 0,001 | < 0,001 | Hay evidencia de asociación |
| exploratoria | A_log_produccion_vs_log_pob | pearson | 123 | 0,424 | 0,267 | 0,559 | < 0,001 | < 0,001 | Hay evidencia de asociación |
| exploratoria | B_suelo_iii_iv_vs_rendimiento_papa | spearman | 92 | 0,409 | 0,214 | 0,572 | < 0,001 | < 0,001 | Hay evidencia de asociación |
| exploratoria | D_mujeres_18_44_vs_mdm | spearman | 123 | 0,327 | 0,155 | 0,480 | < 0,001 | < 0,001 | Hay evidencia de asociación |
| exploratoria | D_hombres_18_44_vs_mdm | spearman | 123 | 0,171 | -0,008 | 0,339 | 0,059 | 0,059 | No se rechaza H0 |

Regresión simple: MDM = β0 + β1 · prop_18_44. β1 = 0,522 (IC 0,161 a 0,884), p = 0,005, R² = 0,063.

Regresión con controles (n = 123, R² ajustado = 0,108, errores clasicos, Breusch-Pagan p = 0,188):

| Término | Coeficiente | IC inf. | IC sup. | p |
|---|---|---|---|---|
| Intercept | 37,006 | 16,049 | 57,963 | < 0,001 |
| C(grupo_capacidad)[T.G2] | -4,591 | -8,700 | -0,482 | 0,029 |
| C(grupo_capacidad)[T.G3] | -4,689 | -8,988 | -0,390 | 0,033 |
| C(grupo_capacidad)[T.G4] | -6,926 | -11,580 | -2,272 | 0,004 |
| C(grupo_capacidad)[T.G5] | -18,143 | -33,499 | -2,786 | 0,021 |
| prop_18_44_pct | 0,281 | -0,164 | 0,726 | 0,214 |
| log_poblacion | 0,923 | -1,080 | 2,925 | 0,363 |
| pct_rural | 0,071 | -0,018 | 0,161 | 0,117 |

Grupos de capacidades iniciales del DNP en 2020:

| Grupo | Municipios | MDM medio | % 18–44 medio |
|---|---|---|---|
| G1 | 26 | 59,5 | 37,1 |
| G2 | 36 | 54,3 | 33,8 |
| G3 | 34 | 54,4 | 33,2 |
| G4 | 26 | 52,5 | 33,2 |
| G5 | 1 | 40,4 | 31,0 |

### 6.3 Producción por cultivo

| Cultivo | Estado físico | Producción (t) | Área cosechada (ha) | Rendimiento (t/ha) | Municipios |
|---|---|---|---|---|---|
| Caña | Caña o verde | 2.078.348 | 22.345 | 93,0 | 60 |
| Papa | En fresco | 962.643 | 46.526 | 20,7 | 92 |
| Tomate | En fresco | 183.196 | 2.282 | 80,3 | 51 |
| Cebolla de bulbo | En fresco | 132.727 | 4.846 | 27,4 | 48 |
| Cebolla de rama | En fresco | 91.067 | 2.597 | 35,1 | 7 |
| Zanahoria | En fresco | 53.473 | 2.270 | 23,6 | 24 |
| Pera | En fresco | 37.350 | 1.711 | 21,8 | 10 |
| Yuca | En fresco | 21.519 | 2.149 | 10,0 | 49 |

### 6.4 Capacidad de uso de las tierras (área departamental clasificada)

| Clase | Área (ha) | % del área |
|---|---|---|
| CA | 11.075 | 0,5 |
| III | 47.598 | 2,1 |
| IV | 197.123 | 8,7 |
| V | 13.005 | 0,6 |
| VI | 221.418 | 9,7 |
| VII | 829.240 | 36,4 |
| VIII | 952.651 | 41,8 |
| ZU | 5.003 | 0,2 |

Figuras en `outputs/figures/` y mapas en `outputs/maps/`; también publicados en la página del proyecto (GitHub Pages).

## 7. Limitaciones

- Asociaciones entre municipios en un solo año: no permiten afirmar causalidad ni medir "disposición al cambio".
- Con controles, el efecto de la población joven deja de ser significativo: parte de la asociación la explica el grupo de capacidades.
- MDM 2020 y EVA 2023: años distintos.
- La población es una proyección, no un conteo, y las dos fuentes difieren hasta en 15 % en algún municipio-año.
- El MDM publicado trae dos bloques para la misma vigencia, con correlación de solo 0,41 entre ellos.
- El mapa IGAC es de 2004 a escala 1:100.000: capacidad de uso, no fertilidad actual.
- La producción total suma toneladas no comparables; en los municipios cañeros domina el indicador por habitante.

## 8. Conclusiones y recomendaciones

En 2020, los municipios con mayor proporción de población de 18 a 44 años tienen, en promedio, mejor desempeño municipal: Spearman r = 0,24 (IC 95 % 0,06 a 0,40), p = 0,004, n = 123. Se rechaza H0, pero la asociación es débil. Al controlar por tamaño, % rural y grupo de capacidades, el efecto deja de ser significativo (coeficiente 0,28, IC 95 % -0,16 a 0,73, p = 0,214): buena parte de la asociación la explica el grupo de capacidades iniciales del municipio. No demuestra causalidad ni mide disposición al cambio.

Para estudiar la disposición al cambio o una relación causal se necesitaría medir actitudes directamente (encuestas), contar con un panel de varios años por municipio, incorporar controles como educación, ingreso, migración y transferencias, y un diseño de identificación. También conviene descargar más vigencias del MDM y de la EVA para repetir el análisis en el tiempo.

## 9. Reproducibilidad

`bash run_pipeline.sh` ejecuta los notebooks 01–08 y las pruebas; `python -m src.generar_informe` regenera este informe y `python -m src.publicar_sitio` la página. Versiones en `requirements.txt` y `requirements-lock.txt`. Guía completa en el README del proyecto.
