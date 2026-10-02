"""Load the MapBiomas land-cover polygons (one file per year, dissolved by class and municipality)."""
import geopandas as gpd
import pandas as pd

from .classes import CLASSES
from .config import YEARS


def load_landcover(aulinor):
    """All years in one GeoDataFrame (EPSG:31982, SIRGAS 2000 / UTM 22S).

    Columns: ano, nm_mun, class_id, class_name, group, area_km2 (computed from the
    geometry), area_km2_attr (value stored in the source file, kept for QA).
    """
    frames = []
    for year in YEARS:
        path = aulinor / "mapbiomas" / "aulinor_mapbiomas_shp" / f"aulinor_mapbiomas_{year}_pol.shp"
        g = gpd.read_file(path)
        g["ano"] = year
        frames.append(g)
    g = pd.concat(frames, ignore_index=True)
    g = gpd.GeoDataFrame(g, geometry="geometry", crs=frames[0].crs)
    # Six of the yearly files carry leftover pieces from the GIS dissolve: polygons without a
    # class (inside the municipalities, never overlapping a classified polygon) and polygons
    # without a municipality (offshore slivers). Neither can be urban, so they are dropped here
    # and show up as "unclassified" area in the coverage QA (metrics.qa_coverage).
    g = g[g["class"].notna() & g["nm_mun"].notna()].copy()
    g["class_id"] = g["class"].astype(int)
    unknown = set(g["class_id"]) - set(CLASSES)
    if unknown:
        raise ValueError(f"MapBiomas classes missing from classes.py: {sorted(unknown)}")
    g["class_name"] = g["class_id"].map(lambda c: CLASSES[c][0])
    g["group"] = g["class_id"].map(lambda c: CLASSES[c][1])
    g["area_km2_attr"] = g["area_km2"]
    g["area_km2"] = g.geometry.area / 1e6
    return g[["ano", "nm_mun", "class_id", "class_name", "group", "area_km2", "area_km2_attr", "geometry"]]


def load_boundaries(aulinor):
    """Municipal boundaries of the 20 AULINOR municipalities."""
    return gpd.read_file(aulinor / "limites" / "aulinor_municipios_pol.shp")[["nm_mun", "geometry"]]
