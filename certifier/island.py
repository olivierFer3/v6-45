"""island.py -- the ILE colouring made exact (rational) for the certification (ILEP256).

* Lattice: R = D/2 and s ~ sqrt(3) R rounded to rationals; v1 = (3R/2, s/2), v2 = (0, s).
* Deformed hexagons: vertices P0(i,j) = c_ij + (R,0) + delta0[i%2][j%2],
  P1(i,j) = c_ij + (R/2, s/2) + delta1[i%2][j%2] (delta rounded to rationals);
  hexagon (i,j) = (P0(i,j), P1(i,j), P0(i-1,j+1), P1(i-1,j), P0(i-1,j), P1(i,j-1)).
* Island: m = exact midpoint of P1(0,0) - P0(-1,1); vertices W = m + rho(psi)(cos psi, sin psi)
  rounded to rationals, for the angles psi_k = 2 pi k / 256 with k in range(decal, 256, pas)
  (rho_k from ILE_ile.json). The certified colouring uses pas = 1 (all 256 vertices).
  The island is star-shaped with respect to m (increasing angles, checked exactly).
* Convex pieces: island = union of convex sectors (m, W_a, ..., W_b) (greedy merging of
  triangles); hexagon minus island = union of H inter cone_k inter {beyond the edge W_k W_k+1}
  (cone_k = cone with apex m spanned by W_k - m and W_k+1 - m), merged when their union is
  convex.
"""
import json, math, os
from flint import fmpq
import geometry as L
from colourings import Config, DATA_DIR, q

DEN = 10 ** 12


def clip_hp(P, a, b, c):
    S, _ = L.clip(P, [0] * len(P), a, b, c, 0)
    return L.clean(S)


def left_half_plane(p, d):
    """{z : cross(d, z - p) >= 0} written as a x + b y <= c."""
    # cross(d, z-p) = d0 (zy - py) - d1 (zx - px) >= 0  <=>  d1 zx - d0 zy <= d1 px - d0 py
    return (d[1], -d[0], d[1] * p[0] - d[0] * p[1])


def merge(pieces):
    """Greedy merging of consecutive convex pieces (cyclic list) when their union is
    convex: area(hull) == sum of the areas (exact)."""
    if not pieces:
        return pieces
    out = [pieces[0]]
    for X in pieces[1:]:
        H = L.hull(out[-1] + X)
        if L.area(H) == L.area(out[-1]) + L.area(X):
            out[-1] = L.clean(H)
        else:
            out.append(X)
    if len(out) > 1:
        H = L.hull(out[-1] + out[0])
        if L.area(H) == L.area(out[-1]) + L.area(out[0]):
            out[0] = L.clean(H)
            out.pop()
    return out


def island_sectors(m, W):
    n = len(W)
    tri = [[m, W[k], W[(k + 1) % n]] for k in range(n)]
    return merge(tri)


def hexagon_minus_island(H, m, W):
    n = len(W)
    parts = []
    for k in range(n):
        A, B = W[k], W[(k + 1) % n]
        X = list(H)
        a, b, c = left_half_plane(m, (A[0] - m[0], A[1] - m[1]))        # left of m->A
        X = clip_hp(X, a, b, c)
        if len(X) < 3:
            continue
        a, b, c = left_half_plane(m, (B[0] - m[0], B[1] - m[1]))        # right of m->B
        X = clip_hp(X, -a, -b, -c)
        if len(X) < 3:
            continue
        a, b, c = left_half_plane(A, (B[0] - A[0], B[1] - A[1]))        # right of A->B (outside)
        X = clip_hp(X, -a, -b, -c)
        if len(X) >= 3 and L.area(X) > 0:
            parts.append(X)
    return merge(parts)


def config_ilep(pas=4, decal=0):
    with open(os.path.join(DATA_DIR, "ILE_hexagones.json")) as f:
        Hj = json.load(f)
    with open(os.path.join(DATA_DIR, "ILE_ile.json")) as f:
        Ij = json.load(f)
    D = Hj["D"]
    R = q(D / 2, DEN)
    s = q(math.sqrt(3) * float(R), DEN)
    dl = [[[(q(d[0], DEN), q(d[1], DEN)) for d in row] for row in typ] for typ in Hj["deplacements_sommets"]["delta"]]
    v1 = (3 * R / 2, s / 2)
    v2 = (fmpq(0), s)

    def c(i, j):
        return (i * v1[0] + j * v2[0], i * v1[1] + j * v2[1])

    def P0(i, j):
        cc, d = c(i, j), dl[0][i % 2][j % 2]
        return (cc[0] + R + d[0], cc[1] + d[1])

    def P1(i, j):
        cc, d = c(i, j), dl[1][i % 2][j % 2]
        return (cc[0] + R / 2 + d[0], cc[1] + s / 2 + d[1])

    def hexa(i, j):
        return [P0(i, j), P1(i, j), P0(i - 1, j + 1), P1(i - 1, j), P0(i - 1, j), P1(i, j - 1)]

    g1, g2 = (2 * v1[0], 2 * v1[1]), (2 * v2[0], 2 * v2[1])
    a1, b1 = P1(0, 0), P0(-1, 1)
    m = ((a1[0] + b1[0]) / 2, (a1[1] + b1[1]) / 2)
    ks = list(range(decal, 256, pas))
    W = []
    for k in ks:
        psi = 2 * math.pi * k / 256
        rho = Ij["rho_k"][k]
        W.append((m[0] + q(rho * math.cos(psi), DEN), m[1] + q(rho * math.sin(psi), DEN)))
    n = len(W)
    for k in range(n):   # star-shaped w.r.t. m, strictly increasing angles (exact)
        A, B = W[k], W[(k + 1) % n]
        assert L.cross(m, A, B) > 0
    # single turn: the angles sum to 2 pi (checked in floating point; each step < pi, exact)
    tot = sum(math.atan2(float(L.cross(m, W[k], W[(k + 1) % n])),
                         float((W[k][0] - m[0]) * (W[(k + 1) % n][0] - m[0]) + (W[k][1] - m[1]) * (W[(k + 1) % n][1] - m[1])))
              for k in range(n))
    assert abs(tot - 2 * math.pi) < 1e-9
    pieces = []
    for (i, j) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        H = hexa(i, j)
        assert L.is_strictly_convex(H)
        # translates of the island meeting H: remove each of them (cones)
        parts = [H]
        for a in range(-2, 3):
            for b in range(-2, 3):
                t = (a * g1[0] + b * g2[0], a * g1[1] + b * g2[1])
                mt = (m[0] + t[0], m[1] + t[1])
                Wt = L.translate(W, t)
                secs = island_sectors(mt, Wt)
                touches = False
                for X in parts:
                    for K in secs:
                        S, _ = L.intersection(X, K)
                        if len(S) >= 3 and L.area(S) > 0:
                            touches = True
                if not touches:
                    continue
                new = []
                for X in parts:
                    new.extend(hexagon_minus_island(X, mt, Wt))
                parts = new
        pieces.extend((X, i + 2 * j) for X in parts)
    for K in island_sectors(m, W):
        pieces.append((K, 4))
    return Config(f"ILEP{pas}", g1, g2, pieces,
                  {"R": R, "s": s, "m_x": m[0], "m_y": m[1], "nb_sommets_ile": n, "pas": pas,
                   "indices_k": ks,
                   "ile": [[f"{int(x.p)}/{int(x.q)}", f"{int(y.p)}/{int(y.q)}"] for (x, y) in W],
                   "delta": [[[[f"{int(d[0].p)}/{int(d[0].q)}", f"{int(d[1].p)}/{int(d[1].q)}"] for d in row] for row in typ] for typ in dl]})
