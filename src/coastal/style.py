"""Figure style: the brand (brand.py, synced from the lina-brand repository) plus this
repository's source line and its own header layout (positions as figure fractions, which
the figures here were laid out with)."""
from . import brand
from .brand import *  # noqa: F401,F403  colors, data palettes, helpers
from .config import ROOT

SOURCE = "Source: MapBiomas land use and land cover 1985–2023; own calculations."
REPO = "github.com/carolinafaccin/coastal"


def setup():
    """Register the bundled fonts (OFL) and set the matplotlib defaults."""
    brand.setup(ROOT / "assets" / "fonts")


def header(fig, title, subtitle=None, top=0.965):
    fig.text(0.04, top, title, fontsize=15, fontweight="semibold", ha="left", va="top", color=INK)
    if subtitle:
        fig.text(0.04, top - 0.062, subtitle, fontsize=9.5, ha="left", va="top", color=MUTED, linespacing=1.4)


def footer(fig, note=SOURCE):
    fig.text(0.04, 0.018, note, fontsize=7.5, ha="left", va="bottom", color=MUTED)
    fig.text(0.96, 0.018, REPO, fontsize=7.5, ha="right", va="bottom", color=MUTED)
