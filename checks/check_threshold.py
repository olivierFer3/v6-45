"""check_threshold.py LABEL DIR DEN -- exact check (fractions.Fraction, no python-flint) of the final
arithmetic of a certificate against the threshold 1/DEN: the boxes partition [0, 1], their bounds sum to
"somme_bornes", the cell area is |det(g1, g2)|, S/(pi_low |C|) <= p_majorant_lisible and
DEN * p_majorant_lisible < 1. Also prints which of the bounds B(n) >= u(n) of verifier/u_bounds.py are beaten.

Example: python3 -B checks/check_threshold.py ILEP_S6A certificates 239
"""
import sys, json, os
from fractions import Fraction as Fr

lab, d, den = sys.argv[1], sys.argv[2], int(sys.argv[3])
c = json.load(open(os.path.join(d, f"{lab}_certificat.json")))
cfg = json.load(open(os.path.join(d, f"{lab}_config.json")))
PI_LOW = Fr(314159265358979, 10 ** 14)
boxes = sorted((Fr(b["x0"]), Fr(b["x1"]), Fr(b["borne_integrale"])) for b in c["boites"])
assert boxes[0][0] == 0 and boxes[-1][1] == 1 and all(boxes[i][1] == boxes[i + 1][0] for i in range(len(boxes) - 1))
S = sum(b[2] for b in boxes)
assert S == Fr(c["somme_bornes"])
g1 = [Fr(x) for x in cfg["g1"]]; g2 = [Fr(x) for x in cfg["g2"]]
A = abs(g1[0] * g2[1] - g1[1] * g2[0])
assert A == Fr(cfg["aire_cellule"]) == Fr(c["aire_cellule"])
bound = S / (PI_LOW * A)
read = Fr(c["p_majorant_lisible"])
ok1 = bound <= read; ok2 = den * read < 1
print(f"{lab}: {len(boxes)} boxes ; S/(pi_low |C|) = {float(bound):.10f} <= readable {read} = {float(read):.10f} : {ok1}")
print(f"  {den} * readable = {float(den * read):.10f} < 1 : {ok2}")
e6 = -(-1 // read)   # ceil(1/readable): a non-5-colourable graph has at least this many edges
print(f"  ceil(1/readable) = {e6}  (=> e6 >= {e6})")
U = {45: 205, 46: 212, 47: 218, 48: 225, 49: 232, 50: 239, 51: 246, 52: 254}   # B(n) >= u(n), verifier/u_bounds.py
for n, un in U.items():
    print(f"  {un} * readable < 1 : {un * read < 1}   (=> e6 > {un} >= u({n}) => v6 >= {n + 1})")
print("THRESHOLD_OK" if ok1 and ok2 else "THRESHOLD_FAILED")
sys.exit(0 if ok1 and ok2 else 1)
