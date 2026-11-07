"""Genera un sitio web estático con los resultados del pipeline, listo para GitHub Pages.

    python -m src.publicar_sitio        # después de ./run_pipeline.sh

Lee outputs/ y data_lake/bronze/manifest_bronze.json y escribe:
    site/index.html     página única con fuentes, calidad, hipótesis, figuras y mapas
    site/img/*.png      copias de las figuras y mapas
    site/.nojekyll      para que GitHub sirva los archivos tal cual

No ejecuta ningún análisis: solo presenta lo que el pipeline ya produjo.
Si falta un archivo, la sección correspondiente dice "pendiente" en vez de fallar.
"""
from __future__ import annotations

import html
import json
import shutil
from datetime import datetime

import polars as pl

from src.config import ANIO_EVA, ANIO_MDM, BRONZE, FIGURES, MAPS, QUALITY, ROOT, STATS

SITE = ROOT / "site"

TITULOS = {
    "p1_piramide": "Población por edad y sexo",
    "p1_distribucion_rural": "Población rural por municipio",
    "p2_produccion_rendimiento_cultivos": "Producción y rendimiento por cultivo",
    "p2_produccion_por_1000": "Producción por 1.000 habitantes de 18–64 años",
    "p4_distribucion_clases": "Clases de capacidad de uso de las tierras",
    "p5_dispersion_joven_mdm": "Población joven vs desempeño municipal",
    "p5_dispersion_produccion_poblacion": "Producción vs población de 18–64 años",
    "m1_poblacion_joven": "Mapa: población de 18–44 años",
    "m2_desempeno": "Mapa: desempeño municipal",
    "m3_rendimiento_papa": "Mapa: rendimiento de papa",
    "m4_produccion_por_1000": "Mapa: producción por 1.000 habitantes",
    "m5_clase_predominante": "Mapa: clase de suelo predominante",
    "m6_bivariado_joven_mdm": "Mapa bivariado: joven × desempeño",
    "m7_lado_a_lado": "Mapas lado a lado: joven y desempeño",
}


def _e(x) -> str:
    return html.escape("" if x is None else str(x))


def _num(x, dec: int = 3) -> str:
    if x is None:
        return "—"
    try:
        return f"{float(x):.{dec}f}"
    except (TypeError, ValueError):
        return _e(x)


def _tabla(df: pl.DataFrame, columnas: list[str], encabezados: list[str], decimales: dict | None = None) -> str:
    decimales = decimales or {}
    cab = "".join(f"<th>{_e(h)}</th>" for h in encabezados)
    filas = []
    for fila in df.select([c for c in columnas if c in df.columns]).iter_rows(named=True):
        celdas = []
        for c in columnas:
            v = fila.get(c)
            celdas.append(f"<td>{_num(v, decimales[c]) if c in decimales else _e(v)}</td>")
        filas.append("<tr>" + "".join(celdas) + "</tr>")
    return f'<div class="tabla"><table><thead><tr>{cab}</tr></thead><tbody>{"".join(filas)}</tbody></table></div>'


def _pendiente(que: str) -> str:
    return f'<p class="pendiente">Pendiente: {_e(que)}. Ejecute <code>./run_pipeline.sh</code> y vuelva a generar el sitio.</p>'


# ------------------------------------------------------------------ secciones

def seccion_fuentes() -> str:
    ruta = BRONZE / "manifest_bronze.json"
    if not ruta.exists():
        return _pendiente("manifiesto de bronze")
    m = json.loads(ruta.read_text(encoding="utf-8"))
    df = pl.DataFrame([{k: f.get(k) for k in ("fuente", "entidad", "filas", "columnas", "crs", "fecha_descarga")}
                       for f in m["fuentes"]])
    return _tabla(df, ["fuente", "entidad", "filas", "columnas", "crs", "fecha_descarga"],
                  ["Fuente", "Entidad", "Filas", "Columnas", "CRS", "Descarga"])


def seccion_calidad() -> str:
    partes = []
    resumen = []
    for capa in ("bronze", "silver", "gold"):
        ruta = QUALITY / f"metricas_{capa}.csv"
        if not ruta.exists():
            continue
        m = pl.read_csv(ruta)
        resumen.append({"capa": capa, "reglas": m.height,
                        "ok": m.filter(pl.col("resultado") == "OK").height,
                        "fallas": m.filter(pl.col("resultado") == "FALLA").height})
        fallas = m.filter(pl.col("resultado") == "FALLA")
        if fallas.height:
            accion = "accion_si_falla" if "accion_si_falla" in fallas.columns else "accion"
            partes.append(f"<h3>Reglas con hallazgos en {capa}</h3>" + _tabla(
                fallas, ["fuente", "regla", "descripcion", "revisados", "afectados", accion],
                ["Fuente", "Regla", "Descripción", "Revisados", "Afectados", "Acción si falla"]))
    if not resumen:
        return _pendiente("métricas de calidad")
    intro = ('<p>Cada regla se aplica fila a fila. <b>Rechazar</b> saca la fila a la zona de rechazos; '
             '<b>alertar</b> la conserva y la anota; <b>detener</b> para el pipeline. Una falla con '
             'acción "alertar" es una anomalía documentada, no un dato perdido.</p>')
    return intro + _tabla(pl.DataFrame(resumen), ["capa", "reglas", "ok", "fallas"],
                          ["Capa", "Reglas evaluadas", "OK", "Con hallazgos"]) + "".join(partes)


def seccion_hipotesis() -> str:
    ruta = STATS / "resultados_hipotesis.csv"
    if not ruta.exists():
        ruta = STATS / "h_principal_correlaciones.csv"
    if not ruta.exists():
        return _pendiente("resultados estadísticos")
    r = pl.read_csv(ruta)
    cols = ["tipo", "analisis", "metodo", "n", "r", "ic95_inf", "ic95_sup", "p", "p_holm", "conclusion"]
    cols = [c for c in cols if c in r.columns]
    enc = {"tipo": "Tipo", "analisis": "Análisis", "metodo": "Método", "n": "n", "r": "r",
           "ic95_inf": "IC 95 % inf.", "ic95_sup": "IC 95 % sup.", "p": "p", "p_holm": "p (Holm)",
           "conclusion": "Conclusión"}
    texto = (f'<p><b>Hipótesis principal ({ANIO_MDM}).</b> H0: no hay asociación positiva entre la proporción '
             f'de población de 18 a 44 años y el puntaje de desempeño municipal. Prueba unilateral, α = 0,05. '
             f'Las complementarias ({ANIO_EVA}) son exploratorias y se ajustan por Holm.</p>'
             '<p class="nota">Una asociación entre municipios en un solo año no demuestra causalidad '
             'ni mide "disposición al cambio".</p>')
    return texto + _tabla(r, cols, [enc[c] for c in cols],
                          {c: 3 for c in ("r", "ic95_inf", "ic95_sup", "p", "p_holm")})


def _galeria(carpeta, prefijo_img: str) -> str:
    imgs = sorted(carpeta.glob("*.png")) if carpeta.exists() else []
    if not imgs:
        return _pendiente(f"imágenes de {carpeta.name}")
    destino = SITE / "img"
    destino.mkdir(parents=True, exist_ok=True)
    tarjetas = []
    for p in imgs:
        nombre = f"{prefijo_img}_{p.name}"
        shutil.copy2(p, destino / nombre)
        clave = next((k for k in TITULOS if p.stem.startswith(k)), None)
        titulo = TITULOS.get(clave, p.stem.replace("_", " "))
        tarjetas.append(f'<figure><a href="img/{_e(nombre)}" target="_blank">'
                        f'<img src="img/{_e(nombre)}" alt="{_e(titulo)}" loading="lazy"></a>'
                        f'<figcaption>{_e(titulo)}</figcaption></figure>')
    return f'<div class="galeria">{"".join(tarjetas)}</div>'


# ------------------------------------------------------------------ página

CSS = """
:root{--bg:#fbfaf7;--fg:#1d2328;--muted:#5d6670;--line:#e3e0d8;--card:#fff;--accent:#2e6f8e;--warn:#9a5b13}
@media (prefers-color-scheme:dark){:root{--bg:#14181b;--fg:#e8e6e1;--muted:#9aa3ab;--line:#2c3338;--card:#1b2024;--accent:#7fb7d1;--warn:#e0a85a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
header,main,footer{max-width:1100px;margin:0 auto;padding:0 16px}
header{padding-top:40px;padding-bottom:8px}h1{font-size:1.9rem;line-height:1.2;margin:0 0 8px}
.sub{color:var(--muted);margin:0}nav{display:flex;flex-wrap:wrap;gap:6px 14px;margin:20px 0 0;font-size:.95rem}
nav a{color:var(--accent);text-decoration:none}nav a:hover{text-decoration:underline}
section{padding:28px 0;border-top:1px solid var(--line)}h2{font-size:1.35rem;margin:0 0 12px}h3{font-size:1.05rem;margin:22px 0 8px}
.tabla{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:.88rem}th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font-weight:600;background:color-mix(in srgb,var(--line) 45%,transparent)}tbody tr:last-child td{border-bottom:0}
.galeria{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px}
figure img{width:100%;height:auto;display:block;border-radius:4px;background:#fff}figcaption{font-size:.9rem;color:var(--muted);margin-top:6px}
.pendiente{color:var(--warn)}.nota{color:var(--muted);font-size:.92rem}code{font-size:.9em}
.flujo{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.85rem;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto;white-space:pre}
footer{color:var(--muted);font-size:.85rem;padding-top:20px;padding-bottom:40px;border-top:1px solid var(--line)}
"""

FLUJO = ("staging/ (6 originales)\n"
         "  └─▶ BRONZE  CSV sin modificar + manifiesto con hash\n"
         "        └─▶ SILVER  datos tipados y validados (Parquet / GeoParquet) + rechazos + métricas\n"
         "              └─▶ GOLD  tabla municipio-año + maestro con geometría\n"
         "                    └─▶ estadística, figuras y mapas")


def generar() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    secciones = [
        ("arquitectura", "Arquitectura", f'<p>Pipeline reproducible con arquitectura medallón.</p>'
                                         f'<div class="flujo">{_e(FLUJO)}</div>'),
        ("fuentes", "Fuentes (capa bronze)", seccion_fuentes()),
        ("calidad", "Calidad de datos por capa", seccion_calidad()),
        ("hipotesis", "Hipótesis y resultados", seccion_hipotesis()),
        ("figuras", "Gráficos", _galeria(FIGURES, "fig")),
        ("mapas", "Mapas municipales", _galeria(MAPS, "map")),
        ("limitaciones", "Limitaciones",
         "<ul><li>No hay un año común: el desempeño es de 2020 y la producción de 2023.</li>"
         "<li>La población es una proyección del DANE, no un conteo.</li>"
         "<li>El archivo de desempeño publica dos bloques para la misma vigencia.</li>"
         "<li>El mapa del IGAC es de 2004, escala 1:100.000: capacidad de uso, no fertilidad actual.</li>"
         "<li>La producción total suma toneladas de cultivos no comparables.</li></ul>"),
    ]
    nav = "".join(f'<a href="#{i}">{_e(t)}</a>' for i, t, _ in secciones)
    cuerpo = "".join(f'<section id="{i}"><h2>{_e(t)}</h2>{c}</section>' for i, t, c in secciones)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    pagina = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Boyacá: resultados del proyecto</title>
<meta name="description" content="Población, producción agrícola, suelo y desempeño de los 123 municipios de Boyacá">
<style>{CSS}</style></head><body>
<header><h1>Municipios de Boyacá: población, agricultura, suelo y desempeño</h1>
<p class="sub">Proyecto final · Electiva Big Data · resultados generados el {fecha}</p><nav>{nav}</nav></header>
<main>{cuerpo}</main>
<footer>Fuentes: DANE, DNP, UPRA y IGAC vía datos.gov.co. Sitio generado con <code>python -m src.publicar_sitio</code>
a partir de las salidas del pipeline.</footer></body></html>"""
    (SITE / "index.html").write_text(pagina, encoding="utf-8")
    print(f"Sitio generado en {SITE / 'index.html'}")


if __name__ == "__main__":
    generar()
