"""Land-cover and urbanization metrics, plus checks against the numbers published in the paper."""
import geopandas as gpd
import pandas as pd

from .classes import GROUPS, SENSITIVE, URBAN
from .config import FOCUS


def area_by_class(lc):
    """Area (km²) by year, municipality and class."""
    return (lc.groupby(["ano", "nm_mun", "class_id", "class_name", "group"], as_index=False)["area_km2"].sum())


def area_by_group(lc, municipalities=None):
    """Area (km²) by year and group, for all municipalities or a subset (wide table)."""
    d = lc if municipalities is None else lc[lc["nm_mun"].isin(municipalities)]
    wide = d.pivot_table(index="ano", columns="group", values="area_km2", aggfunc="sum", fill_value=0)
    return wide.reindex(columns=list(GROUPS), fill_value=0)


def urban_by_year(lc):
    """Urban area (km²) by municipality (rows) and year (columns)."""
    u = lc[lc["class_id"] == URBAN]
    return u.pivot_table(index="nm_mun", columns="ano", values="area_km2", aggfunc="sum", fill_value=0)


def urban_growth(lc, start=1985, end=2023):
    """Urban area at the start and end of the series, absolute and relative growth."""
    t = urban_by_year(lc)
    out = pd.DataFrame({"km2_start": t[start], "km2_end": t[end]})
    out["growth_km2"] = out["km2_end"] - out["km2_start"]
    out["growth_pct"] = (out["growth_km2"] / out["km2_start"].where(out["km2_start"] > 0)) * 100
    out = out.rename(columns={"km2_start": f"km2_{start}", "km2_end": f"km2_{end}"})
    total = out.sum(numeric_only=True)
    total["growth_pct"] = total["growth_km2"] / total[f"km2_{start}"] * 100
    out.loc["AULINOR (20 municipalities)"] = total
    return out.sort_values(f"km2_{end}", ascending=False).reset_index(names="nm_mun")


def urban_expansion(lc, start=1985, end=2023):
    """Geometries of urban area at `start`, at `end`, and of the new urban area (end minus start)."""
    def urban(year):
        u = lc[(lc["ano"] == year) & (lc["class_id"] == URBAN)]
        return gpd.GeoSeries([u.geometry.union_all()], crs=lc.crs)
    u0, u1 = urban(start), urban(end)
    return {f"urban_{start}": u0, f"urban_{end}": u1, "urban_new": u1.difference(u0)}


def land_replaced(lc, start=1985, end=2023):
    """What the new urban area replaced: `end` urban polygons overlaid on `start` land cover.

    Returns km² by municipality and start-year class/group, excluding land that was
    already urban at `start`.
    """
    urb_end = lc[(lc["ano"] == end) & (lc["class_id"] == URBAN)][["nm_mun", "geometry"]]
    before = lc[(lc["ano"] == start) & (lc["class_id"] != URBAN)][["nm_mun", "class_name", "group", "geometry"]]
    inter = gpd.overlay(urb_end, before, how="intersection", keep_geom_type=True)
    inter = inter[inter["nm_mun_1"] == inter["nm_mun_2"]].copy()
    inter["area_km2"] = inter.geometry.area / 1e6
    out = (inter.rename(columns={"nm_mun_1": "nm_mun"})
                .groupby(["nm_mun", "class_name", "group"], as_index=False)["area_km2"].sum())
    return out


def replaced_shares(replaced, focus=FOCUS):
    """Share of the new urban area by previous group, for AULINOR and each focus municipality."""
    parts = {"AULINOR": replaced}
    parts.update({m: replaced[replaced["nm_mun"] == m] for m in focus})
    rows = []
    for name, d in parts.items():
        total = d["area_km2"].sum()
        g = d.groupby("group")["area_km2"].sum().reindex(list(GROUPS), fill_value=0)
        for group, km2 in g.items():
            rows.append({"area": name, "group": group, "km2": km2, "pct": km2 / total * 100,
                         "sensitive": group in SENSITIVE})
    return pd.DataFrame(rows)


def qa_coverage(lc, boundaries):
    """Area covered by classified polygons vs. the municipal boundaries, per year.

    The gap is land that the yearly polygon files leave unclassified (e.g. pixels not observed
    by the satellite); it varies by year and is reported, not filled. Also reports the largest
    difference between each polygon's computed area and the area stored in the source file.
    """
    total = boundaries.geometry.area.sum() / 1e6
    g = lc.assign(gap=(lc["area_km2"] - lc["area_km2_attr"]).abs())
    out = g.groupby("ano").agg(classified_km2=("area_km2", "sum"),
                               max_polygon_gap_km2=("gap", "max")).reset_index()
    out["boundary_km2"] = total
    out["unclassified_km2"] = total - out["classified_km2"]
    out["unclassified_pct"] = out["unclassified_km2"] / total * 100
    return out[["ano", "boundary_km2", "classified_km2", "unclassified_km2", "unclassified_pct",
                "max_polygon_gap_km2"]]


def compare_with_workbook(urban_table, workbook):
    """Compare urban area by municipality and year with the original analysis workbook.

    `workbook` is aulinor_analise_mapbiomas_final.xlsx (sheet `area_urb_p_ano`). Returns the
    largest absolute difference (km²) and the number of municipality-years compared.
    """
    w = pd.read_excel(workbook, sheet_name="area_urb_p_ano", header=1)
    w = w.rename(columns={"nm_mun": "nm_mun"}).set_index("nm_mun")
    diffs = []
    for year in urban_table.columns:
        col = f"{year}_km2"
        if col not in w.columns:
            continue
        for mun, ref in w[col].dropna().items():
            if mun in urban_table.index:
                diffs.append(abs(urban_table.loc[mun, year] - ref))
    return (max(diffs) if diffs else float("nan")), len(diffs)


def population_growth(pop):
    """Population by census and growth between censuses."""
    wide = pop.pivot(index="nm_mun", columns="ano", values="pop")
    wide["ratio_1991_2022"] = wide[2022] / wide[1991]
    wide["growth_pct_2010_2022"] = (wide[2022] / wide[2010] - 1) * 100
    return wide.reset_index()


# Numbers published in the paper / used in the maps of the project page
def validate(growth, pop_growth):
    """Compare computed values with published ones. Returns a DataFrame with an `ok` flag."""
    g = growth.set_index("nm_mun")
    total = g.loc["AULINOR (20 municipalities)"]
    checks = [
        ("AULINOR urban area 1985 (km²)", 112, total["km2_1985"], 1.0),
        ("AULINOR urban area 2023 (km²)", 180, total["km2_2023"], 1.0),
        ("AULINOR urban growth (%)", 60, total["growth_pct"], 1.5),
        ("Imbé urban growth (%)", 17.1, g.loc["Imbé", "growth_pct"], 0.2),
        ("Imbé urban growth (km²)", 2.6, g.loc["Imbé", "growth_km2"], 0.1),
        ("Tramandaí urban growth (%)", 26.2, g.loc["Tramandaí", "growth_pct"], 0.2),
        ("Tramandaí urban growth (km²)", 4.7, g.loc["Tramandaí", "growth_km2"], 0.1),
        ("Osório urban growth (%)", 79, g.loc["Osório", "growth_pct"], 0.5),
    ]
    if pop_growth is not None:
        p = pop_growth.set_index("nm_mun")
        checks.append(("Imbé population, 2022 / 1991", 3.6, p.loc["Imbé", "ratio_1991_2022"], 0.1))
    return pd.DataFrame([{"check": c, "published": pub, "computed": round(float(val), 2),
                          "tolerance": tol, "ok": abs(float(val) - pub) <= tol}
                         for c, pub, val, tol in checks])
