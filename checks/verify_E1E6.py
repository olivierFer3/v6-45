"""verify_E1E6.py LABEL DIR [VERIFY_PY] -- run a verifier/verify.py (by default the one of this repository;
for version 1, extract it with `git show v1:verifier/verify.py > verify_v1.py`) unmodified, imported as a
module, on a certificate, stopping right after E6: the floating-point check N is skipped by replacing
multiprocessing.Pool with a stub that raises. Also prints the comparisons with 1/205, ..., 1/246 and checks that
the colours are in {0, ..., 4}. Used to run the verifier of version 1 on the version-2 certificates."""
import sys, importlib.util, json, os
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__))
label, d = sys.argv[1], sys.argv[2]
REF = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "..", "verifier", "verify.py")
spec = importlib.util.spec_from_file_location("verify_ref", REF)
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
class StopAfterE6(Exception): pass
class _P:
    def __init__(self, *a, **k): raise StopAfterE6()
V.mp.Pool = _P
sys.argv = ["verify.py", label, "--dir", d, "--proc", "1"]
try:
    V.main()
except StopAfterE6:
    print("  [check] verify.py: E1-E6 completed without assertion failure (N skipped)")
C = json.load(open(os.path.join(d, f"{label}_config.json")))
cert = json.load(open(os.path.join(d, f"{label}_certificat.json")))
cols = sorted(set(p["couleur"] for p in C["pieces"])); assert set(cols) <= {0, 1, 2, 3, 4}, cols
lis = V.fr(cert["p_majorant_lisible"])
for dd in (205, 212, 218, 225, 232, 239, 246):
    print(f"  [check] p_majorant_lisible < 1/{dd} : {lis < Fr(1, dd)}")
