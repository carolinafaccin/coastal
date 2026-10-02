"""COASTAL pipeline: MapBiomas polygons + IBGE census -> tables, spatial files and figures.

    python pipeline.py                       # everything
    python pipeline.py --only tables         # tables, spatial files and validation
    python pipeline.py --only figures docs   # redraw figures and copy the README ones
    python pipeline.py --refresh-population  # download the IBGE population again

Inputs come from raw_dir and outputs go to data_dir, both set in config.local.json.
"""
import argparse
import shutil
import sys
from pathlib import Path

import geopandas as gpd

sys.path.insert(0, str(Path(__file__).parent / "src"))

from coastal import config, figures, landcover, metrics, population, style  # noqa: E402

README_FIGURES = ["urban_timeline", "urban_growth", "landcover_change", "land_replaced", "map_urban_expansion"]


def run_tables(raw_dir, data_dir, aulinor, refresh):
    t = data_dir / "tables"
    lc = landcover.load_landcover(aulinor)
    bnd = landcover.load_boundaries(aulinor)
    print(f"land cover: {len(lc)} polygons, {lc['ano'].nunique()} years, {lc['nm_mun'].nunique()} municipalities")

    metrics.area_by_class(lc).to_csv(t / "landcover_area_by_class.csv", index=False)
    metrics.urban_by_year(lc).round(4).to_csv(t / "urban_area_by_year.csv")
    growth = metrics.urban_growth(lc)
    growth.round(4).to_csv(t / "urban_growth_1985_2023.csv", index=False)
    metrics.qa_coverage(lc, bnd).round(3).to_csv(t / "qa_coverage.csv", index=False)

    replaced = metrics.land_replaced(lc)
    replaced.round(4).to_csv(t / "land_replaced_by_urban.csv", index=False)
    metrics.replaced_shares(replaced).round(3).to_csv(t / "land_replaced_shares.csv", index=False)

    pop = population.fetch(raw_dir, sorted(bnd["nm_mun"]), refresh=refresh)
    pop.to_csv(t / "population_census.csv", index=False)
    pop_growth = metrics.population_growth(pop)
    pop_growth.round(3).to_csv(t / "population_growth.csv", index=False)

    exp = metrics.urban_expansion(lc)
    out = data_dir / "spatial" / "aulinor_urban_expansion.gpkg"
    out.unlink(missing_ok=True)
    for layer, geom in exp.items():
        gpd.GeoDataFrame(geometry=geom).to_file(out, layer=layer, driver="GPKG")

    val = metrics.validate(growth, pop_growth)
    max_diff, n = metrics.compare_with_workbook(metrics.urban_by_year(lc),
                                                aulinor / "mapbiomas" / "aulinor_analise_mapbiomas_final.xlsx")
    val.loc[len(val)] = {"check": f"Urban area vs original workbook, {n} municipality-years (max diff km²)",
                         "published": 0.0, "computed": round(float(max_diff), 3), "tolerance": 0.05,
                         "ok": max_diff <= 0.05}
    val.to_csv(t / "validation.csv", index=False)
    for _, r in val.iterrows():
        print(f"  {'ok ' if r['ok'] else 'FAIL'} {r['check']}: published {r['published']}, computed {r['computed']}")
    return val["ok"].all()


def run_figures(data_dir, aulinor):
    style.setup()
    f = data_dir / "figures"
    t = data_dir / "tables"
    lc = landcover.load_landcover(aulinor)
    bnd = landcover.load_boundaries(aulinor)
    growth = metrics.urban_growth(lc)
    replaced = metrics.land_replaced(lc)
    shares = metrics.replaced_shares(replaced)
    km2 = {"AULINOR": replaced["area_km2"].sum()}
    km2.update({m: replaced.loc[replaced["nm_mun"] == m, "area_km2"].sum() for m in config.FOCUS})

    figures.urban_timeline(lc, growth, f / "urban_timeline.png")
    figures.urban_growth(growth, f / "urban_growth.png")
    figures.landcover_change(lc, f / "landcover_change.png")
    figures.land_replaced(shares, km2, f / "land_replaced.png")
    figures.map_landcover(lc, bnd, f / "map_landcover.png")
    figures.map_urban_expansion(lc, bnd, metrics.urban_expansion(lc), f / "map_urban_expansion.png")
    print(f"figures written to {f}")


def run_docs(data_dir):
    dest = Path(__file__).parent / "docs" / "img"
    dest.mkdir(parents=True, exist_ok=True)
    for name in README_FIGURES:
        shutil.copy(data_dir / "figures" / f"{name}.png", dest / f"{name}.png")
    print(f"copied {len(README_FIGURES)} figures to {dest}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--only", nargs="+", choices=["tables", "figures", "docs"])
    p.add_argument("--refresh-population", action="store_true")
    args = p.parse_args()
    steps = args.only or ["tables", "figures", "docs"]

    raw_dir, data_dir = config.load()
    aulinor = config.aulinor_dir(raw_dir)
    ok = True
    if "tables" in steps:
        ok = run_tables(raw_dir, data_dir, aulinor, args.refresh_population)
    if "figures" in steps:
        run_figures(data_dir, aulinor)
    if "docs" in steps:
        run_docs(data_dir)
    if not ok:
        sys.exit("validation failed: computed values differ from the published ones (see tables/validation.csv)")


if __name__ == "__main__":
    main()
