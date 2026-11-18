"""make_regions_figure.py -- simple figure of a colouring without the splitting lines: the regions of
colours 0-3 (hexagons minus the islands) and the island (colour 4) of one period cell, each drawn as the
union of the pieces of that colour, together with their translates around the cell.

It also prints, for each colour, the exact area (sum of the rational piece areas) and the diameter
(maximal distance between vertices of the pieces of that colour) of the region in one cell.

Usage: python3 scripts/make_regions_figure.py CONFIG.json OUTPUT.pdf
  e.g. python3 scripts/make_regions_figure.py certificates/ILEP_S6A_config.json note/fig_s6a_regions.pdf
(Uses shapely and matplotlib; plays no role in the proof.)
"""
import sys, json, math
from fractions import Fraction
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPolygon
from shapely.geometry import Polygon
from shapely.ops import unary_union

COLOURS = {0: "#d95f5f", 1: "#5f86d9", 2: "#6cbf6c", 3: "#e8cf55", 4: "#8e5fb3"}


def area(P):
    n = len(P)
    return sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n)) / 2


def main():
    cfg = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    g1 = [float(Fraction(z)) for z in cfg["g1"]]
    g2 = [float(Fraction(z)) for z in cfg["g2"]]
    by = {}
    for p in cfg["pieces"]:
        by.setdefault(p["couleur"], []).append([(Fraction(x), Fraction(y)) for (x, y) in p["sommets"]])
    regions = {}
    for c in sorted(by):
        A = sum(area(P) for P in by[c])
        V = [v for P in by[c] for v in P]
        d2 = max((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 for a in V for b in V)
        print(f"colour {c}: {len(by[c])} pieces, area {float(A):.6f}, diameter {math.sqrt(d2):.6f}")
        # tiny buffer so that pieces sharing an edge merge into one region in the drawing
        U = unary_union([Polygon([(float(x), float(y)) for (x, y) in P]).buffer(1e-9) for P in by[c]])
        regions[c] = list(U.geoms) if hasattr(U, "geoms") else [U]
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    xmin, xmax, ymin, ymax = -1.25, 2.45, -0.95, 2.95
    for a in range(-2, 3):
        for b in range(-3, 4):
            tx, ty = a * g1[0] + b * g2[0], a * g1[1] + b * g2[1]
            for c, geoms in regions.items():
                for g in geoms:
                    Q = [(x + tx, y + ty) for (x, y) in g.exterior.coords]
                    ax.add_patch(MPolygon(Q, closed=True, facecolor=COLOURS[c], edgecolor="black",
                                          linewidth=0.3))
    cell = [(0, 0), (g1[0], g1[1]), (g1[0] + g2[0], g1[1] + g2[1]), (g2[0], g2[1])]
    ax.add_patch(MPolygon(cell, closed=True, fill=False, edgecolor="black", linewidth=1.0, linestyle="--"))
    ax.plot([1.2, 2.2], [-0.8, -0.8], color="black", linewidth=1.5)
    ax.text(1.7, -0.75, "1", ha="center", va="bottom", fontsize=9)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02, metadata={"Creator": None, "Producer": None})


if __name__ == "__main__":
    main()
