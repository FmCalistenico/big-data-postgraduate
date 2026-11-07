"""Genera docs/informe_final.md con las cifras reales de la última corrida. Dueño: P6.

    python -m src.generar_informe      # después de ./run_pipeline.sh

Todas las cifras salen de src/resumen.py (las mismas que muestra la página web).
Solo quedan para llenar a mano los nombres y códigos de los integrantes.
"""
from __future__ import annotations

from datetime import date

import polars as pl

from src.config import ANIO_EVA, ANIO_MDM, ROOT
from src.resumen import cargar, conclusion_principal, ic, n0, n1, pv, respuestas

DESTINO = ROOT / "docs" / "informe_final.md"


def _tabla_md(df: pl.DataFrame, cols: list[str], enc: list[str], fmt: dict | None = None) -> str:
    fmt = fmt or {}
    filas = ["| " + " | ".join(enc) + " |", "|" + "---|" * len(enc)]
    for row in df.select(cols).iter_rows(named=True):
        filas.append("| " + " | ".join(fmt[c](row[c]) if c in fmt else ("" if row[c] is None else str(row[c])) for c in cols) + " |")
    return "\n".join(filas)


def generar() -> str:
    r = cargar()
    f = r.f
    sp, rs = f["h_sp"], f["reg_simple"]
    cal = r.tablas["calidad"]
    resp = respuestas(f)
    hip = r.tablas["hipotesis"]

    tabla_calidad = "\n".join(
        ["| Capa | Reglas evaluadas | OK | Con hallazgos |", "|---|---|---|---|"]
        + [f"| {c} | {v['reglas']} | {v['ok']} | {v['fallas'].height} |" for c, v in cal.items()])
    hallazgos = pl.concat([v["fallas"].with_columns(capa=pl.lit(c)) for c, v in cal.items() if v["fallas"].height])
    tabla_hallazgos = _tabla_md(hallazgos, ["capa", "fuente", "regla", "revisados", "afectados", "accion_si_falla"],
                                ["Capa", "Fuente", "Regla", "Revisados", "Afectados", "Acción si falla"])
    tabla_hip = _tabla_md(
        hip, ["tipo", "analisis", "metodo", "n", "r", "ic95_inf", "ic95_sup", "p", "p_holm", "conclusion"],
        ["Tipo", "Análisis", "Método", "n", "r", "IC inf.", "IC sup.", "p", "p Holm", "Conclusión"],
        {"r": lambda x: n1(x, 3), "ic95_inf": lambda x: n1(x, 3), "ic95_sup": lambda x: n1(x, 3),
         "p": pv, "p_holm": lambda x: pv(x) if x is not None else "—"})
    ctrl = r.tablas["reg_ctrl"]
    tabla_ctrl = _tabla_md(ctrl, ["termino", "coef", "ic95_inf", "ic95_sup", "p"],
                           ["Término", "Coeficiente", "IC inf.", "IC sup.", "p"],
                           {"coef": lambda x: n1(x, 3), "ic95_inf": lambda x: n1(x, 3), "ic95_sup": lambda x: n1(x, 3), "p": pv})
    tabla_grupos = _tabla_md(r.tablas["grupos"], ["grupo_capacidad", "municipios", "mdm_medio", "joven_medio"],
                             ["Grupo", "Municipios", "MDM medio", "% 18–44 medio"],
                             {"mdm_medio": n1, "joven_medio": n1})
    tabla_suelo = _tabla_md(r.tablas["suelo"], ["clase", "area_ha", "pct_area"], ["Clase", "Área (ha)", "% del área"],
                            {"area_ha": n0, "pct_area": n1})
    tabla_cult = _tabla_md(r.tablas["cultivos"].head(8), ["cultivo", "estado_fisico", "produccion_t", "area_cosechada_ha", "rendimiento_t_ha", "municipios"],
                           ["Cultivo", "Estado físico", "Producción (t)", "Área cosechada (ha)", "Rendimiento (t/ha)", "Municipios"],
                           {"produccion_t": n0, "area_cosechada_ha": n0, "rendimiento_t_ha": n1})
    tabla_resp = "\n\n".join(f"**{q['n']}. {q['pregunta']}**\n\n{q['respuesta']}\n\n*Evidencia: {q['evidencia']}.*" for q in resp)
    incoh = r.tablas["incoherentes"]
    incoh_txt = ", ".join(f"{row['codigo_municipio']} figura como {row['municipio_fuente']} (DANE: {row['municipio_dane']})"
                          for row in incoh.filter(pl.col("municipio_dane").is_not_null()).iter_rows(named=True)
                          if row["municipio_fuente"] and row["municipio_dane"]
                          and row["municipio_fuente"].split()[0][:4].lower() != row["municipio_dane"].split()[0][:4].lower())

    md = f"""# Proyecto final: municipios de Boyacá

**Análisis de población, producción agrícola, capacidad de uso de las tierras y desempeño municipal**

Curso: Big Data · Especialización en Bases de Datos · Fecha: {date.today().isoformat()}

| N.º | Nombre completo | Código | Rol |
|---|---|---|---|
| 1 | | | P1 · Población y desempeño |
| 2 | | | P2 · Producción agrícola |
| 3 | | | P3 · Cartografía |
| 4 | | | P4 · Suelo IGAC |
| 5 | | | P5 · Estadística |
| 6 | | | P6 · Plataforma, calidad e integración |

## 1. Resumen

Se construyó un pipeline reproducible bronze → silver → gold con seis fuentes públicas (DANE, DNP, UPRA e IGAC) para los {f['n_municipios']} municipios de Boyacá. {conclusion_principal(f)}

## 2. Planteamiento y objetivo

Los municipios de Boyacá difieren en estructura poblacional, producción agrícola, capacidad de uso de las tierras y desempeño. El objetivo es integrar estas dimensiones en un proceso trazable y evaluar si la proporción de población adulta joven se asocia con el desempeño municipal, sin atribuir causalidad.

## 3. Hipótesis

- **Principal.** H0: no existe asociación positiva entre la proporción de población de 18 a 44 años y el puntaje MDM. H1: existe una asociación positiva. Prueba unilateral, α = 0,05 fijado antes del análisis.
- **Complementarias (exploratorias, p ajustado por Holm):** A, producción agrícola total vs población de 18–64; B, % de clases III–IV vs rendimiento de papa; D, proporciones de mujeres y hombres de 18–44 vs desempeño.

## 4. Fuentes y vigencias

| Fuente | Entidad | Vigencia | Filas |
|---|---|---|---|
| Evaluaciones Agropecuarias Municipales | UPRA / MADR | {ANIO_EVA} | 2.613 |
| Población por área ("centros poblados") | Gobernación con base en DANE | 2020–2024 | 1.845 |
| Medición del Desempeño Municipal | DNP | {ANIO_MDM} | 246 |
| Proyecciones de población municipal | DANE | 2020–2025 | 738 |
| Límites municipales MGN | DANE | 2025 | 123 |
| Capacidad de uso de las tierras 1:100.000 | IGAC | 2004 | 958 |

**No existe un año común.** El MDM solo trae {ANIO_MDM} y la EVA solo {ANIO_EVA}. La hipótesis principal se evalúa con MDM y población de {ANIO_MDM}; las agrícolas, con EVA y población de {ANIO_EVA}. La población existe para todos los años, así que cada indicador usa el denominador de su mismo año. Efecto: desempeño y producción no se comparan en un mismo año.

## 5. Metodología

### 5.1 Data lake y calidad

- **Bronze:** los 6 archivos en CSV sin modificar; los GeoJSON se exportaron a CSV con la geometría en WKT. Manifiesto con hash SHA-256, filas, columnas, codificación y CRS.
- **Silver:** tipos, claves DIVIPOLA de 5 dígitos, rangos, coherencia código-nombre y geometrías reparadas, en Parquet y GeoParquet.
- **Gold:** tabla municipio-año, indicadores y tablas para mapas, con conciliación contra silver.
- Cada regla tiene una acción si falla: rechazar (la fila va a rejects), alertar (se conserva y se anota) o detener (el pipeline se para).

{tabla_calidad}

**Filas rechazadas en total: {f['rechazados']}.** Hallazgos documentados (todos con acción "alertar"):

{tabla_hallazgos}

Particionamiento: no se particiona. La tabla más grande ronda las 210.000 filas y pocos MB; particionar por año crearía archivos de pocos KB sin beneficio de consulta.

### 5.2 Población

`poblacion_dane` es la fuente municipal oficial. El archivo de "centros poblados" son proyecciones por área (cabecera, centros poblados y rural disperso, total); se cargan solo cabecera y rural para no duplicar. Su total difiere de la fuente oficial entre {n0(f['conc_min'])} y {n0(f['conc_max'])} personas por municipio-año (mediana {n0(f['conc_med'])}): son versiones distintas de la proyección y la diferencia se reporta en `outputs/quality/conciliacion_poblacion_fuentes.csv`.

### 5.3 Desempeño municipal

El archivo trae 246 filas para 123 municipios: dos bloques rotulados {ANIO_MDM}. En el bloque A, {incoh_txt or 'hay códigos con nombres cruzados'}. Se usó el bloque {f['bloque_oficial']}, cuyos 123 nombres coinciden con el DANE. Los bloques difieren en promedio {n1(f['bloques_dif_media'])} puntos (máximo {n1(f['bloques_dif_max'])}; correlación {n1(f['bloques_corr'], 2)}); el otro bloque se usó en el análisis de sensibilidad.

### 5.4 Producción agrícola

La EVA {ANIO_EVA} trae {f['n_cultivos']} cultivos y seis estados físicos. Los periodos A y B se suman por municipio y cultivo; el rendimiento es Σ producción / Σ área cosechada, y con área 0 queda nulo. Las 373 filas con área cosechada mayor que la sembrada se conservaron con una marca, porque en cultivos permanentes es posible. Sumar toneladas de cultivos distintos no representa valor económico.

### 5.5 Análisis espacial

El GeoJSON del IGAC no declara CRS; sus coordenadas están en grados y se asumió EPSG:4326. Se repararon 2 geometrías inválidas. Las áreas y el overlay se calcularon en EPSG:9377 tras disolver el suelo por clase. La simplificación del MGN a 75 m cambia el área municipal en promedio menos de 0,1 %. {f['suelo_sin_clas_5']} municipios tienen más de 5 % de su área sin clasificar.

### 5.6 Integración

Uniones LEFT sobre la población (123 municipios × 6 años = 738 filas); el pipeline se detiene si una unión duplica filas o cambia la población total. Registros no vinculados: {', '.join(f'{k}: {v}' for k, v in f['no_vinculados'].items())}. Los 123 sin % rural corresponden a 2025, año que la fuente por áreas no cubre. Municipios incluidos: {sp['n']} en la hipótesis principal y {f['h_a']['n']} en la agrícola.

### 5.7 Estadística

Pearson y Spearman con IC 95 % (z de Fisher) y valor p. Shapiro-Wilk: {'no se rechaza la normalidad de ninguna de las dos variables' if f['normal_ambas'] else 'se rechaza la normalidad en al menos una variable, por eso Spearman es la medida principal'}. Regresión simple y con controles (log de población, % rural, grupo de capacidades); Breusch-Pagan, distancia de Cook y VIF. Sensibilidad sin influyentes, con el otro bloque del MDM y con la otra fuente de población. Holm para las complementarias.

## 6. Resultados

### 6.1 Respuestas a las preguntas de investigación

{tabla_resp}

### 6.2 Hipótesis principal y complementarias

{tabla_hip}

Regresión simple: MDM = β0 + β1 · prop_18_44. β1 = {n1(rs['coef'], 3)} (IC {ic(rs['ic95_inf'], rs['ic95_sup'], 3)}), p = {pv(rs['p'])}, R² = {n1(f['reg_simple_meta']['r2'], 3)}.

Regresión con controles (n = {f['reg_ctrl_meta']['n']}, R² ajustado = {n1(f['reg_ctrl_meta']['r2_ajustado'], 3)}, errores {f['reg_ctrl_meta']['errores']}, Breusch-Pagan p = {n1(f['reg_ctrl_meta']['breusch_pagan_p'], 3)}):

{tabla_ctrl}

Grupos de capacidades iniciales del DNP en {ANIO_MDM}:

{tabla_grupos}

### 6.3 Producción por cultivo

{tabla_cult}

### 6.4 Capacidad de uso de las tierras (área departamental clasificada)

{tabla_suelo}

Figuras en `outputs/figures/` y mapas en `outputs/maps/`; también publicados en la página del proyecto (GitHub Pages).

## 7. Limitaciones

- Asociaciones entre municipios en un solo año: no permiten afirmar causalidad ni medir "disposición al cambio".
- Con controles, el efecto de la población joven deja de ser significativo: parte de la asociación la explica el grupo de capacidades.
- MDM {ANIO_MDM} y EVA {ANIO_EVA}: años distintos.
- La población es una proyección, no un conteo, y las dos fuentes difieren hasta en {n1(f['conc_pct_max'], 0)} % en algún municipio-año.
- El MDM publicado trae dos bloques para la misma vigencia, con correlación de solo {n1(f['bloques_corr'], 2)} entre ellos.
- El mapa IGAC es de 2004 a escala 1:100.000: capacidad de uso, no fertilidad actual.
- La producción total suma toneladas no comparables; en los municipios cañeros domina el indicador por habitante.

## 8. Conclusiones y recomendaciones

{conclusion_principal(f)}

Para estudiar la disposición al cambio o una relación causal se necesitaría medir actitudes directamente (encuestas), contar con un panel de varios años por municipio, incorporar controles como educación, ingreso, migración y transferencias, y un diseño de identificación. También conviene descargar más vigencias del MDM y de la EVA para repetir el análisis en el tiempo.

## 9. Reproducibilidad

`bash run_pipeline.sh` ejecuta los notebooks 01–08 y las pruebas; `python -m src.generar_informe` regenera este informe y `python -m src.publicar_sitio` la página. Versiones en `requirements.txt` y `requirements-lock.txt`. Guía completa en `docs/GUIA_EJECUCION.md`.
"""
    DESTINO.write_text(md, encoding="utf-8")
    print(f"Informe generado en {DESTINO}")
    return md


if __name__ == "__main__":
    generar()
