"""compare_pairs.py LABEL DIR [VERIFY_PY] -- exact comparison of the SET of pairs (P, Q) enumerated by the
certifier (certifier/core.enumerate_pairs, used for the Arb box bounds) with the set E5 of the second verifier
(its E4+E5 loop re-executed with the verifier's own helper functions). Requires python-flint."""
import sys, os, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "certifier"))
from fractions import Fraction as Fr
import core as K
from colourings import Config
from flint import fmpq
label, d = sys.argv[1], sys.argv[2]
REF = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "..", "verifier", "verify.py")
spec = importlib.util.spec_from_file_location("verify_ref", REF)
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
C = json.load(open(os.path.join(d, f"{label}_config.json")))
pq = lambda s: fmpq(*map(int, s.split("/")))
g1 = tuple(pq(z) for z in C["g1"]); g2 = tuple(pq(z) for z in C["g2"])
pieces = [([(pq(x), pq(y)) for (x, y) in p["sommets"]], p["couleur"]) for p in C["pieces"]]
cfg = Config(C["nom"], g1, g2, pieces, {})
key = lambda P: tuple((str(x), str(y)) for (x, y) in P)
A = {(key(pr.P), key(pr.Q)) for pr in K.enumerate_pairs(cfg)}
# E5 of the original verifier (same code as verify.py main, E4+E5)
g1f = tuple(V.fr(z) for z in C["g1"]); g2f = tuple(V.fr(z) for z in C["g2"])
pf = [([(V.fr(x), V.fr(y)) for (x, y) in p["sommets"]], p["couleur"]) for p in C["pieces"]]
cell = abs(g1f[0] * g2f[1] - g1f[1] * g2f[0]); N1 = g1f[0]**2 + g1f[1]**2; N2 = g2f[0]**2 + g2f[1]**2
allv = [v for P, _ in pf for v in P]; dt = lambda g, v: g[0] * v[1] - g[1] * v[0]
W2 = max(dt(g2f, v) for v in allv) - min(dt(g2f, v) for v in allv)
W1 = max(dt(g1f, v) for v in allv) - min(dt(g1f, v) for v in allv)
A_s = V.smallest_k(lambda k: k * cell - W2 > 0 and (k * cell - W2) ** 2 > N2)
B_s = V.smallest_k(lambda k: k * cell - W1 > 0 and (k * cell - W1) ** 2 > N1)
bbs = [V.bbox(P) for P, _ in pf]; one = Fr(1); B = set()
fk = lambda P: tuple((f"{x.numerator}/{x.denominator}" if x.denominator != 1 else f"{x.numerator}",
                      f"{y.numerator}/{y.denominator}" if y.denominator != 1 else f"{y.numerator}") for (x, y) in P)
for i, (P, ci) in enumerate(pf):
    x0, x1, y0, y1 = bbs[i]
    for j, (Q0, cj) in enumerate(pf):
        if ci != cj: continue
        X0, X1, Y0, Y1 = bbs[j]
        for aa in range(-(A_s - 1), A_s):
            for bb in range(-(B_s - 1), B_s):
                tx = aa * g1f[0] + bb * g2f[0]; ty = aa * g1f[1] + bb * g2f[1]
                gx = max(X0 + tx - x1, x0 - X1 - tx, Fr(0)); gy = max(Y0 + ty - y1, y0 - Y1 - ty, Fr(0))
                if gx * gx + gy * gy >= one: continue
                Q = [(x + tx, y + ty) for (x, y) in Q0]
                if V.dist2(P, Q) >= one: continue
                if max((q[0]-p[0])**2 + (q[1]-p[1])**2 for p in P for q in Q) <= one: continue
                B.add((fk(P), fk(Q)))
print(f"{label}: certifier pairs {len(A)} ; verifier E5 pairs {len(B)} ; A-B {len(A-B)} ; B-A {len(B-A)} ; EQUAL {A == B}")
