"""colourings.py -- EXACT (rational) colourings used for the certification.

A colouring ("configuration") consists of
  * a period lattice G = Z g1 + Z g2 (g1, g2 rational);
  * a list of representative pieces (rational convex CCW polygon, colour) whose union is a
    fundamental domain of G (up to a null set) and whose G-translates partition the plane.
    Pieces of colour 4 are the fifth-colour regions; pieces of colour < 4 are the hexagons
    minus the fifth-colour regions.

Colourings:
  * 'BANDES'   : trivial test, vertical strips of width 1, 2 colours; p = 1 - 2/pi.
  * 'H4'       : hexagons (D = 1.133523), 4 colours, s = sqrt(3) R rounded to a rational.
  * 'DISQP<N>' : the fifth-colour disk is replaced by a rational N-gon.
  * 'ILEP...'  : see island.py.

The JSON schema (keys in French, kept for byte-identical outputs): "nom" = name,
"aire_cellule" = cell area, "parametres" = parameters, "pieces" = pieces, "couleur" = colour,
"sommets" = vertices. Rationals are written "p/q".
"""
import json, math, os
from flint import fmpq
import geometry as L

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data", "input")


def q(x, den=10 ** 9):
    return L.rational(x, den)


def qstr(x):
    return f"{int(x.p)}/{int(x.q)}"


class Config:
    def __init__(self, name, g1, g2, pieces, params):
        self.name = name
        self.g1, self.g2 = g1, g2
        self.pieces = pieces          # list of (polygon, colour)
        self.params = params          # dict of exact parameters (for the JSON)
        self.cell_area = abs(g1[0] * g2[1] - g1[1] * g2[0])

    def json(self):
        return {"nom": self.name,
                "g1": [qstr(c) for c in self.g1], "g2": [qstr(c) for c in self.g2],
                "aire_cellule": qstr(self.cell_area),
                "parametres": {k: (qstr(v) if isinstance(v, type(fmpq(1))) else v)
                               for k, v in self.params.items()},
                "pieces": [{"couleur": c, "sommets": [[qstr(x), qstr(y)] for (x, y) in P]}
                           for (P, c) in self.pieces]}


def hexagon(c, R, s):
    """Hexagon with centre c: vertices c+(R,0), c+(R/2,s/2), c+(-R/2,s/2), c+(-R,0),
    c+(-R/2,-s/2), c+(R/2,-s/2). For s = sqrt(3) R it is regular; for a rational s close to
    it, it is the image of a regular hexagon under (x, y) -> (x, y s/(sqrt3 R))."""
    h = R / 2
    return [(c[0] + R, c[1]), (c[0] + h, c[1] + s / 2), (c[0] - h, c[1] + s / 2),
            (c[0] - R, c[1]), (c[0] - h, c[1] - s / 2), (c[0] + h, c[1] - s / 2)]


def hex_lattice(R, s):
    v1 = (3 * R / 2, s / 2)
    v2 = (fmpq(0), s)
    return v1, v2


def hexagon_reps(R, s):
    v1, v2 = hex_lattice(R, s)
    reps = []
    for (i, j) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        c = (i * v1[0] + j * v2[0], i * v1[1] + j * v2[1])
        reps.append((hexagon(c, R, s), i + 2 * j))
    return reps, v1, v2


def add_fifth_colour(reps_hex, regions, g1, g2, nmax=3):
    """Pieces: each hexagon minus all the G-translates of the convex regions that meet it;
    plus the representative regions (colour 4)."""
    pieces = []
    for (H, c) in reps_hex:
        parts = [H]
        for K0 in regions:
            for a in range(-nmax, nmax + 1):
                for b in range(-nmax, nmax + 1):
                    t = (a * g1[0] + b * g2[0], a * g1[1] + b * g2[1])
                    K = L.translate(K0, t)
                    S, _ = L.intersection(H, K)
                    if len(S) >= 3 and L.area(S) > 0:
                        new = []
                        for X in parts:
                            S2, _ = L.intersection(X, K)
                            if len(S2) >= 3 and L.area(S2) > 0:
                                new.extend(L.subtract(X, K))
                            else:
                                new.append(X)
                        parts = new
        pieces.extend((X, c) for X in parts)
    for K0 in regions:
        pieces.append((K0, 4))
    return pieces


# ---------------------------------------------------------------------------

def config_strips():
    g1, g2 = (fmpq(2), fmpq(0)), (fmpq(0), fmpq(1, 2))
    r0 = [(fmpq(0), fmpq(0)), (fmpq(1), fmpq(0)), (fmpq(1), fmpq(1, 2)), (fmpq(0), fmpq(1, 2))]
    r1 = L.translate(r0, (fmpq(1), fmpq(0)))
    return Config("BANDES", g1, g2, [(r0, 0), (r1, 1)], {"largeur": fmpq(1), "hauteur_piece": fmpq(1, 2)})


def config_h4():
    D = fmpq(1133523, 10 ** 6)
    R = D / 2
    s = q(math.sqrt(3) * float(R), 10 ** 12)
    reps, v1, v2 = hexagon_reps(R, s)
    g1, g2 = (2 * v1[0], 2 * v1[1]), (2 * v2[0], 2 * v2[1])
    return Config("H4", g1, g2, reps, {"R": R, "s": s})


def ngon(centre, r, N, phase, den=10 ** 9):
    """N-gon with rational vertices: centre + r (cos, sin)(phase + 2 pi k / N) rounded to 1/den."""
    return [(centre[0] + q(r * math.cos(phase + 2 * math.pi * k / N), den),
             centre[1] + q(r * math.sin(phase + 2 * math.pi * k / N), den)) for k in range(N)]


def config_disqp(N=32, r=None, phase=None, ty=None):
    with open(os.path.join(DATA_DIR, "parametres.json")) as f:
        P = json.load(f)["DISQ"]
    R = q(P["D"] / 2, 10 ** 8)
    s = q(math.sqrt(3) * float(R), 10 ** 12)
    if ty is None:
        ty = P["centre_en_unites_de_s"][1]
    if r is None:
        r = P["rayon_disque_r"]
    if phase is None:
        phase = math.pi / N          # no vertex on the vertical/horizontal axis
    cy = q(ty * float(s), 10 ** 9)
    E = ngon((fmpq(0), cy), r, N, phase)
    reps, v1, v2 = hexagon_reps(R, s)
    g1, g2 = (2 * v1[0], 2 * v1[1]), (2 * v2[0], 2 * v2[1])
    pieces = add_fifth_colour(reps, [E], g1, g2)
    return Config(f"DISQP{N}", g1, g2, pieces,
                  {"R": R, "s": s, "centre_y": cy, "N": N, "rayon_flottant_genere": r,
                   "phase_flottante_generee": phase})


def build(name, **kw):
    if name == "BANDES":
        return config_strips()
    if name == "H4":
        return config_h4()
    if name.startswith("DISQP"):
        return config_disqp(**kw)
    if name.startswith("ILEP"):
        import island
        return island.config_ilep(**kw)
    raise ValueError(name)
