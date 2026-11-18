"""make_figure.py -- figure of an ILEP colouring (one period cell and its neighbourhood, and a zoom
on one island showing the boundaries of the convex pieces).

Reads only an ILEP colouring file (<name>_config.json: lattice g1, g2 and the list of
convex pieces with their colour) and draws all translates P_i + a g1 + b g2 meeting a
window around the period cell C = {s g1 + t g2 : s, t in [0, 1)}.

Usage: python3 scripts/make_figure.py CONFIG.json OUTPUT.pdf
  version 1: python3 scripts/make_figure.py certificates/ILEP256_config.json note/fig_cellule.pdf
  version 2: python3 scripts/make_figure.py certificates/ILEP_S6A_config.json note/fig_s6a.pdf
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


def draw(ax, pieces, g1, g2, win, edges):
    xmin, xmax, ymin, ymax = win
    for a in range(-2, 3):
        for b in range(-3, 4):
            tx, ty = a * g1[0] + b * g2[0], a * g1[1] + b * g2[1]
            for (P, c) in pieces:
                Q = [(x + tx, y + ty) for (x, y) in P]
                if max(x for x, _ in Q) < xmin or min(x for x, _ in Q) > xmax:
                    continue
                if max(y for _, y in Q) < ymin or min(y for _, y in Q) > ymax:
                    continue
                if edges:
                    ax.add_patch(Polygon(Q, closed=True, facecolor=COLOURS[c], edgecolor="black",
                                         linewidth=0.35))
                else:
                    ax.add_patch(Polygon(Q, closed=True, facecolor=COLOURS[c], edgecolor=COLOURS[c],
                                         linewidth=0.25))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    cfg = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    g1 = [f(z) for z in cfg["g1"]]
    g2 = [f(z) for z in cfg["g2"]]
    pieces = [([(f(x), f(y)) for (x, y) in p["sommets"]], p["couleur"]) for p in cfg["pieces"]]
    fig, (ax, az) = plt.subplots(1, 2, figsize=(9.2, 4.9), gridspec_kw={"width_ratios": [1, 1]})
    # left: the period cell and its neighbourhood
    draw(ax, pieces, g1, g2, (-1.25, 2.45, -0.95, 2.95), edges=False)
    cell = [(0, 0), (g1[0], g1[1]), (g1[0] + g2[0], g1[1] + g2[1]), (g2[0], g2[1])]
    ax.add_patch(Polygon(cell, closed=True, fill=False, edgecolor="black", linewidth=1.0,
                         linestyle="--"))
    ax.plot([1.2, 2.2], [-0.8, -0.8], color="black", linewidth=1.5)
    ax.text(1.7, -0.75, "1", ha="center", va="bottom", fontsize=9)
    # right: zoom on one island (colour 4) with the boundaries of all convex pieces
    pts = [v for (P, c) in pieces if c == 4 for v in P]
    cx = (min(x for x, _ in pts) + max(x for x, _ in pts)) / 2
    cy = (min(y for _, y in pts) + max(y for _, y in pts)) / 2
    r = 0.72
    draw(az, pieces, g1, g2, (cx - r, cx + r, cy - r, cy + r), edges=True)
    az.plot([cx - 0.5, cx + 0.5], [cy - r + 0.05] * 2, color="black", linewidth=1.5)
    az.text(cx, cy - r + 0.08, "1", ha="center", va="bottom", fontsize=9)
    ax.add_patch(Polygon([(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)],
                         closed=True, fill=False, edgecolor="black", linewidth=0.6))
    fig.tight_layout(w_pad=0.6)
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)


if __name__ == "__main__":
    main()
