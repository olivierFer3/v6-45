"""recompute.py -- recomputation of a certificate from the JSON files only.

Reads <label>_config.json (exact colouring) and <label>_certificat.json (boxes and bounds),
redoes the exact checks (true convexity, areas, disjointness), recomputes the bound of every
box of the certificate, and checks that sum / (pi |C|) <= the announced upper bound.

This is a RECOMPUTATION with the same library as the certifier, not an independent check.
The independent check is verifier/verify.py.

Usage: python3 -B certifier/recompute.py LABEL [--dir certificates] [--proc 3]
"""
import sys, os, json, time, argparse
import multiprocessing as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flint import fmpq, arb
import geometry as L
import core as K
from colourings import Config

PAIRS = None


def pq(s):
    a, b = s.split("/")
    return fmpq(int(a), int(b))


def work(b):
    x0, x1 = pq(b["x0"]), pq(b["x1"])
    v, _ = K.box_bound(PAIRS, x0, x1)
    return b["x0"], b["x1"], v <= pq(b["borne_integrale"]), f"{int(v.p)}/{int(v.q)}"


def main():
    global PAIRS
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("--dir", default="certificates")
    ap.add_argument("--proc", type=int, default=3)
    a = ap.parse_args()
    t = time.time()
    with open(os.path.join(a.dir, f"{a.label}_config.json")) as f:
        C = json.load(f)
    with open(os.path.join(a.dir, f"{a.label}_certificat.json")) as f:
        cert = json.load(f)
    g1 = tuple(pq(z) for z in C["g1"])
    g2 = tuple(pq(z) for z in C["g2"])
    pieces = [([(pq(x), pq(y)) for (x, y) in p["sommets"]], p["couleur"]) for p in C["pieces"]]
    cfg = Config(C["nom"], g1, g2, pieces, {})
    assert cfg.cell_area == pq(cert["aire_cellule"]) == pq(C["aire_cellule"])
    print(f"=== recomputation {a.label} : {len(pieces)} pieces read", flush=True)
    K.verify(cfg)
    PAIRS = K.enumerate_pairs(cfg)
    # the boxes cover [0, 1] exactly, without gap or overlap
    bx = sorted(((pq(b["x0"]), pq(b["x1"])) for b in cert["boites"]))
    assert bx[0][0] == 0 and bx[-1][1] == 1 and all(bx[i][1] == bx[i + 1][0] for i in range(len(bx) - 1))
    assert all(x0 < x1 for (x0, x1) in bx)
    print(f"  {len(bx)} boxes : exact partition of [0, pi]", flush=True)
    with mp.Pool(a.proc) as pool:
        R = list(pool.imap_unordered(work, cert["boites"], chunksize=4))
    assert all(r[2] for r in R), "a recomputed bound exceeds the bound of the certificate"
    tot = sum((pq(b["borne_integrale"]) for b in cert["boites"]), fmpq(0))
    assert tot == pq(cert["somme_bornes"])
    p = arb(tot) / (arb.pi() * arb(cfg.cell_area))
    ph = L.fmpq_upper(p)
    lis = pq(cert["p_majorant_lisible"])
    assert ph <= lis
    print(f"  all box bounds recomputed (<= certificate) ; p <= {cert['p_majorant_lisible']}"
          f" = {float(lis):.10f} CONFIRMED ; < 1/192 : {lis < fmpq(1, 192)} ; < 1/198 : {lis < fmpq(1, 198)} ;"
          f" < 1/203 : {lis < fmpq(1, 203)} ; < 1/205 : {lis < fmpq(1, 205)} ; < 1/232 : {lis < fmpq(1, 232)} ;"
          f" < 1/239 : {lis < fmpq(1, 239)} ; < 1/243 : {lis < fmpq(1, 243)} ; < 1/246 : {lis < fmpq(1, 246)} ; time {time.time() - t:.1f} s", flush=True)


if __name__ == "__main__":
    main()
