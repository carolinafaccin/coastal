"""The pipeline must reproduce the numbers published in the paper (needs raw_dir; skipped without it)."""
import json

import pytest

from coastal import config, landcover, metrics, population

CFG = config.ROOT / "config.local.json"
pytestmark = pytest.mark.skipif(not CFG.exists(), reason="config.local.json not set")


@pytest.fixture(scope="module")
def data():
    raw_dir = __import__("pathlib").Path(json.loads(CFG.read_text())["raw_dir"])
    aulinor = config.aulinor_dir(raw_dir)
    lc = landcover.load_landcover(aulinor)
    bnd = landcover.load_boundaries(aulinor)
    pop = population.fetch(raw_dir, sorted(bnd["nm_mun"]))
    return aulinor, lc, pop


def test_published_numbers(data):
    _, lc, pop = data
    val = metrics.validate(metrics.urban_growth(lc), metrics.population_growth(pop))
    assert val["ok"].all(), val[~val["ok"]].to_string()


def test_matches_original_workbook(data):
    aulinor, lc, _ = data
    diff, n = metrics.compare_with_workbook(metrics.urban_by_year(lc),
                                            aulinor / "mapbiomas" / "aulinor_analise_mapbiomas_final.xlsx")
    assert n > 100 and diff < 0.05


def test_new_urban_area_is_mostly_traceable(data):
    _, lc, _ = data
    traced = metrics.land_replaced(lc)["area_km2"].sum()
    new = metrics.urban_growth(lc).set_index("nm_mun").loc["AULINOR (20 municipalities)", "growth_km2"]
    assert 0.9 * new <= traced <= new
