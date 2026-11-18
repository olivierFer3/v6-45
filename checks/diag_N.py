"""diag_N.py LABEL DIR [VERIFY_PY] -- diagnostic of an alert of the floating-point check N of
verifier/verify.py (imported read-only, unmodified): reruns N serially, then recomputes the integral of each box
with Gauss-Legendre rules of 20 and 30 nodes and prints, for the boxes whose margin is below the error estimate
of N, the certified bound, I10, I20, I30 and the relative margins. Floating point only: NOT a proof.
Used for ILEP_S7_93 (boxes 263 and 264)."""
import sys, json, os, importlib.util
from fractions import Fraction as Fr
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
lab, d = sys.argv[1], sys.argv[2]
REF = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "..", "verifier", "verify.py")
spec = importlib.util.spec_from_file_location("verify_ref", REF)
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
class SerialPool:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def imap_unordered(self, f, it, chunksize=1): return map(f, it)
V.mp.Pool = SerialPool
sys.argv = ["verify.py", lab, "--dir", d, "--proc", "1"]
try:
    V.main()
except SystemExit as e:
    print("  (verify.main exit code", e.code, ")")
cert = json.load(open(os.path.join(d, f"{lab}_certificat.json")))
bx = sorted((Fr(b["x0"]), Fr(b["x1"]), Fr(b["borne_integrale"])) for b in cert["boites"])
bounds = np.array([float(z[2]) for z in bx])
def run(n1, n2):
    V.G10 = np.polynomial.legendre.leggauss(n1); V.G6 = np.polynomial.legendre.leggauss(n2)
    I1 = np.zeros(len(bx)); I2 = np.zeros(len(bx))
    for i in range(len(V.PAIRS)):
        _, a, b = V.integrate_pair(i); I1 += a; I2 += b
    return I1, I2
I10, I6 = run(10, 6)
err = np.abs(I10 - I6) + 1e-14 * np.abs(I10) + 1e-16
weak = np.where(bounds - I10 < err)[0]
I30, I20 = run(30, 20)
print("weak boxes:", weak.tolist())
for k in weak:
    print(f" box {k} [{bx[k][0]}, {bx[k][1]}] bound={bounds[k]:.17e} I10={I10[k]:.17e} I20={I20[k]:.17e} I30={I30[k]:.17e}")
    print(f"   margin rel (bound-I30)/bound = {(bounds[k]-I30[k])/bounds[k]:.3e} ; |I10-I6|={abs(I10[k]-I6[k]):.2e} |I30-I20|={abs(I30[k]-I20[k]):.2e}")
m = (bounds - I30) / bounds
print(f"all boxes: min rel margin vs GL30 = {m.min():.3e} (box {int(m.argmin())}) ; boxes with bound < I30 : {int((bounds < I30).sum())}")
print(f"median rel margin = {np.median(m):.3e} ; boxes with rel margin < 1e-10 : {int((m < 1e-10).sum())}")
