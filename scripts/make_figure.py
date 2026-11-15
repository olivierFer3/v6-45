"""make_figure.py -- figure of the ILEP256 colouring (one period cell and its neighbourhood).

Reads only an ILEP256 colouring file (<name>_config.json: lattice g1, g2 and the list of
convex pieces with their colour) and draws all translates P_i + a g1 + b g2 meeting a
window around the period cell C = {s g1 + t g2 : s, t in [0, 1)}.

Usage: python3 scripts/make_figure.py certificates/ILEP256_config.json note/fig_cellule.pdf
(Uses matplotlib; plays no role in the proof.)
"""
import sys, json
from fractions import Fraction
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

COLOURS = {0: "#d95f5f", 1: "#5f86d9", 2: "#6cbf6c", 3: "#e8cf55", 4: "#8e5fb3"}


def f(s):
    return float(Fraction(s))


def main():
    cfg = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    g1 = [f(z) for z in cfg["g1"]]
    g2 = [f(z) for z in cfg["g2"]]
    pieces = [([(f(x), f(y)) for (x, y) in p["sommets"]], p["couleur"]) for p in cfg["pieces"]]
    xmin, xmax, ymin, ymax = -1.25, 2.45, -0.95, 2.95
    fig, ax = plt.subplots(figsize=(4.6, 4.9))
    for a in range(-2, 3):
        for b in range(-3, 4):
            tx, ty = a * g1[0] + b * g2[0], a * g1[1] + b * g2[1]
            for (P, c) in pieces:
                Q = [(x + tx, y + ty) for (x, y) in P]
                if max(x for x, _ in Q) < xmin or min(x for x, _ in Q) > xmax:
                    continue
                if max(y for _, y in Q) < ymin or min(y for _, y in Q) > ymax:
                    continue
                ax.add_patch(Polygon(Q, closed=True, facecolor=COLOURS[c], edgecolor=COLOURS[c],
                                     linewidth=0.25))
    # period cell
    cell = [(0, 0), (g1[0], g1[1]), (g1[0] + g2[0], g1[1] + g2[1]), (g2[0], g2[1])]
    ax.add_patch(Polygon(cell, closed=True, fill=False, edgecolor="black", linewidth=1.0,
                         linestyle="--"))
    # unit segment
    ax.plot([1.2, 2.2], [-0.8, -0.8], color="black", linewidth=1.5)
    ax.text(1.7, -0.75, "1", ha="center", va="bottom", fontsize=9)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)


if __name__ == "__main__":
    main()
