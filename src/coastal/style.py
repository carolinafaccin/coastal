"""Visual identity for the figures: Source Code Pro and the brand palette."""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

from .config import ROOT

INK = "#383C2F"       # dark olive
MUTED = "#737464"
GRID = "#E7E1DA"
CREAM = "#FFF8F2"
GREY = "#DAD2CC"
SAGE_L = "#CDD7C5"
SAGE = "#93A97E"
SAGE_D = "#5C704C"
YELLOW = "#FDD34A"
PEACH = "#FED2BF"
ORANGE = "#D94400"
RUST = "#7B2405"

SOURCE = "Source: MapBiomas land use and land cover 1985–2023; own calculations."
REPO = "github.com/carolinafaccin/coastal"


def setup():
    """Register the bundled fonts (OFL) and set the matplotlib defaults."""
    for f in (ROOT / "assets" / "fonts").glob("*.ttf"):
        fm.fontManager.addfont(str(f))
    families = {f.name for f in fm.fontManager.ttflist}
    mpl.rcParams.update({
        "font.family": "Source Code Pro" if "Source Code Pro" in families else "monospace",
        "font.size": 9.5,
        "text.color": INK,
        "axes.edgecolor": GREY,
        "axes.labelcolor": MUTED,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "legend.frameon": False,
        "savefig.facecolor": "white",
    })


def header(fig, title, subtitle=None, top=0.965):
    fig.text(0.04, top, title, fontsize=15, fontweight="semibold", ha="left", va="top", color=INK)
    if subtitle:
        fig.text(0.04, top - 0.062, subtitle, fontsize=9.5, ha="left", va="top", color=MUTED, linespacing=1.4)


def footer(fig, note=SOURCE):
    fig.text(0.04, 0.018, note, fontsize=7.5, ha="left", va="bottom", color=MUTED)
    fig.text(0.96, 0.018, REPO, fontsize=7.5, ha="right", va="bottom", color=MUTED)


def save(fig, path):
    fig.savefig(path, dpi=200)
    plt.close(fig)
