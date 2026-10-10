"""Operaciones vectoriales y mapas reproducibles para E08, E09 y E11."""
from pathlib import Path
import json
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import shape, box

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw'
OUT = ROOT / 'salidas'


def leer_vector(nombre):
    ruta = RAW / nombre
    origen = 'zip://' + str(ruta) if ruta.suffix == '.zip' else str(ruta)
    datos = gpd.read_file(origen, engine='pyogrio')
    if not isinstance(datos, gpd.GeoDataFrame):
        raise ValueError(f'{nombre}: fuente tabular sin geometría; leer sus atributos con pandas')
    if datos.crs is None:
        raise ValueError(f'{nombre}: falta CRS; revisar la fuente antes de asignarlo')
    return datos


def reparar(datos):
    datos = datos.copy()
    if datos.geometry.isna().any() or datos.geometry.is_empty.any():
        raise ValueError('Hay geometrías ausentes o vacías; revisar antes de intersectar')
    invalidas = int((~datos.geometry.is_valid).sum())
    datos.geometry = datos.geometry.make_valid()
    return datos, invalidas


def intersecciones():
    """Recorta cada muestra IGAC; conserva atributos y registra reparaciones."""
    OUT.mkdir(parents=True, exist_ok=True)
    municipios, reparadas = reparar(leer_vector('dane_municipios.zip'))
    campo = next(c for c in municipios if c.lower() == 'mpio_cdpmp')
    municipios['codigo_municipio'] = municipios[campo].astype('string').str.zfill(5)
    municipios = municipios[['codigo_municipio', 'geometry']].to_crs(4326)
    reparaciones = {'municipios': reparadas}
    productos = []
    for tema in ['igac_capacidad', 'igac_quimica']:
        muestra, n = reparar(leer_vector(tema + '.json'))
        reparaciones[tema] = n
        muestra = muestra.to_crs(municipios.crs)
        # Mantener la geometría de recorte histórica; proyectar para medir áreas.
        recorte = gpd.overlay(muestra, municipios, how='intersection', keep_geom_type=False)
        recorte['area_interseccion_ha'] = recorte.to_crs(9377).area / 10000
        recorte = recorte.loc[recorte.area_interseccion_ha > 0].copy()
        recorte['tema'] = tema
        recorte = recorte.rename(columns={'OBJECTID': 'objectid'})
        recorte['alcance'] = 'muestra_de_5_poligonos'
        productos.append(recorte)
    resultado = gpd.GeoDataFrame(pd.concat(productos, ignore_index=True), crs=municipios.crs)
    columnas = ['tema','codigo_municipio','objectid','area_interseccion_ha','alcance']
    resultado[columnas].to_csv(OUT / 'intersecciones_muestra.csv', index=False)
    resultado[columnas + ['geometry']].to_file(OUT / 'intersecciones_muestra.geojson', driver='GeoJSON')
    resultado.to_file(OUT / 'intersecciones_muestra.gpkg', layer='intersecciones', driver='GPKG', mode='w')
    control = {'municipios_leidos': len(municipios), 'intersecciones': len(resultado),
               'crs_area': 'EPSG:9377', 'geometrias_reparadas': reparaciones,
               'limitacion': 'No representa cobertura nacional ni municipal completa.'}
    (OUT / 'control_geografico.json').write_text(json.dumps(control, ensure_ascii=False, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    for ax, (tema, color) in zip(axes, [('igac_capacidad', 'steelblue'), ('igac_quimica', 'teal')]):
        parte = resultado.loc[resultado.tema.eq(tema)]
        parte.plot(ax=ax, color=color, edgecolor='white', linewidth=.4)
        limites = ax.axis()
        municipios.loc[municipios.codigo_municipio.isin(parte.codigo_municipio)].boundary.plot(ax=ax, color='grey', linewidth=.6)
        ax.axis(limites)
        ax.set_title(tema.replace('igac_', '').replace('_', ' ').capitalize())
        ax.set_xlabel('Longitud'); ax.set_ylabel('Latitud')
    fig.suptitle('IGAC: muestra de cinco polígonos por tema\nIntersecciones con municipios; WGS84; escalas distintas por panel')
    fig.tight_layout(); fig.savefig(OUT / 'mapa_intersecciones.png', dpi=160); plt.close(fig)
    print(control)
    return resultado


def mapa_suelo():
    import numpy as np
    import rasterio
    from rasterio.plot import show
    with rasterio.open(RAW / 'soilgrids.tif') as src:
        valores = src.read(1, masked=True).astype(float)
        ph = np.ma.masked_where((valores <= 0) | (valores > 140), valores) / 10
        fig, ax = plt.subplots(figsize=(8, 6))
        show(ph, transform=src.transform, ax=ax, cmap='viridis')
        fig.colorbar(ax.images[0], ax=ax, label='pH (valor / 10)')
        perfiles = leer_vector('wosis.json').to_crs(src.crs)
        dentro = perfiles.geometry.intersects(box(*src.bounds))
        if dentro.any(): perfiles.loc[dentro].plot(ax=ax, color='red', markersize=15)
        perfiles.drop(columns='geometry').to_csv(OUT / 'perfiles_wosis.csv', index=False)
        ax.set_title(f'SoilGrids: recorte de pH; ceros pendientes\n{int(dentro.sum())} horizontes WoSIS dentro del recorte; CRS {src.crs}')
        fig.tight_layout(); fig.savefig(OUT / 'mapa_suelo.png', dpi=160); plt.close(fig)


def mapa_clima():
    import numpy as np
    import rasterio
    from rasterio.plot import show
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds
    with rasterio.open(RAW / 'chirps.tif') as src:
        bounds = transform_bounds('EPSG:4326', src.crs, -73.4, 5.5, -73.3, 5.6)
        ventana = from_bounds(*bounds, transform=src.transform).round_offsets().round_lengths()
        lluvia = src.read(1, window=ventana, masked=True)
        lluvia = np.ma.masked_where(lluvia < 0, lluvia)
        fig, ax = plt.subplots(figsize=(8, 6))
        show(lluvia, transform=src.window_transform(ventana), ax=ax, cmap='Blues')
        fig.colorbar(ax.images[0], ax=ax, label='Precipitación mensual (mm)')
        nasa = json.loads((RAW / 'nasa.json').read_text())
        punto = gpd.GeoDataFrame({'fuente':['NASA POWER']}, geometry=[shape(nasa['geometry'])], crs=4326).to_crs(src.crs)
        punto.plot(ax=ax, color='red', markersize=35, label='Punto NASA'); ax.legend()
        ax.set_title(f'CHIRPS: recorte demostrativo, enero 2025\nSoportes distintos de NASA; CRS {src.crs}')
        fig.tight_layout(); fig.savefig(OUT / 'mapa_clima.png', dpi=160); plt.close(fig)
