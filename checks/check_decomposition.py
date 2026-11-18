"""check_decomposition.py CONFIG.json [INPUT_DIR] -- exact check (fractions.Fraction) of the piece decomposition of
an ILEP colouring with free centre and angles (written for ILEP_S6A during an AI review of the splitting of
non-convex hexagons). Reads ONLY the config JSON (pieces + exact parameters R, s, delta, m, island) and the
float inputs (to check the rounding). Does not import the certifier.

Checks:
 H0  hexagons rebuilt from the exact parameters; orientation, reflex vertices, simplicity;
 H1  each hexagon split by an independent method (one diagonal from the reflex vertex) into two
     convex polygons; area check;
 I0  island W: star-shaped w.r.t. m (cross > 0) and winding number 1 (exact count);
 C1  every piece of colour c < 4 lies in hexagon c (area(piece) = sum area(piece & part));
 C2  no piece of colour c < 4 meets the interior of any island translate (25 translates);
 C3  area(pieces of colour c) = area(H_c) - area(H_c & union of island translates);
 C4  colour-4 pieces lie in the island and their areas sum to area(island);
 E1/E2 strict convexity (CCW, equal to hull) and sum of areas = |det(g1,g2)| (own code);
 X   edge cases: reflex vertex vs island translates, min area / min turn / min edge of pieces.
Combined with E3 (disjoint interiors of the G-translates), C1-C4 show that, for each hexagon,
the union of its pieces is exactly closure(H_c minus islands) and nothing is lost.
"""
import json, sys, math
from fractions import Fraction as Fr

CFG = sys.argv[1]
INP = sys.argv[2] if len(sys.argv) > 2 else None


def fr(s):
    a, b = s.split("/")
    return Fr(int(a), int(b))


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def area(P):
    n = len(P)
    return sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n)) / 2


def hull(points):
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def strictly_convex(P):
    n = len(P)
    if n < 3 or not all(cross(P[i], P[(i + 1) % n], P[(i + 2) % n]) > 0 for i in range(n)):
        return False
    H = hull(P)
    if len(H) != n or P[0] not in H:
        return False
    k = H.index(P[0])
    return all(P[i] == H[(k + i) % n] for i in range(n))


def clip(P, A, B):
    """P inter {left of the directed line A->B (closed)} (Sutherland-Hodgman)."""
    out = []
    n = len(P)
    for i in range(n):
        p, q = P[i], P[(i + 1) % n]
        dp, dq = cross(A, B, p), cross(A, B, q)
        if dp >= 0:
            out.append(p)
        if (dp > 0 and dq < 0) or (dp < 0 and dq > 0):
            t = dp / (dp - dq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def inter_area(P, Q):
    """area(P inter Q), P and Q convex CCW."""
    S = list(P)
    m = len(Q)
    for k in range(m):
        if len(S) < 3:
            return Fr(0)
        S = clip(S, Q[k], Q[(k + 1) % m])
    return area(S) if len(S) >= 3 else Fr(0)


def bbox(P):
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    return min(xs), max(xs), min(ys), max(ys)


def bb_meet(b1, b2):
    return not (b1[1] <= b2[0] or b2[1] <= b1[0] or b1[3] <= b2[2] or b2[3] <= b1[2])


def seg_cross_proper(a, b, c, d):
    d1, d2, d3, d4 = cross(a, b, c), cross(a, b, d), cross(c, d, a), cross(c, d, b)
    return d1 * d2 < 0 and d3 * d4 < 0


C = json.load(open(CFG))
par = C["parametres"]
g1 = tuple(fr(z) for z in C["g1"]); g2 = tuple(fr(z) for z in C["g2"])
cell = abs(g1[0] * g2[1] - g1[1] * g2[0])
R, s = fr(par["R"]), fr(par["s"])
m = (fr(par["m_x"]), fr(par["m_y"]))
W = [(fr(x), fr(y)) for (x, y) in json.loads(par["ile"].replace("'", '"'))] if isinstance(par["ile"], str) \
    else [(fr(x), fr(y)) for (x, y) in par["ile"]]
dl_raw = json.loads(par["delta"].replace("'", '"')) if isinstance(par["delta"], str) else par["delta"]
dl = [[[(fr(d[0]), fr(d[1])) for d in row] for row in typ] for typ in dl_raw]
pieces = [([(fr(x), fr(y)) for (x, y) in p["sommets"]], p["couleur"]) for p in C["pieces"]]
print(f"config {C['nom']}: {len(pieces)} pieces, colours {sorted(set(c for _, c in pieces))},"
      f" island {len(W)} vertices")

v1 = (3 * R / 2, s / 2); v2 = (Fr(0), s)
assert g1 == (2 * v1[0], 2 * v1[1]) and g2 == (2 * v2[0], 2 * v2[1]), "lattice != 2 v1, 2 v2"
assert C["aire_cellule"] == f"{cell.numerator}/{cell.denominator}" or fr(C["aire_cellule"]) == cell


def c_(i, j):
    return (i * v1[0] + j * v2[0], i * v1[1] + j * v2[1])


def P0(i, j):
    cc, d = c_(i, j), dl[0][i % 2][j % 2]
    return (cc[0] + R + d[0], cc[1] + d[1])


def P1(i, j):
    cc, d = c_(i, j), dl[1][i % 2][j % 2]
    return (cc[0] + R / 2 + d[0], cc[1] + s / 2 + d[1])


def hexa(i, j):
    return [P0(i, j), P1(i, j), P0(i - 1, j + 1), P1(i - 1, j), P0(i - 1, j), P1(i, j - 1)]


# rounding of the float inputs (reproducibility only)
if INP:
    Hj = json.load(open(INP + "/ILE_hexagones.json")); Ij = json.load(open(INP + "/ILE_ile.json"))
    DEN = 10 ** 12
    q = lambda x: Fr(int(round(x * DEN)), DEN)
    assert R == q(Hj["D"] / 2) and s == q(math.sqrt(3) * float(R))
    assert all(dl[t][a][b] == (q(Hj["deplacements_sommets"]["delta"][t][a][b][0]), q(Hj["deplacements_sommets"]["delta"][t][a][b][1]))
               for t in range(2) for a in range(2) for b in range(2))
    assert m == (q(Ij["m_libre"][0]), q(Ij["m_libre"][1]))
    assert len(W) == len(Ij["rho_k"]) == len(Ij["psi_k"])
    assert all(W[k] == (m[0] + q(Ij["rho_k"][k] * math.cos(Ij["psi_k"][k])), m[1] + q(Ij["rho_k"][k] * math.sin(Ij["psi_k"][k])))
               for k in range(len(W)))
    print("[R0] exact parameters of the JSON = rounding to 1/10^12 of the float inputs: OK")

# E1, E2 (own implementation)
assert all(strictly_convex(P) for P, _ in pieces), "E1 fails"
assert sum(area(P) for P, _ in pieces) == cell, "E2 fails"
assert all(c in (0, 1, 2, 3, 4) for _, c in pieces)
print(f"[E1/E2] {len(pieces)} pieces strictly convex CCW; sum of areas = |det(g1,g2)| = {float(cell):.15f}")

# I0 island
n = len(W)
assert all(cross(m, W[k], W[(k + 1) % n]) > 0 for k in range(n))
wind = sum(1 for k in range(n) if W[k][1] - m[1] < 0 <= W[(k + 1) % n][1] - m[1])
assert wind == 1, wind
sect = [[m, W[k], W[(k + 1) % n]] for k in range(n)]
A_isl = area(W)
assert A_isl == sum(area(T) for T in sect)
print(f"[I0] island star-shaped w.r.t. m, winding number {wind} (exact), area {float(A_isl):.12f};"
      f" min cross(m,W_k,W_k+1) = {float(min(cross(m, W[k], W[(k + 1) % n]) for k in range(n))):.3e}")
reflex_island = [k for k in range(n) if cross(W[k - 1], W[k], W[(k + 1) % n]) < 0]
print(f"     island reflex vertices: {len(reflex_island)} ; island convex: {len(reflex_island) == 0}")

trans = [(a * g1[0] + b * g2[0], a * g1[1] + b * g2[1]) for a in range(-2, 3) for b in range(-2, 3)]
sect_t = []
for t in trans:
    for T in sect:
        Tt = [(x + t[0], y + t[1]) for (x, y) in T]
        sect_t.append((Tt, bbox(Tt)))

order = [(0, 0), (1, 0), (0, 1), (1, 1)]
pb = [bbox(P) for P, _ in pieces]
ok_all = True
for (i, j) in order:
    col = i + 2 * j
    H = hexa(i, j)
    A_H = area(H)
    nH = len(H)
    turns = [cross(H[k - 1], H[k], H[(k + 1) % nH]) for k in range(nH)]
    refl = [k for k in range(nH) if turns[k] < 0]
    simple = not any(seg_cross_proper(H[a], H[(a + 1) % nH], H[b], H[(b + 1) % nH])
                     for a in range(nH) for b in range(a + 2, nH) if not (a == 0 and b == nH - 1))
    print(f"\n[H0] hexagon ({i},{j}) colour {col}: area {float(A_H):.12f} (>0: {A_H > 0}), simple {simple},"
          f" reflex vertices {refl}, turns min/max {float(min(turns)):.4e}/{float(max(turns)):.4e}")
    assert A_H > 0 and simple and len(refl) <= 1
    if refl:
        r = refl[0]
        # independent split: one diagonal from the reflex vertex r to some vertex r+d
        parts = None
        for dgo in (3, 2, 4):
            Q1 = [H[(r + k) % nH] for k in range(0, dgo + 1)]
            Q2 = [H[(r + k) % nH] for k in range(dgo, nH + 1)]
            ok = all(cross(Q[k - 1], Q[k], Q[(k + 1) % len(Q)]) > 0 for Q in (Q1, Q2) for k in range(len(Q)))
            if ok and area(Q1) + area(Q2) == A_H:
                parts = [Q1, Q2]
                print(f"[H1] split by the diagonal V{r}-V{(r + dgo) % nH}: two strictly convex polygons"
                      f" ({len(Q1)} and {len(Q2)} vertices), areas sum to area(H)")
                break
        assert parts is not None, "no convex split by one diagonal"
        assert all(strictly_convex(Q) for Q in parts)
        # reflex vertex vs islands
        rv = H[r]
        insid = []
        for (Tt, bt) in sect_t:
            # rv in closed triangle?
            c1, c2, c3 = cross(Tt[0], Tt[1], rv), cross(Tt[1], Tt[2], rv), cross(Tt[2], Tt[0], rv)
            if c1 >= 0 and c2 >= 0 and c3 >= 0:
                insid.append((c1 > 0 and c2 > 0 and c3 > 0, c2 == 0))
        st = "outside every island translate" if not insid else \
            ("strictly inside an island sector" if any(a for a, _ in insid) else "ON the boundary of an island translate")
        print(f"[X] reflex vertex V{r} = ({float(rv[0]):.6f},{float(rv[1]):.6f}): {st} {insid[:3]}")
    else:
        assert all(t > 0 for t in turns)
        parts = [H]
    pbH = [bbox(Q) for Q in parts]
    # island area inside H
    A_HI = Fr(0)
    for (Tt, bt) in sect_t:
        for Q, bq in zip(parts, pbH):
            if bb_meet(bt, bq):
                A_HI += inter_area(Q, Tt)
    mine = [k for k, (P, c) in enumerate(pieces) if c == col]
    S = Fr(0)
    for k in mine:
        P = pieces[k][0]
        aP = area(P)
        S += aP
        inH = sum(inter_area(P, Q) for Q, bq in zip(parts, pbH) if bb_meet(pb[k], bq))
        if inH != aP:
            ok_all = False; print("  C1 FAIL piece", k)
        for (Tt, bt) in sect_t:
            if bb_meet(pb[k], bt) and inter_area(P, Tt) != 0:
                ok_all = False; print("  C2 FAIL piece", k); break
    print(f"[C1/C2] {len(mine)} pieces of colour {col}: all inside hexagon ({i},{j}), none meets an island interior")
    print(f"[C3] area(H) - area(H & islands) = {float(A_H - A_HI):.15f} ; sum pieces = {float(S):.15f} ;"
          f" exact equality: {A_H - A_HI == S} ; island area cut = {float(A_HI):.12f}")
    ok_all &= (A_H - A_HI == S)

mine = [k for k, (P, c) in enumerate(pieces) if c == 4]
S4 = Fr(0)
bW = bbox(W)
for k in mine:
    P = pieces[k][0]; S4 += area(P)
    inI = sum(inter_area(P, T) for T in sect if bb_meet(pb[k], bbox(T)))
    if inI != area(P):
        ok_all = False; print("  C4 FAIL piece", k)
print(f"\n[C4] {len(mine)} pieces of colour 4 inside the island at m; sum = {float(S4):.15f},"
      f" area(island) = {float(A_isl):.15f}, equal: {S4 == A_isl}")
ok_all &= (S4 == A_isl)
# global balance
tot_hex = sum(area(hexa(i, j)) for (i, j) in order)
print(f"[B] sum of the 4 hexagon areas = {float(tot_hex):.15f} ; |C| = {float(cell):.15f} ; equal: {tot_hex == cell}")

# X: degeneracies
amin = min(area(P) for P, _ in pieces)
tmin = min(cross(P[i - 1], P[i], P[(i + 1) % len(P)]) for P, _ in pieces for i in range(len(P)))
emin = min((P[i][0] - P[i - 1][0]) ** 2 + (P[i][1] - P[i - 1][1]) ** 2 for P, _ in pieces for i in range(len(P)))
nv = [len(P) for P, _ in pieces]
print(f"[X] min piece area {float(amin):.3e} ; min turn (cross) {float(tmin):.3e} ; min edge length"
      f" {math.sqrt(float(emin)):.3e} ; vertices per piece {min(nv)}..{max(nv)} ; triangles {nv.count(3)}")
print(f"\nRESULT: {'ALL CHECKS PASSED' if ok_all else 'FAILURE'}")
