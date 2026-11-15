"""geometry.py -- exact geometry of convex polygons and ball-arithmetic helpers.

Polygons are lists of vertices (x, y) in counter-clockwise (CCW) order. The functions are
generic: they work over any ordered field (flint.fmpq for the certification, float for
exploration and step choices).

Two upper bounds are used by core.py (proofs: note, Section 4):

 (M1) concavity bound (Brunn-Minkowski): g = sqrt(A_PQ) is concave on its support; if A_PQ is
      differentiable at u0 with A0 = A_PQ(u0) > 0 and G = grad A_PQ(u0), then for EVERY u
          A_PQ(u) <= A0 + G.(u-u0) + (G.(u-u0))^2 / (4 A0).
 (M2) Minkowski bound: if K contains the arc {u(theta), theta in I}, then for theta in I,
          A_PQ(u(theta)) <= area(P inter (Q + (-K))).
"""
from flint import fmpq, arb, ctx

ctx.prec = 256

# ---------------------------------------------------------------------------
# convex polygons
# ---------------------------------------------------------------------------


def area(P):
    """Signed area (shoelace formula)."""
    n = len(P)
    s = 0
    for i in range(n):
        x0, y0 = P[i]
        x1, y1 = P[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return s / 2


def translate(P, t):
    return [(x + t[0], y + t[1]) for (x, y) in P]


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def hull(points):
    """Convex hull (Andrew's monotone chain), CCW, without collinear points."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def all_left_turns(P):
    """All consecutive turns strictly positive. NOT sufficient for convexity on its own
    (a pentagram passes); see is_strictly_convex."""
    n = len(P)
    return n >= 3 and all(cross(P[i], P[(i + 1) % n], P[(i + 2) % n]) > 0 for i in range(n))


def equals_cyclically(P, H):
    if len(P) != len(H):
        return False
    try:
        k = P.index(H[0])
    except ValueError:
        return False
    return all(P[(k + i) % len(P)] == H[i] for i in range(len(P)))


def is_strictly_convex(P):
    """True strict convexity test (exact): all turns strictly positive AND P equals its convex
    hull up to a cyclic rotation. This rejects star polygons (winding number > 1)."""
    return all_left_turns(P) and equals_cyclically(list(P), hull(P))


def minkowski(P, Q):
    """Minkowski sum P + Q of two convex polygons."""
    return hull([(p[0] + q[0], p[1] + q[1]) for p in P for q in Q])


def negate(P):
    return [(-x, -y) for (x, y) in P]


def half_planes(P):
    """Half-planes of the CCW convex polygon P: list of (a, b, c) with P = {a x + b y <= c}."""
    n = len(P)
    L = []
    for i in range(n):
        (x0, y0), (x1, y1) = P[i], P[(i + 1) % n]
        a, b = y1 - y0, x0 - x1          # outward normal (not normalised)
        L.append((a, b, a * x0 + b * y0))
    return L


def clip(P, tags, a, b, c, new_tag):
    """Sutherland-Hodgman: P inter {a x + b y <= c}. tags[i] = label of the edge
    P[i] -> P[i+1]. Returns (vertices, tags)."""
    n = len(P)
    out, otag = [], []
    for i in range(n):
        p, q = P[i], P[(i + 1) % n]
        dp = a * p[0] + b * p[1] - c
        dq = a * q[0] + b * q[1] - c
        if dp <= 0:
            out.append(p)
            otag.append(tags[i])
            if dq > 0:      # leaving: exit point, then an edge on the clipping line
                t = dp / (dp - dq)
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
                otag.append(new_tag)
        elif dq <= 0:       # entering
            t = dp / (dp - dq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
            otag.append(tags[i])
    return out, otag


def intersection(P, Q):
    """P inter Q (convex). Returns (vertices, tags); tag 0 = edge carried by the boundary of P,
    tag 1 = edge carried by the boundary of Q."""
    S, T = list(P), [0] * len(P)
    for (a, b, c) in half_planes(Q):
        if not S:
            break
        S, T = clip(S, T, a, b, c, 1)
    return S, T


def area_and_gradient(P, Q, u):
    """A(u) = area(P inter (Q-u)) and grad_u A = sum, over the edges of P inter (Q-u) carried
    by the boundary of P, of (outward normal x length) = (dy, -dx). (Valid when A is
    differentiable at u; see is_regular.)"""
    Qu = translate(Q, (-u[0], -u[1]))
    S, T = intersection(P, Qu)
    if len(S) < 3:
        return 0, (0, 0)
    A = area(S)
    gx, gy = 0, 0
    n = len(S)
    for i in range(n):
        if T[i] == 0:
            (x0, y0), (x1, y1) = S[i], S[(i + 1) % n]
            gx += y1 - y0
            gy -= x1 - x0
    return A, (gx, gy)


def parallel_edges(P, Q):
    """List of (a, b, cP, cQ): an edge of P and an edge of Q carried by parallel lines
    a x + b y = cP and a x + b y = cQ (same normal up to a factor). A(u) can fail to be
    differentiable at u only if, for one of them, a ux + b uy = cQ - cP."""
    out = []
    for (a, b, c) in half_planes(P):
        for (a2, b2, c2) in half_planes(Q):
            if a * b2 - b * a2 == 0:
                # same line direction; normalise (a2, b2) onto (a, b)
                if a != 0:
                    k = a2 / a
                else:
                    k = b2 / b
                out.append((a, b, c, c2 / k))
    return out


def is_regular(par, u):
    """Exact sufficient condition for differentiability of A at u: no pair of parallel edges
    becomes collinear. Line of Q-u: a x + b y = cQ - (a ux + b uy)."""
    for (a, b, cP, cQ) in par:
        if cQ - (a * u[0] + b * u[1]) == cP:
            return False
    return True


def dist2_origin_polygon(P):
    """Squared distance from the origin to the convex polygon P (0 if the origin is in P)."""
    n = len(P)
    inside = all(cross(P[i], P[(i + 1) % n], (0, 0)) >= 0 for i in range(n))
    if inside:
        return 0
    best = None
    for i in range(n):
        p, q = P[i], P[(i + 1) % n]
        dx, dy = q[0] - p[0], q[1] - p[1]
        L2 = dx * dx + dy * dy
        t = -(p[0] * dx + p[1] * dy) / L2
        if t < 0:
            t = 0
        elif t > 1:
            t = 1
        x, y = p[0] + t * dx, p[1] + t * dy
        d = x * x + y * y
        if best is None or d < best:
            best = d
    return best


def max2_origin_polygon(P):
    return max(x * x + y * y for (x, y) in P)


# ---------------------------------------------------------------------------
# convex subtraction: P \ K as disjoint convex pieces
# ---------------------------------------------------------------------------

def subtract(P, K):
    """P \\ K (P, K convex) = disjoint union of the pieces
    P inter {l_k > 0} inter {l_j <= 0, j < k} (l_j = j-th half-plane of K).
    Returns the pieces of positive area (closed polygons; boundaries are null sets)."""
    pieces = []
    rest = list(P)
    for (a, b, c) in half_planes(K):
        if len(rest) < 3:
            break
        outside, _ = clip(rest, [0] * len(rest), -a, -b, -c, 0)   # {a x + b y >= c}
        outside = clean(outside)
        if len(outside) >= 3 and area(outside) > 0:
            pieces.append(outside)
        rest, _ = clip(rest, [0] * len(rest), a, b, c, 0)
        rest = clean(rest)
    return pieces


def clean(P):
    """Remove repeated consecutive vertices and collinear vertices (exact)."""
    Q = []
    for p in P:
        if not Q or Q[-1] != p:
            Q.append(p)
    if len(Q) > 1 and Q[0] == Q[-1]:
        Q.pop()
    changed = True
    while changed and len(Q) >= 3:
        changed = False
        n = len(Q)
        for i in range(n):
            if cross(Q[i - 1], Q[i], Q[(i + 1) % n]) == 0:
                Q.pop(i)
                changed = True
                break
    return Q


# ---------------------------------------------------------------------------
# arb: moments over an arc, and rationals
# ---------------------------------------------------------------------------

def moments(t0, t1):
    """Exact integrals (arb balls) over [t0, t1] (arb balls) of
    1, cos, sin, cos^2, sin^2, cos sin."""
    c0, s0 = t0.cos(), t0.sin()
    c1, s1 = t1.cos(), t1.sin()
    h = t1 - t0
    d2 = (2 * t1).sin() - (2 * t0).sin()
    return (h, s1 - s0, c0 - c1, h / 2 + d2 / 4, h / 2 - d2 / 4, (s1 * s1 - s0 * s0) / 2)


def fmpq_upper(x):
    """A rational >= every point of the arb ball x (exact upper bound)."""
    m, e = x.upper().man_exp()
    m, e = int(m), int(e)
    return fmpq(m * 2 ** e) if e >= 0 else fmpq(m, 2 ** (-e))


def fmpq_lower(x):
    """A rational <= every point of the arb ball x (exact lower bound)."""
    m, e = x.lower().man_exp()
    m, e = int(m), int(e)
    return fmpq(m * 2 ** e) if e >= 0 else fmpq(m, 2 ** (-e))


def rational(x, den=10 ** 12):
    """Rational p/den close to the float x (used to choose points; no role in the proof)."""
    return fmpq(int(round(x * den)), den)
