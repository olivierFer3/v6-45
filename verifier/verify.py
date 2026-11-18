"""verify.py -- INDEPENDENT verifier of a certificate (does not import the certifier).

It reads only <label>_config.json (exact colouring) and <label>_certificat.json (boxes and
certified box bounds). Exact steps use Python's fractions.Fraction (no python-flint);
the numerical step uses numpy and shapely (GEOS).

Exact checks [E1]-[E6]:
  E1  every piece is strictly convex and CCW: all turns > 0 AND the piece equals its convex
      hull up to a cyclic rotation (this rejects star polygons such as a pentagram);
  E2  sum of the piece areas = |det(g1, g2)| = announced cell area;
  E3  the G-translates of the pieces have pairwise disjoint interiors (separating edge
      line for each pair whose bounding boxes overlap; all translations with |t| <= 2 Rmax,
      Rmax = max |vertex|). E2 + E3 => the translates partition the plane up to a null set;
  E4  completeness of the translations: with W2 = width of F = U pieces orthogonally to g2
      (times |g2|), |a| |C| - W2 > |g2| implies dist(P_i, P_j + a g1 + b g2) > 1 for all
      i, j; same for b with g1. The smallest such |a|, |b| are computed (expected: 2);
  E5  exact list of the pairs (P_i, P_j + t), same colour, |a|, |b| below the E4 thresholds,
      with dist^2 < 1 < max vertex distance^2 (the only pairs whose overlap area A(u) can be
      positive for some unit vector u). Their number is printed;
  E6  final arithmetic of the certificate: the boxes partition [0, 1] (theta = x pi),
      their bounds sum to "somme_bornes", and somme / (pi_low |C|) <= "p_majorant_lisible"
      with pi_low = 314159265358979/10^14 < pi; comparison with 1/192, ..., 1/205, 1/232,
      1/239, 1/243, 1/246 (printed only).

Numerical check [N] (floating point, NOT a proof): for every box, the integral of
F(theta) = sum over the pairs of E5 of area(P inter (Q - u(theta))) is computed with GEOS
areas, explicit breakpoints (where a vertex of one polygon crosses an edge line of the other,
A is a polynomial of degree 2 in (cos, sin) between breakpoints) and Gauss-Legendre with 10
nodes (6 nodes for an error estimate). Each certified box bound must exceed this integral.
This shows that no contribution is missing from the certificate.

Usage: python3 -B verifier/verify.py LABEL [--dir certificates] [--proc 3]
"""
import sys, json, time, math, argparse, os
from fractions import Fraction as Fr
import multiprocessing as mp
import numpy as np
import shapely

PI_LOW = Fr(314159265358979, 10 ** 14)        # < pi = 3.14159265358979323...
G10 = np.polynomial.legendre.leggauss(10)
G6 = np.polynomial.legendre.leggauss(6)
PAIRS = None
EDGES = None


def fr(s):
    a, b = s.split("/")
    return Fr(int(a), int(b))


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


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


def same_cyclic(P, H):
    if len(P) != len(H):
        return False
    try:
        k = P.index(H[0])
    except ValueError:
        return False
    return all(P[(k + i) % len(P)] == H[i] for i in range(len(P)))


def strictly_convex(P):
    n = len(P)
    turns = n >= 3 and all(cross(P[i], P[(i + 1) % n], P[(i + 2) % n]) > 0 for i in range(n))
    return turns and same_cyclic(list(P), hull(P))


def shoelace(P):
    n = len(P)
    return sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n)) / 2


def edge_separates(P, Q):
    """True if the line of some edge of P (CCW) has all vertices of Q on its closed outer side."""
    n = len(P)
    for k in range(n):
        p0, p1 = P[k], P[(k + 1) % n]
        if all(cross(p0, p1, q) <= 0 for q in Q):
            return True
    return False


def strictly_separated(P, Q):
    """True if the line of some edge of P or Q strictly separates P and Q (equivalent to
    P inter Q empty for convex compact polygons)."""
    for (A, B) in ((P, Q), (Q, P)):
        n = len(A)
        for k in range(n):
            a, b = A[k], A[(k + 1) % n]
            if all(cross(a, b, q) < 0 for q in B):
                return True
    return False


def d2_point_segment(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2
    t = min(max(t, Fr(0)), Fr(1))
    x, y = a[0] + t * dx - p[0], a[1] + t * dy - p[1]
    return x * x + y * y


def dist2(P, Q):
    """Exact squared distance between convex CCW polygons."""
    if not strictly_separated(P, Q):
        return Fr(0)
    best = None
    for (A, B) in ((P, Q), (Q, P)):
        n = len(B)
        for p in A:
            for k in range(n):
                d = d2_point_segment(p, B[k], B[(k + 1) % n])
                if best is None or d < best:
                    best = d
    return best


def bbox(P):
    xs = [p[0] for p in P]
    ys = [p[1] for p in P]
    return min(xs), max(xs), min(ys), max(ys)


def smallest_k(cond):
    k = 1
    while not cond(k):
        k += 1
    return k


# ---------------------------------------------------------------------------
# numerical integration (floating point)
# ---------------------------------------------------------------------------

def breakpoints(P, Q, lo, hi):
    """Angles theta in (lo, hi) at which a vertex of one polygon meets an edge line segment of
    the other (Q - u(theta) versus P)."""
    segs = []
    m, n = len(Q), len(P)
    for k in range(m):
        q0, q1 = Q[k], Q[(k + 1) % m]
        for p in P:
            segs.append((q0 - p, q1 - p))
    for q in Q:
        for k in range(n):
            p0, p1 = P[k], P[(k + 1) % n]
            segs.append((q - p0, q - p1))
    A = np.array([s[0] for s in segs])
    B = np.array([s[1] for s in segs])
    d = B - A
    aa = (d * d).sum(1)
    bb = 2 * (A * d).sum(1)
    cc = (A * A).sum(1) - 1
    disc = bb * bb - 4 * aa * cc
    ok = (disc >= 0) & (aa > 0)
    sq = np.sqrt(np.where(ok, disc, 0))
    th = []
    for sgn in (-1, 1):
        t = (-bb + sgn * sq) / (2 * np.where(aa > 0, aa, 1))
        sel = ok & (t >= -1e-12) & (t <= 1 + 1e-12)
        pts = A[sel] + t[sel, None] * d[sel]
        th.append(np.arctan2(pts[:, 1], pts[:, 0]) % (2 * math.pi))
    th = np.concatenate(th)
    return th[(th > lo) & (th < hi)]


def areas(P, Q, theta):
    u = np.stack([np.cos(theta), np.sin(theta)], 1)
    ring = np.concatenate([Q, Q[:1]], 0)
    polys = shapely.polygons(ring[None, :, :] - u[:, None, :])
    return shapely.area(shapely.intersection(shapely.Polygon(P), polys))


def integrate_pair(idx):
    P, Q = PAIRS[idx]
    edges = EDGES
    br = breakpoints(P, Q, edges[0], edges[-1])
    pts = np.unique(np.concatenate([edges, br]))
    s, e = pts[:-1], pts[1:]
    keep = e - s > 0
    s, e = s[keep], e[keep]
    res = []
    for (x, w) in (G10, G6):
        mid, half = (s + e) / 2, (e - s) / 2
        th = (mid[:, None] + half[:, None] * x[None, :]).ravel()
        A = areas(P, Q, th).reshape(len(s), len(x))
        val = (A * w[None, :]).sum(1) * half
        box = np.searchsorted(edges, mid, side="right") - 1
        acc = np.zeros(len(edges) - 1)
        np.add.at(acc, box, val)
        res.append(acc)
    return idx, res[0], res[1]


# ---------------------------------------------------------------------------

def main():
    global PAIRS, EDGES
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("--dir", default="certificates")
    ap.add_argument("--proc", type=int, default=3)
    a = ap.parse_args()
    t0 = time.time()
    with open(os.path.join(a.dir, f"{a.label}_config.json")) as f:
        C = json.load(f)
    with open(os.path.join(a.dir, f"{a.label}_certificat.json")) as f:
        cert = json.load(f)
    g1 = tuple(fr(z) for z in C["g1"])
    g2 = tuple(fr(z) for z in C["g2"])
    pieces = [([(fr(x), fr(y)) for (x, y) in p["sommets"]], p["couleur"]) for p in C["pieces"]]
    det = g1[0] * g2[1] - g1[1] * g2[0]
    cell = abs(det)
    print(f"=== independent verification of {a.label} : {len(pieces)} pieces ;"
          f" colours {sorted(set(c for _, c in pieces))}", flush=True)

    # E1
    bad = [i for i, (P, c) in enumerate(pieces) if not strictly_convex(P)]
    assert not bad, ("non-convex pieces", bad)
    print(f"  [E1 exact] {len(pieces)}/{len(pieces)} pieces strictly convex, CCW, equal to their hull", flush=True)

    # E2
    S = sum(shoelace(P) for P, _ in pieces)
    assert S == cell == fr(C["aire_cellule"]) == fr(cert["aire_cellule"]), (float(S), float(cell))
    print(f"  [E2 exact] sum of areas = |det(g1,g2)| = cell area = {float(S):.15f}", flush=True)

    # E3
    R2 = max(x * x + y * y for P, _ in pieces for (x, y) in P)
    Rq = Fr(math.isqrt(int(math.ceil(R2 * 10 ** 12))) + 1, 10 ** 6)
    assert Rq * Rq >= R2
    T = 2 * Rq
    N1 = g1[0] ** 2 + g1[1] ** 2
    N2 = g2[0] ** 2 + g2[1] ** 2
    # |a| |C| = |det(g2, t)| <= |t| |g2| <= T |g2| : amax = largest a with (a |C|)^2 <= T^2 N2
    amax = smallest_k(lambda k: (k * cell) ** 2 > T * T * N2) - 1
    bmax = smallest_k(lambda k: (k * cell) ** 2 > T * T * N1) - 1
    bbs = [bbox(P) for P, _ in pieces]
    ntest = 0
    for i, (P, ci) in enumerate(pieces):
        x0, x1, y0, y1 = bbs[i]
        for j, (Q0, cj) in enumerate(pieces):
            X0, X1, Y0, Y1 = bbs[j]
            for aa in range(-amax, amax + 1):
                for bb in range(-bmax, bmax + 1):
                    if aa == 0 and bb == 0 and j <= i:
                        continue
                    tx = aa * g1[0] + bb * g2[0]
                    ty = aa * g1[1] + bb * g2[1]
                    if X0 + tx >= x1 or x0 >= X1 + tx or Y0 + ty >= y1 or y0 >= Y1 + ty:
                        continue      # bounding boxes with disjoint interiors
                    Q = [(x + tx, y + ty) for (x, y) in Q0]
                    ntest += 1
                    assert edge_separates(P, Q) or edge_separates(Q, P), ("OVERLAP", i, j, aa, bb)
    print(f"  [E3 exact] disjoint interiors proved by a separating edge line: {ntest} pairs tested"
          f" (|a|<={amax}, |b|<={bmax}, |t| <= 2 Rmax ~ {float(T):.4f})", flush=True)

    # E4
    allv = [v for P, _ in pieces for v in P]
    dt = lambda g, v: g[0] * v[1] - g[1] * v[0]
    W2 = max(dt(g2, v) for v in allv) - min(dt(g2, v) for v in allv)
    W1 = max(dt(g1, v) for v in allv) - min(dt(g1, v) for v in allv)
    A_s = smallest_k(lambda k: k * cell - W2 > 0 and (k * cell - W2) ** 2 > N2)
    B_s = smallest_k(lambda k: k * cell - W1 > 0 and (k * cell - W1) ** 2 > N1)
    print(f"  [E4 exact] |a| >= {A_s} or |b| >= {B_s} => every pair of points at distance > 1"
          f" (margins (k|C|-W)^2 - |g|^2 = {float((A_s * cell - W2) ** 2 - N2):.4f},"
          f" {float((B_s * cell - W1) ** 2 - N1):.4f})", flush=True)

    # E5
    one = Fr(1)
    pairs = []
    for i, (P, ci) in enumerate(pieces):
        x0, x1, y0, y1 = bbs[i]
        for j, (Q0, cj) in enumerate(pieces):
            if ci != cj:
                continue
            X0, X1, Y0, Y1 = bbs[j]
            for aa in range(-(A_s - 1), A_s):
                for bb in range(-(B_s - 1), B_s):
                    tx = aa * g1[0] + bb * g2[0]
                    ty = aa * g1[1] + bb * g2[1]
                    gx = max(X0 + tx - x1, x0 - X1 - tx, Fr(0))
                    gy = max(Y0 + ty - y1, y0 - Y1 - ty, Fr(0))
                    if gx * gx + gy * gy >= one:
                        continue          # distance >= 1
                    Q = [(x + tx, y + ty) for (x, y) in Q0]
                    if dist2(P, Q) >= one:
                        continue
                    if max((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2 for p in P for q in Q) <= one:
                        continue
                    pairs.append((i, j, aa, bb, P, Q))
    print(f"  [E5 exact] {len(pairs)} pairs of the same colour with dist^2 < 1 < max^2"
          f" [{time.time() - t0:.1f} s]", flush=True)

    # E6
    bx = sorted((fr(b["x0"]), fr(b["x1"]), fr(b["borne_integrale"])) for b in cert["boites"])
    assert bx[0][0] == 0 and bx[-1][1] == 1
    assert all(bx[k][1] == bx[k + 1][0] for k in range(len(bx) - 1)) and all(b[0] < b[1] for b in bx)
    assert all(b[2] > 0 for b in bx)
    tot = sum(b[2] for b in bx)
    assert tot == fr(cert["somme_bornes"])
    pmaj = tot / (PI_LOW * cell)
    lis = fr(cert["p_majorant_lisible"])
    assert pmaj <= lis
    print(f"  [E6 exact] {len(bx)} boxes partition [0, 1] ; sum of bounds = somme_bornes ;"
          f" sum/(pi_low |C|) = {float(pmaj):.12f} <= {lis.numerator}/{lis.denominator}", flush=True)
    for d in (192, 193, 198, 203, 204, 205, 206, 207, 212, 232, 234, 239, 243, 246):
        print(f"      bound < 1/{d} : {lis < Fr(1, d)}   ({lis.numerator}*{d} = {lis.numerator * d}"
              f" vs {lis.denominator})")

    # N
    PAIRS = [(np.array([[float(x), float(y)] for (x, y) in P]),
              np.array([[float(x), float(y)] for (x, y) in Q])) for (_, _, _, _, P, Q) in pairs]
    EDGES = np.array([float(z[0]) for z in bx] + [float(bx[-1][1])]) * math.pi
    bounds = np.array([float(z[2]) for z in bx])
    with mp.Pool(a.proc) as pool:
        R = list(pool.imap_unordered(integrate_pair, range(len(PAIRS)), chunksize=8))
    I10 = np.zeros(len(bx))
    I6 = np.zeros(len(bx))
    for idx, r10, r6 in R:
        I10 += r10
        I6 += r6
    err = np.abs(I10 - I6) + 1e-14 * np.abs(I10) + 1e-16
    margin = bounds - I10
    norm = math.pi * float(cell)
    k = int(np.argmin(margin))
    nviol = int((margin < 0).sum())
    nweak = int((margin < err).sum())
    print(f"  [N float] p (independent integral over [0, pi]) = {I10.sum() / norm:.10f} ;"
          f" |GL10 - GL6| total = {abs(I10.sum() - I6.sum()) / norm:.2e}")
    print(f"  [N float] {len(bx)} boxes ; bound < integral : {nviol} ; margin < error estimate : {nweak} ;"
          f" min margin {margin[k]:.3e} (box {k}) ; max |GL10 - GL6| per box {np.abs(I10 - I6).max():.2e}")
    ok = (nviol == 0 and nweak == 0)
    print(f"  VERDICT {a.label} : exact checks E1-E6 PASSED ; numerical check N {'PASSED' if ok else 'FAILED'} ;"
          f" certified bound p <= {lis.numerator}/{lis.denominator} ; time {time.time() - t0:.1f} s", flush=True)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
