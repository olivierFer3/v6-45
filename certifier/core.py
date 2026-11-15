"""core.py -- exact checks of a colouring, enumeration of the contributing pairs,
floating-point evaluation (exploration only) and certified upper bound on a box of angles.

Convention: theta is measured in units of pi (x = theta/pi in [0, 1]) for the box endpoints,
which are therefore exact rationals.
"""
import math
from flint import fmpq, arb
import geometry as L


# ---------------------------------------------------------------------------
# 1. exact checks
# ---------------------------------------------------------------------------

def translation_bounds(cfg, radius):
    """Integers amax, bmax such that |a g1 + b g2| <= radius implies |a| <= amax, |b| <= bmax.
    (The component of a g1 + b g2 orthogonal to g2 has length |a| area/|g2|; same for b.)"""
    g1, g2, A = cfg.g1, cfg.g2, cfg.cell_area
    n1 = g1[0] ** 2 + g1[1] ** 2
    n2 = g2[0] ** 2 + g2[1] ** 2
    r2 = radius * radius
    amax = 0
    while (amax + 1) ** 2 * A * A <= r2 * n2:
        amax += 1
    bmax = 0
    while (bmax + 1) ** 2 * A * A <= r2 * n1:
        bmax += 1
    return amax, bmax


def ball(P):
    """Rational centre (mean of the vertices) and rational upper bound of the radius."""
    n = len(P)
    cx = sum(p[0] for p in P) / n
    cy = sum(p[1] for p in P) / n
    r2 = max((p[0] - cx) ** 2 + (p[1] - cy) ** 2 for p in P)
    r = L.rational(math.sqrt(float(r2)) + 1e-9, 10 ** 12)
    assert r * r >= r2
    return (cx, cy), r


def radius_bound(balls, extra):
    """Rational radius >= extra + max |z_i - z_j| + 2 max r_i (exact: square root bounded
    from above, then checked)."""
    dz2 = max((z1[0] - z2[0]) ** 2 + (z1[1] - z2[1]) ** 2 for (z1, _) in balls for (z2, _) in balls)
    dz = L.rational(math.sqrt(float(dz2)) + 1e-9, 10 ** 12)
    assert dz * dz >= dz2
    return extra + dz + 2 * max(r for (_, r) in balls)


def verify(cfg, log=print):
    """Exact proofs: the pieces are strictly convex (true convexity test), the sum of their
    areas equals the area of the cell, and the G-translates of the pieces have pairwise
    disjoint interiors. (The last two facts imply that the G-translates of the pieces
    partition the plane up to a null set.)"""
    for (P, c) in cfg.pieces:
        assert L.is_strictly_convex(P), "piece not strictly convex"
    S = sum(L.area(P) for (P, c) in cfg.pieces)
    assert S == cfg.cell_area, (S, cfg.cell_area)
    log(f"  [exact] {len(cfg.pieces)} convex pieces (true convexity: equal to their hull) ;"
        f" sum of areas = |C| = {float(S):.15f}")
    balls = [ball(P) for (P, c) in cfg.pieces]
    # two pieces can meet only if |z_i + g - z_j| <= r_i + r_j ; bound |g|
    radius = radius_bound(balls, 0)
    amax, bmax = translation_bounds(cfg, radius)
    nchk = 0
    for i, (P, ci) in enumerate(cfg.pieces):
        for j, (Q0, cj) in enumerate(cfg.pieces):
            for a in range(-amax, amax + 1):
                for b in range(-bmax, bmax + 1):
                    if a == 0 and b == 0 and j <= i:
                        continue
                    t = (a * cfg.g1[0] + b * cfg.g2[0], a * cfg.g1[1] + b * cfg.g2[1])
                    (zi, ri), (zj, rj) = balls[i], balls[j]
                    dx, dy = zj[0] + t[0] - zi[0], zj[1] + t[1] - zi[1]
                    if dx * dx + dy * dy > (ri + rj) ** 2:
                        continue
                    Q = L.translate(Q0, t)
                    S2, _ = L.intersection(P, Q)
                    nchk += 1
                    if len(S2) >= 3:
                        assert L.area(S2) == 0, ("overlap", i, j, a, b)
    log(f"  [exact] disjoint interiors: {nchk} pairs of neighbouring pieces tested (|a|<={amax}, |b|<={bmax})")
    return True


# ---------------------------------------------------------------------------
# 2. pairs (representative piece P, translate Q of the same colour) that can contribute
# ---------------------------------------------------------------------------

class Pair:
    __slots__ = ("P", "Q", "par", "span", "always", "Pf", "Qf")


def angle_arb(v, ref):
    """Angle (arb ball, radians) of v relative to the direction ref, in (-pi, pi)."""
    cr = arb(ref[0] * v[1] - ref[1] * v[0])
    dt = arb(ref[0] * v[0] + ref[1] * v[1])
    return arb.atan2(cr, dt)


def enumerate_pairs(cfg, log=print):
    balls = [ball(P) for (P, c) in cfg.pieces]
    radius = radius_bound(balls, 1)
    amax, bmax = translation_bounds(cfg, radius)
    pairs = []
    npi = arb.pi()
    for i, (P, ci) in enumerate(cfg.pieces):
        mP = L.negate(P)
        for j, (Q0, cj) in enumerate(cfg.pieces):
            if ci != cj:
                continue
            for a in range(-amax, amax + 1):
                for b in range(-bmax, bmax + 1):
                    t = (a * cfg.g1[0] + b * cfg.g2[0], a * cfg.g1[1] + b * cfg.g2[1])
                    (zi, ri), (zj, rj) = balls[i], balls[j]
                    dx, dy = zj[0] + t[0] - zi[0], zj[1] + t[1] - zi[1]
                    if dx * dx + dy * dy > (1 + ri + rj) ** 2:
                        continue        # |x - (x+u)| = 1 impossible
                    Q = L.translate(Q0, t)
                    M = L.minkowski(Q, mP)      # the u with P inter (Q-u) non-empty
                    d2 = L.dist2_origin_polygon(M)
                    m2 = L.max2_origin_polygon(M)
                    if not (d2 < 1 < m2):
                        continue        # the unit circle does not meet the interior of M
                    pr = Pair()
                    pr.P, pr.Q = P, Q
                    pr.par = L.parallel_edges(P, Q)
                    pr.Pf = [(float(x), float(y)) for (x, y) in P]
                    pr.Qf = [(float(x), float(y)) for (x, y) in Q]
                    if d2 == 0:
                        pr.always = True
                        pr.span = None
                    else:
                        pr.always = False
                        n = len(M)
                        ref = (sum(p[0] for p in M) / n, sum(p[1] for p in M) / n)  # inside M
                        angs = [angle_arb(v, ref) for v in M]
                        phi = arb.atan2(arb(ref[1]), arb(ref[0]))
                        lo_q = min(L.fmpq_lower(z) for z in angs)
                        hi_q = max(L.fmpq_upper(z) for z in angs)
                        # in units of pi: [ (phi+lo)/pi , (phi+hi)/pi ], rigorously widened
                        a0 = L.fmpq_lower((phi + arb(lo_q)) / npi)
                        a1 = L.fmpq_upper((phi + arb(hi_q)) / npi)
                        pr.span = (a0, a1)
                    pairs.append(pr)
    log(f"  {len(pairs)} pairs (P, Q) of the same colour whose support meets the unit circle"
        f" (translations |a|<={amax}, |b|<={bmax})")
    return pairs


def active(pr, x0, x1):
    """Can the pair contribute for theta/pi in [x0, x1]? (rigorous test, by excess)"""
    if pr.always:
        return True
    a0, a1 = pr.span
    for k in (-4, -2, 0, 2, 4):
        if not (x1 < a0 + k or x0 > a1 + k):
            return True
    return False


# ---------------------------------------------------------------------------
# 3. floating-point evaluation (exploration only, no role in the proof)
# ---------------------------------------------------------------------------

def F_float(pairs, theta):
    u = (math.cos(theta), math.sin(theta))
    x = theta / math.pi
    tot = 0.0
    for pr in pairs:
        if not active_float(pr, x):
            continue
        Qu = L.translate(pr.Qf, (-u[0], -u[1]))
        S, _ = L.intersection(pr.Pf, Qu)
        if len(S) >= 3:
            tot += L.area(S)
    return tot


def active_float(pr, x):
    if pr.always:
        return True
    a0, a1 = float(pr.span[0]), float(pr.span[1])
    for k in (-4, -2, 0, 2, 4):
        if a0 + k - 1e-9 <= x <= a1 + k + 1e-9:
            return True
    return False


def p_float(cfg, pairs, n=512):
    """(1/(pi |C|)) int_0^pi F, midpoint rule with n points (exploration)."""
    h = math.pi / n
    s = sum(F_float(pairs, (k + 0.5) * h) for k in range(n))
    return s * h / (math.pi * float(cfg.cell_area))


# ---------------------------------------------------------------------------
# 4. certified upper bound of int_{x0 pi}^{x1 pi} F(theta) d theta
# ---------------------------------------------------------------------------

def arc_rectangle(t0, t1):
    """Rational rectangle K containing the arc {u(theta), theta in [t0, t1]} (t0 < t1 arb balls,
    0 <= t0, t1 <= pi). cos is decreasing on [0, pi]; sin is monotone on [0, pi/2] and on
    [pi/2, pi], with maximum 1 at pi/2."""
    c0, c1 = t0.cos(), t1.cos()
    s0, s1 = t0.sin(), t1.sin()
    xlo, xhi = L.fmpq_lower(c1), L.fmpq_upper(c0)
    ylo = min(L.fmpq_lower(s0), L.fmpq_lower(s1))
    pi2 = arb.pi() / 2
    if (t1 < pi2) or (t0 > pi2):
        yhi = max(L.fmpq_upper(s0), L.fmpq_upper(s1))
    else:
        yhi = fmpq(1)
    return [(xlo, ylo), (xhi, ylo), (xhi, yhi), (xlo, yhi)]


def box_bound(pairs, x0, x1, quad_threshold=0.05, stats=None):
    """Rigorous upper bound (upper end of an arb ball) of int F over theta in [x0 pi, x1 pi].
    Returns (rational upper bound, floating-point midpoint estimate)."""
    npi = arb.pi()
    t0, t1 = arb(x0) * npi, arb(x1) * npi
    h_f = float(x1 - x0) * math.pi
    mo = L.moments(t0, t1)                 # h, Ic, Is, Icc, Iss, Ics
    mof = [float(z.mid()) for z in mo]
    act = [pr for pr in pairs if active(pr, x0, x1)]
    # rational anchor point u0 (arbitrary: (M1) holds for every u0); chosen near the mean of u
    # over the arc so that the linear term nearly cancels
    ux = mof[1] / mof[0]
    uy = mof[2] / mof[0]
    attempt = 0
    while True:
        u0 = (L.rational(ux + attempt * 1.3e-9, 2 ** 40), L.rational(uy - attempt * 0.7e-9, 2 ** 40))
        if all(L.is_regular(pr.par, u0) for pr in act):
            break
        attempt += 1
    x0q, y0q = u0
    # centred moments: d = u - u0 ; J1x = int (c - x0q), ..., Jxx = int (c - x0q)^2, ...
    h, Ic, Is, Icc, Iss, Ics = mo
    ax, ay = arb(x0q), arb(y0q)
    J1x = Ic - ax * h
    J1y = Is - ay * h
    Jxx = Icc - 2 * ax * Ic + ax * ax * h
    Jyy = Iss - 2 * ay * Is + ay * ay * h
    Jxy = Ics - ax * Is - ay * Ic + ax * ay * h
    jf = [float(z.mid()) for z in (J1x, J1y, Jxx, Jyy, Jxy)]
    S0 = fmpq(0)
    SGx, SGy = fmpq(0), fmpq(0)
    Mxx, Mxy, Myy = fmpq(0), fmpq(0), fmpq(0)
    Smink = fmpq(0)          # sum of the (M2) areas, to be multiplied by h
    K = None
    est = 0.0
    nm1 = nm2 = 0
    for pr in act:
        A0, (gx, gy) = L.area_and_gradient(pr.P, pr.Q, u0)
        est += float(A0) * h_f
        use_m2 = (A0 == 0)
        if not use_m2:
            quad = (float(gx) ** 2 * jf[2] + float(gy) ** 2 * jf[3] + 2 * float(gx) * float(gy) * jf[4]) / (4 * float(A0))
            if quad > quad_threshold * float(A0) * h_f:
                # compare with (M2)
                if K is None:
                    K = arc_rectangle(t0, t1)
                QK = L.minkowski(pr.Q, L.negate(K))
                S, _ = L.intersection(pr.P, QK)
                am = L.area(S) if len(S) >= 3 else fmpq(0)
                b1 = float(A0) * h_f + float(gx) * jf[0] + float(gy) * jf[1] + quad
                if float(am) * h_f < b1:
                    Smink += am
                    nm2 += 1
                    continue
            S0 += A0
            SGx += gx
            SGy += gy
            inv = 1 / (4 * A0)
            Mxx += gx * gx * inv
            Mxy += gx * gy * inv
            Myy += gy * gy * inv
            nm1 += 1
        else:
            if K is None:
                K = arc_rectangle(t0, t1)
            QK = L.minkowski(pr.Q, L.negate(K))
            S, _ = L.intersection(pr.P, QK)
            if len(S) >= 3:
                Smink += L.area(S)
            nm2 += 1
    B = (arb(S0) * h + arb(SGx) * J1x + arb(SGy) * J1y
         + arb(Mxx) * Jxx + 2 * arb(Mxy) * Jxy + arb(Myy) * Jyy + arb(Smink) * h)
    if stats is not None:
        stats["active"] = len(act)
        stats["M1"] = nm1
        stats["M2"] = nm2
        stats["u0_attempts"] = attempt
    return L.fmpq_upper(B), est
