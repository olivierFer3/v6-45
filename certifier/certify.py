"""certify.py -- certification of an upper bound p <= a/b for an exact colouring.

Usage:
  python3 -B certifier/certify.py NAME TARGET N0 [--proc 3] [--rounds 6] [--pas 1] [--N 32]
                                  [--label LABEL] [--out DIR]
     NAME   : BANDES | H4 | DISQP | ILEP
     TARGET : fraction p/q (e.g. 1/192); boxes are refined until the bound is < TARGET
     N0     : initial number of uniform boxes for theta in [0, pi]

Outputs (DIR defaults to ./out): DIR/<label>_config.json (exact colouring),
DIR/<label>_certificat.json (boxes and bounds), and DIR/<label>_FINI when done.
Existing files with the same label are overwritten: use a new --label.

JSON keys of the certificate (in French, kept for byte-identical outputs): "nom" = label,
"cible" = target, "boites" = boxes [x0, x1] (theta = x pi), "borne_integrale" = certified
upper bound of the integral of F over the box, "somme_bornes" = sum of box bounds,
"aire_cellule" = |C|, "p_majorant_dyadique" = dyadic upper bound of p,
"p_majorant_lisible" = readable upper bound k/10^10, "inferieur_a_cible" = bound < target,
"p_flottant" = floating-point estimate (no role in the proof).
"""
import sys, os, time, json, argparse
import multiprocessing as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flint import fmpq, arb
import geometry as L
import core as K
import colourings as CC

PAIRS = None


def qs(x):
    return f"{int(x.p)}/{int(x.q)}"


def pq(s):
    a, b = s.split("/")
    return fmpq(int(a), int(b))


def work(args):
    x0s, x1s = args
    x0, x1 = pq(x0s), pq(x1s)
    st = {}
    b, e = K.box_bound(PAIRS, x0, x1, stats=st)
    return (x0s, x1s, qs(b), e, st["active"], st["M1"], st["M2"], st["u0_attempts"])


def main():
    global PAIRS
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("target")
    ap.add_argument("n0", type=int)
    ap.add_argument("--proc", type=int, default=3)
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--pas", type=int, default=1)
    ap.add_argument("--N", type=int, default=32)
    ap.add_argument("--label", default=None)
    ap.add_argument("--nfloat", type=int, default=512)
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    t_start = time.time()
    target = pq(a.target)
    if a.name == "ILEP":
        cfg = CC.build("ILEP", pas=a.pas)
    elif a.name == "DISQP":
        cfg = CC.build(f"DISQP{a.N}", N=a.N)
    else:
        cfg = CC.build(a.name)
    label = a.label or cfg.name
    out = a.out
    log = lambda *z: print(*z, flush=True)
    log(f"=== {label} : target p < {a.target} = {float(target):.10f} ; start {time.strftime('%Y-%m-%dT%H:%M:%S')}")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"{label}_config.json"), "w") as f:
        json.dump(cfg.json(), f, indent=0)
    log(f"  exact colouring written: {os.path.join(out, label + '_config.json')}")
    K.verify(cfg, log)
    PAIRS = K.enumerate_pairs(cfg, log)
    log(f"  preparation: {time.time() - t_start:.1f} s")
    t = time.time()
    pf = K.p_float(cfg, PAIRS, n=a.nfloat)
    log(f"  floating-point p (midpoint rule, {a.nfloat} angles) = {pf:.10f}  (1/p = {1 / pf:.4f}) [{time.time() - t:.1f} s]")
    # boxes: list of rational (x0, x1) (theta = x pi)
    boxes = [(fmpq(k, a.n0), fmpq(k + 1, a.n0)) for k in range(a.n0)]
    res = {}
    norm = arb.pi() * arb(cfg.cell_area)
    pool = mp.Pool(a.proc)
    for rnd in range(a.rounds + 1):
        t = time.time()
        todo = [(qs(x0), qs(x1)) for (x0, x1) in boxes if (qs(x0), qs(x1)) not in res]
        for r in pool.imap_unordered(work, todo, chunksize=4):
            res[(r[0], r[1])] = r
        tot = fmpq(0)
        est = 0.0
        for (x0, x1) in boxes:
            r = res[(qs(x0), qs(x1))]
            tot += pq(r[2])
            est += r[3]
        pb = arb(tot) / norm
        p_up = L.fmpq_upper(pb)
        ok = p_up < target
        log(f"  round {rnd} : {len(boxes)} boxes ({len(todo)} new, {time.time() - t:.1f} s) ; "
            f"p <= {float(p_up):.10f} ; midpoint estimate {est / float(norm.mid()):.10f} ; "
            f"{'< target' if ok else '>= target'}")
        if ok or rnd == a.rounds:
            break
        # refinement: split the boxes with the largest gap bound - estimate
        excess = float(tot) - float(target) * float(norm.mid())
        gaps = sorted(((float(pq(res[(qs(x0), qs(x1))][2])) - res[(qs(x0), qs(x1))][3], (x0, x1))
                       for (x0, x1) in boxes), key=lambda z: -z[0])
        to_split, cum = set(), 0.0
        for g, bx in gaps:
            if cum >= 3 * excess and len(to_split) >= len(boxes) // 8:
                break
            to_split.add(bx)
            cum += g * 0.75
        nb = []
        for (x0, x1) in boxes:
            if (x0, x1) in to_split:
                xm = (x0 + x1) / 2
                nb += [(x0, xm), (xm, x1)]
            else:
                nb.append((x0, x1))
        boxes = nb
    pool.close()
    pool.join()
    # certificate
    cert = {"nom": label, "cible": a.target, "theta": "theta = x * pi, x in [0, 1] ; boites [x0, x1]",
            "boites": [{"x0": qs(x0), "x1": qs(x1), "borne_integrale": res[(qs(x0), qs(x1))][2]}
                       for (x0, x1) in boxes],
            "somme_bornes": qs(tot), "aire_cellule": qs(cfg.cell_area),
            "p_majorant_dyadique": qs(p_up), "p_majorant_float": float(p_up),
            "p_flottant": pf, "conclusion": bool(ok)}
    # readable rational upper bound: smallest k/10^10 >= p_up
    den = 10 ** 10
    k = (int(p_up.p) * den + int(p_up.q) - 1) // int(p_up.q)
    readable = fmpq(k, den)
    assert readable >= p_up
    cert["p_majorant_lisible"] = qs(readable)
    cert["inferieur_a_cible"] = bool(readable < target)
    with open(os.path.join(out, f"{label}_certificat.json"), "w") as f:
        json.dump(cert, f, indent=0)
    st_act = [res[(qs(x0), qs(x1))] for (x0, x1) in boxes]
    log(f"  final boxes: {len(boxes)} ; mean active pairs {sum(r[4] for r in st_act) / len(st_act):.1f} ;"
        f" (M1) {sum(r[5] for r in st_act)} ; (M2) {sum(r[6] for r in st_act)} ;"
        f" boxes with u0 attempts > 0: {sum(1 for r in st_act if r[7] > 0)}")
    log(f"  RESULT {label} : p <= {qs(readable)} = {float(readable):.10f} ; 1/bound = {1 / float(readable):.4f} ;"
        f" target {a.target} : {'REACHED' if readable < target else 'NOT REACHED'}")
    for c in (192, 193, 198, 203, 205):
        log(f"    bound < 1/{c} : {readable < fmpq(1, c)}")
    log(f"  total time {time.time() - t_start:.1f} s ; end {time.strftime('%Y-%m-%dT%H:%M:%S')}")
    with open(os.path.join(out, f"{label}_FINI"), "w") as f:
        f.write(time.strftime('%Y-%m-%dT%H:%M:%S') + "\n")


if __name__ == "__main__":
    main()
