"""Census population by municipality (IBGE, SIDRA API).

Raw responses are saved in raw_dir under ibge/censo/populacao_municipal_sidra/t0/
(with a download manifest in _docs/) and re-used on later runs.
"""
import json
import unicodedata
from datetime import date

import pandas as pd
import requests

API = "https://servicodados.ibge.gov.br/api"
HEADERS = {"User-Agent": "coastal/0.1 (github.com/carolinafaccin/coastal)"}
# table 200: Censos 1991, 2000, 2010 | table 4714: Censo 2022 (variable 93 = resident population)
TABLES = {"200_1991-2010": (200, "1991|2000|2010"), "4714_2022": (4714, "2022")}
PRODUCT = "ibge/censo/populacao_municipal_sidra"


def _norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def municipality_codes(names):
    """IBGE codes of the given RS municipalities (matched by accent-free name)."""
    r = requests.get(f"{API}/v1/localidades/estados/43/municipios", headers=HEADERS, timeout=60)
    r.raise_for_status()
    by_name = {_norm(m["nome"]): str(m["id"]) for m in r.json()}
    missing = [n for n in names if _norm(n) not in by_name]
    if missing:
        raise ValueError(f"Municipalities not found in IBGE list: {missing}")
    return {n: by_name[_norm(n)] for n in names}


def fetch(raw_dir, names, refresh=False):
    """Download (or read from raw_dir) the SIDRA responses; return the tidy table."""
    t0 = raw_dir / PRODUCT / "t0"
    docs = raw_dir / PRODUCT / "_docs"
    t0.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)
    codes = municipality_codes(names)
    manifest = []
    rows = []
    for key, (table, periods) in TABLES.items():
        path = t0 / f"sidra_tabela_{key}.json"
        url = (f"{API}/v3/agregados/{table}/periodos/{periods}/variaveis/93"
               f"?localidades=N6[{','.join(codes.values())}]")
        if refresh or not path.exists():
            r = requests.get(url, headers=HEADERS, timeout=120)
            r.raise_for_status()
            path.write_text(json.dumps(r.json(), ensure_ascii=False))
            manifest.append({"arquivo": path.name, "tabela": table, "periodos": periods,
                             "baixado_em": date.today().isoformat(), "url": url})
        data = json.loads(path.read_text())
        for res in data[0]["resultados"]:
            for s in res["series"]:
                code = s["localidade"]["id"]
                for year, value in s["serie"].items():
                    rows.append({"cd_mun": code, "ano": int(year),
                                 "pop": pd.to_numeric(value, errors="coerce")})
    if manifest:
        m = pd.DataFrame(manifest)
        mp = docs / "manifesto_download.csv"
        if mp.exists():
            m = pd.concat([pd.read_csv(mp), m], ignore_index=True)
        m.to_csv(mp, index=False)
    inv = {v: k for k, v in codes.items()}
    df = pd.DataFrame(rows)
    df["nm_mun"] = df["cd_mun"].map(inv)
    return df.sort_values(["nm_mun", "ano"]).reset_index(drop=True)[["nm_mun", "cd_mun", "ano", "pop"]]
