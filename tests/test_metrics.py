"""Unit tests on small synthetic polygons (no data needed)."""
import geopandas as gpd
import pytest
from shapely.geometry import box

from coastal import metrics


def make_lc():
    """Municipality A, 10x10 km. 1985: urban 1 km² + wetland 99 km²; 2023: urban 5 km² (4 km² on wetland)."""
    rows = [
        (1985, "A", 24, "Urban Area", "Urban", box(0, 0, 1000, 1000)),
        (1985, "A", 11, "Wetland", "Wetland and grassland", box(1000, 0, 10000, 10000)),
        (1985, "A", 11, "Wetland", "Wetland and grassland", box(0, 1000, 1000, 10000)),
        (2023, "A", 24, "Urban Area", "Urban", box(0, 0, 2000, 2500)),
        (2023, "A", 11, "Wetland", "Wetland and grassland", box(2000, 0, 10000, 10000)),
        (2023, "A", 11, "Wetland", "Wetland and grassland", box(0, 2500, 2000, 10000)),
    ]
    g = gpd.GeoDataFrame(rows, columns=["ano", "nm_mun", "class_id", "class_name", "group", "geometry"],
                         geometry="geometry", crs=31982)
    g["area_km2"] = g.geometry.area / 1e6
    g["area_km2_attr"] = g["area_km2"]
    return g


def test_urban_growth():
    g = metrics.urban_growth(make_lc()).set_index("nm_mun")
    assert g.loc["A", "km2_1985"] == pytest.approx(1.0)
    assert g.loc["A", "km2_2023"] == pytest.approx(5.0)
    assert g.loc["A", "growth_pct"] == pytest.approx(400.0)
    assert g.loc["AULINOR (20 municipalities)", "growth_km2"] == pytest.approx(4.0)


def test_land_replaced_traces_new_urban_area_to_1985_cover():
    rep = metrics.land_replaced(make_lc())
    assert rep["area_km2"].sum() == pytest.approx(4.0)  # 1 km² was already urban
    assert set(rep["group"]) == {"Wetland and grassland"}


def test_replaced_shares_sum_to_100():
    shares = metrics.replaced_shares(metrics.land_replaced(make_lc()), focus=["A"])
    assert shares[shares["area"] == "A"]["pct"].sum() == pytest.approx(100.0)
