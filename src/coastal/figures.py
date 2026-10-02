"""Figures in the project's visual identity (brand palette, Source Code Pro)."""
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from . import metrics, style
from .classes import GROUPS
from .config import FOCUS, YEARS

FOCUS_COLORS = {"Osório": style.ORANGE, "Tramandaí": style.RUST, "Imbé": style.SAGE_D}


def _legend(fig, ncol=5, y=0.075, groups=GROUPS):
    handles = [Patch(facecolor=c, edgecolor="none", label=g) for g, c in groups.items()]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, y), ncol=ncol,
               fontsize=8.5, handlelength=1.1, handleheight=1.1, columnspacing=1.6)


def urban_timeline(lc, growth, out):
    """Urban area of the three focus municipalities, 1985-2023."""
    t = metrics.urban_by_year(lc).loc[FOCUS]
    g = growth.set_index("nm_mun")
    ymax = t.values.max() * 1.12
    fig, ax = plt.subplots(figsize=(10, 5.6))
    fig.subplots_adjust(left=0.08, right=0.76, top=0.78, bottom=0.14)
    # end labels, pushed apart so they never overlap
    ends = sorted(FOCUS, key=lambda m: -t.loc[m, 2023])
    ypos, gap = {}, ymax * 0.05
    for m in ends:
        y = t.loc[m, 2023]
        ypos[m] = min(y, ypos[ends[ends.index(m) - 1]] - gap) if ends.index(m) else y
    for m in FOCUS:
        c = FOCUS_COLORS[m]
        ax.plot(YEARS, t.loc[m], color=c, lw=2.6, marker="o", ms=5, mfc="white", mew=2)
        ax.annotate(f"{t.loc[m, 1985]:.1f}", (1985, t.loc[m, 1985]), xytext=(-8, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=8.5, color=c)
        ax.annotate(f"{m}  {t.loc[m, 2023]:.1f} km²  +{g.loc[m, 'growth_pct']:.0f}%", (2023, t.loc[m, 2023]),
                    xytext=(2024.8, ypos[m]), textcoords="data", ha="left", va="center",
                    fontsize=9, color=c, fontweight="semibold", annotation_clip=False,
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.8, shrinkA=0, shrinkB=4))
    ax.set_xlim(1980, 2024)
    ax.set_ylim(0, ymax)
    ax.set_xticks(YEARS)
    ax.set_xticklabels([str(y) for y in YEARS], fontsize=8.5)
    ax.set_ylabel("Urban area (km²)")
    ax.grid(axis="x", visible=False)
    style.header(fig, "Urban area, 1985–2023",
                 "Osório, Tramandaí and Imbé. Growth over 38 years, in km² and as a share of the 1985 area.")
    style.footer(fig)
    style.save(fig, out)


def urban_growth(growth, out, min_km2=1.0):
    """Dumbbell chart: urban area 1985 vs 2023 by municipality."""
    total = growth[growth["nm_mun"].str.startswith("AULINOR")].iloc[0]
    d = growth[~growth["nm_mun"].str.startswith("AULINOR") & (growth["km2_2023"] >= min_km2)]
    d = d.sort_values("km2_2023")
    fig, ax = plt.subplots(figsize=(10, 6.4))
    fig.subplots_adjust(left=0.2, right=0.9, top=0.8, bottom=0.15)
    for i, (_, r) in enumerate(d.iterrows()):
        ax.plot([r["km2_1985"], r["km2_2023"]], [i, i], color=style.GREY, lw=4, solid_capstyle="round", zorder=1)
        ax.scatter(r["km2_1985"], i, s=55, color=style.SAGE_D, zorder=3)
        ax.scatter(r["km2_2023"], i, s=55, color=style.ORANGE, zorder=3)
        label = "new" if r["km2_1985"] < 0.05 else f"+{r['growth_pct']:.0f}%"
        ax.annotate(label, (r["km2_2023"], i), xytext=(10, 0), textcoords="offset points", va="center",
                    fontsize=8.5, color=style.MUTED)
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(d["nm_mun"], fontsize=9)
    for lab in ax.get_yticklabels():
        if lab.get_text() in FOCUS:
            lab.set_fontweight("semibold")
            lab.set_color(style.INK)
    ax.set_xlim(0, d["km2_2023"].max() * 1.15)
    ax.set_ylim(-0.7, len(d) - 0.3)
    ax.set_xlabel("Urban area (km²)")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=style.SAGE_D, label="1985"),
                       Line2D([], [], marker="o", ls="", color=style.ORANGE, label="2023")],
              loc="lower right", fontsize=9)
    style.header(fig, "Where the urban area grew",
                 f"AULINOR (20 municipalities): {total['km2_1985']:.0f} → {total['km2_2023']:.0f} km² "
                 f"(+{total['growth_pct']:.0f}%).\nMunicipalities with at least {min_km2:.0f} km² of urban area in 2023.")
    style.footer(fig)
    style.save(fig, out)


def landcover_change(lc, out):
    """Stacked land cover by group over time, for the three focus municipalities."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 5.6))
    fig.subplots_adjust(left=0.06, right=0.985, top=0.76, bottom=0.25, wspace=0.28)
    for ax, m in zip(axes, FOCUS):
        d = metrics.area_by_group(lc, [m])
        ax.stackplot(d.index, [d[g] for g in d.columns], colors=list(GROUPS.values()),
                     edgecolor="white", linewidth=0.5)
        ax.set_xlim(1985, 2023)
        ax.set_xticks([1985, 2000, 2015, 2023])
        ax.set_title(m, loc="left", fontsize=10.5, fontweight="semibold", color=style.INK, pad=8)
        ax.grid(visible=False)
        ax.set_ylabel("km²" if m == FOCUS[0] else "")
    _legend(fig, ncol=5, y=0.075)
    style.header(fig, "Land cover, 1985–2023",
                 "Area by land-cover group. Urban area (top, orange) grows while beach, dune, restinga and wetland\n"
                 "classes shrink. The y-axis differs between municipalities; unclassified land (0.4–2%) is not shown.")
    style.footer(fig)
    style.save(fig, out)


def land_replaced(shares, replaced_km2, out):
    """What the new urban area replaced: share by 1985 land-cover group."""
    order = ["AULINOR", "Osório", "Tramandaí", "Imbé"]
    groups = [g for g in GROUPS if g != "Urban"]
    fig, ax = plt.subplots(figsize=(11, 4.9))
    fig.subplots_adjust(left=0.13, right=0.9, top=0.74, bottom=0.27)
    for i, name in enumerate(reversed(order)):
        d = shares[shares["area"] == name].set_index("group")["pct"]
        left = 0
        for g in groups:
            w = d.get(g, 0)
            ax.barh(i, w, left=left, color=GROUPS[g], edgecolor="white", height=0.62)
            if w >= 7:
                dark = g in ("Forest", "Forestry", "Restinga")
                ax.text(left + w / 2, i, f"{w:.0f}%", ha="center", va="center", fontsize=8.5,
                        color="white" if dark else style.INK)
            left += w
        ax.text(101.5, i, f"{replaced_km2[name]:.1f} km²", va="center", fontsize=8.5, color=style.MUTED)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(list(reversed(order)), fontsize=9.5)
    ax.get_yticklabels()[-1].set_fontweight("semibold")
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    ax.grid(visible=False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.text(101.5, len(order) - 0.45, "new urban\narea traced", fontsize=7.5, color=style.MUTED, va="bottom")
    _legend(fig, ncol=4, y=0.06, groups={g: GROUPS[g] for g in groups})
    style.header(fig, "What the new urban land replaced",
                 "Land cover in 1985 of the area that is urban in 2023 but was not in 1985 (share of the area).\n"
                 "Beach, dune, restinga and wetland: about half of AULINOR and most of Imbé and Tramandaí (land unclassified in 1985 excluded).")
    style.footer(fig)
    style.save(fig, out)


def _scalebar(ax, km=10):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    x, y = x0 + (x1 - x0) * 0.04, y0 + (y1 - y0) * 0.93
    ax.plot([x, x + km * 1000], [y, y], color=style.INK, lw=2, solid_capstyle="butt")
    ax.text(x + km * 500, y + (y1 - y0) * 0.015, f"{km} km", ha="center", va="bottom", fontsize=8, color=style.INK)


def _label_municipalities(ax, bnd):
    halo = [pe.withStroke(linewidth=2.5, foreground="white")]
    for _, r in bnd.iterrows():
        p = r.geometry.representative_point()
        ax.text(p.x, p.y, r["nm_mun"], ha="center", va="center", fontsize=8.5, fontweight="semibold",
                color=style.INK, path_effects=halo)


def map_landcover(lc, bnd, out):
    """Land cover of the three focus municipalities in 1985 and 2023."""
    b = bnd[bnd["nm_mun"].isin(FOCUS)]
    minx, miny, maxx, maxy = b.total_bounds
    pad = 1500
    fig, axes = plt.subplots(1, 2, figsize=(11, 8.2))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.85, bottom=0.12, wspace=0.03)
    for ax, year in zip(axes, (1985, 2023)):
        d = lc[(lc["ano"] == year) & lc["nm_mun"].isin(FOCUS)]
        for g, color in GROUPS.items():
            sub = d[d["group"] == g]
            if len(sub):
                sub.plot(ax=ax, color=color, linewidth=0)
        b.boundary.plot(ax=ax, color=style.INK, linewidth=0.7)
        ax.set_xlim(minx - pad, maxx + pad)
        ax.set_ylim(miny - pad, maxy + pad)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(str(year), loc="left", fontsize=11, fontweight="semibold", color=style.INK)
        _scalebar(ax)
    _label_municipalities(axes[1], b)
    _legend(fig, ncol=5, y=0.05)
    style.header(fig, "Land cover in 1985 and 2023", "Osório, Tramandaí and Imbé.")
    style.footer(fig)
    style.save(fig, out)


def map_urban_expansion(lc, bnd, expansion, out):
    """Urban area in 1985 and new urban area by 2023."""
    b = bnd[bnd["nm_mun"].isin(FOCUS)]
    minx, miny, maxx, maxy = b.total_bounds
    pad = 1500
    water = lc[(lc["ano"] == 2023) & (lc["group"] == "Water") & lc["nm_mun"].isin(FOCUS)]
    fig, ax = plt.subplots(figsize=(7.4, 8.6))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.12)
    area = b.union_all()
    b.plot(ax=ax, color="#F4F0EA", linewidth=0)
    water.plot(ax=ax, color=style.SAGE_L, linewidth=0)
    expansion["urban_1985"].intersection(area).plot(ax=ax, color=style.RUST, linewidth=0)
    expansion["urban_new"].intersection(area).plot(ax=ax, color=style.ORANGE, linewidth=0)
    b.boundary.plot(ax=ax, color=style.INK, linewidth=0.7)
    ax.set_xlim(minx - pad, maxx + pad)
    ax.set_ylim(miny - pad, maxy + pad)
    ax.set_aspect("equal")
    ax.axis("off")
    _scalebar(ax)
    _label_municipalities(ax, b)
    fig.legend(handles=[Patch(facecolor=style.RUST, label="Urban in 1985"),
                        Patch(facecolor=style.ORANGE, label="New urban area, 1985–2023"),
                        Patch(facecolor=style.SAGE_L, label="Water (2023)")],
               loc="lower center", bbox_to_anchor=(0.5, 0.055), ncol=3, fontsize=8.5, handlelength=1.1)
    style.header(fig, "Urban expansion, 1985–2023", "Osório, Tramandaí and Imbé.")
    style.footer(fig)
    style.save(fig, out)
