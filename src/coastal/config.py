"""Paths: read from config.local.json (gitignored), like the rest of the repositories.

- raw_dir   shared raw data catalog (read; new downloads are saved here under t0/)
- data_dir  this project's outputs (tables, spatial files, figures)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Project area: AULINOR (Aglomeração Urbana do Litoral Norte) = 20 municipalities.
# The paper focuses on these three.
FOCUS = ["Osório", "Tramandaí", "Imbé"]
YEARS = [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023]


def load():
    """Return (raw_dir, data_dir) as Paths; create data_dir subfolders."""
    cfg_path = ROOT / "config.local.json"
    if not cfg_path.exists():
        raise SystemExit(f"Missing {cfg_path.name}: copy config.local.json.example and set raw_dir and data_dir.")
    cfg = json.loads(cfg_path.read_text())
    raw_dir, data_dir = Path(cfg["raw_dir"]), Path(cfg["data_dir"])
    if not raw_dir.exists():
        raise SystemExit(f"raw_dir not found: {raw_dir}")
    for sub in ("tables", "spatial", "figures"):
        (data_dir / sub).mkdir(parents=True, exist_ok=True)
    return raw_dir, data_dir


def aulinor_dir(raw_dir):
    """Folder with the AULINOR MapBiomas polygons (moved once during the raw_dir reorganization)."""
    for rel in ("_projetos/aulinor", "_archive/projetos/aulinor"):
        p = raw_dir / rel
        if (p / "mapbiomas").exists():
            return p
    raise SystemExit("aulinor folder not found under raw_dir (_projetos/aulinor or _archive/projetos/aulinor)")
