#!/usr/bin/env python3
"""Controle Monte-Carlo independant de p5 pour une 5-coloration periodique du plan.

Ecrit de zero : n'importe aucun script du projet. Lit seulement le JSON de configuration
(g1, g2, pieces = polygones convexes {"sommets": [["a/b","c/d"],...], "couleur": 0..4}).

p5 = P(les deux extremites d'un segment unite aleatoire ont la meme couleur),
origine uniforme dans la cellule {s g1 + t g2 : s,t in [0,1)}, angle uniforme dans [0, 2pi).

Usage : mc_p5.py config.json N_segments [graine] [taille_lot]
"""
import json
import sys
import time
from fractions import Fraction

import numpy as np

TOL = 1e-12   # tolerance de bord (distance euclidienne)
GRID = 256    # grille de localisation dans les coordonnees (s, t)
SUB = 250_000  # sous-lot de points pour les tests (memoire)


def charger(chemin):
    d = json.load(open(chemin))
    g1 = np.array([float(Fraction(c)) for c in d["g1"]])
    g2 = np.array([float(Fraction(c)) for c in d["g2"]])
    pieces = []
    for p in d["pieces"]:
        V = np.array([[float(Fraction(c)) for c in v] for v in p["sommets"]])
        pieces.append((V, int(p["couleur"])))
    return d, g1, g2, pieces


def demi_plans(V):
    """Retourne (A, c) normalises avec A x <= c a l'interieur ; verifie la convexite."""
    x, y = V[:, 0], V[:, 1]
    aire = 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)
    if aire < 0:
        V = V[::-1]
    E = np.roll(V, -1, axis=0) - V
    # convexite : produits vectoriels consecutifs >= 0
    cr = E[:, 0] * np.roll(E, -1, axis=0)[:, 1] - E[:, 1] * np.roll(E, -1, axis=0)[:, 0]
    convexe = bool(np.all(cr >= -1e-14))
    L = np.hypot(E[:, 0], E[:, 1])
    ok = L > 0
    E, Vk, L = E[ok], V[ok], L[ok]
    n = np.stack([E[:, 1], -E[:, 0]], axis=1) / L[:, None]  # normale sortante (CCW)
    c = np.sum(n * Vk, axis=1)
    return n, c, abs(aire), convexe


def preparer(g1, g2, pieces):
    M = np.array([g1, g2]).T            # x = M @ (s, t)
    Minv = np.linalg.inv(M)
    trans = []  # (n, c, couleur, indice_piece, -)
    polys = []
    nonconv = 0
    aires = np.zeros(5)
    for k, (V, col) in enumerate(pieces):
        n, c, a, conv = demi_plans(V)
        nonconv += (not conv)
        aires[col] += a
        st = V @ Minv.T
        smin, tmin = st.min(axis=0)
        smax, tmax = st.max(axis=0)
        for i in range(int(np.floor(-smax)) - 1, int(np.ceil(1 - smin)) + 1):
            for j in range(int(np.floor(-tmax)) - 1, int(np.ceil(1 - tmin)) + 1):
                if smax + i < 0 or smin + i > 1 or tmax + j < 0 or tmin + j > 1:
                    continue
                sh = i * g1 + j * g2
                trans.append((n, c + n @ sh, col, k, None)); polys.append((V, sh))
    P = len(trans)
    vmax = max(len(t[1]) for t in trans)
    NA = np.zeros((P, vmax, 2))
    NC = np.ones((P, vmax))   # demi-plan trivial 0 <= 1
    COL = np.zeros(P, dtype=np.int64)
    for q, (n, c, col, k, _) in enumerate(trans):
        NA[q, :len(c)] = n
        NC[q, :len(c)] = c
        COL[q] = col
    # grille de candidats : intersection exacte (shapely) polygone (en coordonnees s,t) / case elargie
    from shapely.geometry import Polygon, box
    from shapely.strtree import STRtree
    eps = 1e-9
    cases = [box(a / GRID - eps, b / GRID - eps, (a + 1) / GRID + eps, (b + 1) / GRID + eps)
             for a in range(GRID) for b in range(GRID)]
    arbre = STRtree(cases)
    cand = [[] for _ in range(GRID * GRID)]
    for q, (V, sh) in enumerate(polys):
        st = (V + sh) @ Minv.T
        for g in arbre.query(Polygon(st), predicate="intersects"):
            cand[int(g)].append(q)
    K = max(len(c) for c in cand)
    CAND = -np.ones((GRID * GRID, K), dtype=np.int64)
    for g, c in enumerate(cand):
        CAND[g, :len(c)] = c
    return M, Minv, NA, NC, COL, CAND, nonconv, aires, P


def localiser(X, Minv, g1, g2, NA, NC, COL, CAND):
    """X : (N,2) points. Retourne couleur (-1 si non couvert), nb de pieces couvrant strictement,
    nb de pieces a <= TOL."""
    st = X @ Minv.T
    fl = np.floor(st)
    st -= fl
    st = np.clip(st, 0.0, np.nextafter(1.0, 0.0))
    Xr = X - fl[:, :1] * g1 - fl[:, 1:] * g2       # point ramene dans la cellule
    cell = (st[:, 0] * GRID).astype(np.int64) * GRID + (st[:, 1] * GRID).astype(np.int64)
    N = len(X)
    best = np.full(N, np.inf)
    col = np.full(N, -1, dtype=np.int64)
    nstrict = np.zeros(N, dtype=np.int64)
    nfermé = np.zeros(N, dtype=np.int64)
    for k in range(CAND.shape[1]):
        q = CAND[cell, k]
        m = q >= 0
        if not m.any():
            break
        idx = np.nonzero(m)[0]
        qq = q[idx]
        A = NA[qq]                     # (n, v, 2)
        d = np.max(A[:, :, 0] * Xr[idx, 0, None] + A[:, :, 1] * Xr[idx, 1, None] - NC[qq], axis=1)
        nstrict[idx] += d < -TOL
        nfermé[idx] += d <= TOL
        mieux = d < best[idx]
        best[idx[mieux]] = d[mieux]
        col[idx[mieux]] = COL[qq[mieux]]
    col[best > TOL] = -1
    return col, nstrict, nfermé


def main():
    chemin = sys.argv[1]
    N = int(float(sys.argv[2]))
    graine = int(sys.argv[3]) if len(sys.argv) > 3 else 12345
    lot = int(float(sys.argv[4])) if len(sys.argv) > 4 else 1_000_000
    t0 = time.time()
    d, g1, g2, pieces = charger(chemin)
    M, Minv, NA, NC, COL, CAND, nonconv, aires, P = preparer(g1, g2, pieces)
    aire_cell = abs(np.linalg.det(M))
    print(f"fichier {chemin}")
    print(f"pieces {len(pieces)} ; translates retenus {P} ; non convexes {nonconv} ; candidats max/case {CAND.shape[1]}")
    print(f"aire cellule {aire_cell:.12f} ; somme aires pieces {aires.sum():.12f} ; ecart {aires.sum()-aire_cell:.3e}")
    print("fraction d'aire par couleur", " ".join(f"{a/aire_cell:.6f}" for a in aires))
    print(f"graine {graine} ; N {N} ; lot {lot}", flush=True)
    rng = np.random.default_rng(graine)
    tot = meme = 0
    n0 = nmult = nbord = 0
    exclus = 0
    fait = 0
    while fait < N:
        b = min(lot, N - fait)
        s = rng.random(b); t = rng.random(b); th = rng.random(b) * (2 * np.pi)
        P0 = s[:, None] * g1 + t[:, None] * g2
        P1 = P0 + np.stack([np.cos(th), np.sin(th)], axis=1)
        cols = []
        for X in (P0, P1):
            c_all = np.empty(b, dtype=np.int64)
            for u in range(0, b, SUB):
                c, ns, nf = localiser(X[u:u + SUB], Minv, g1, g2, NA, NC, COL, CAND)
                c_all[u:u + SUB] = c
                n0 += int(np.sum(nf == 0))
                nmult += int(np.sum(ns >= 2))
                nbord += int(np.sum((nf >= 2) & (ns <= 1)))
            cols.append(c_all)
        ok = (cols[0] >= 0) & (cols[1] >= 0)
        exclus += int(np.sum(~ok))
        meme += int(np.sum(ok & (cols[0] == cols[1])))
        tot += int(np.sum(ok))
        fait += b
        if (fait // lot) % 5 == 0 or fait == N:
            p = meme / tot
            print(f"  {fait:>11d} segments  p5={p:.8f}  sd={np.sqrt(p*(1-p)/tot):.2e}  "
                  f"t={time.time()-t0:.0f}s", flush=True)
    p = meme / tot
    sd = np.sqrt(p * (1 - p) / tot)
    print("RESULTAT")
    print(f"segments_valides {tot} ; segments_exclus {exclus}")
    print(f"points_non_couverts {n0} ; points_couverts_strictement_par_>=2_pieces {nmult} ; "
          f"points_sur_bord_commun (info) {nbord}")
    print(f"p5 {p:.10f} ; ecart_type {sd:.3e} ; meme_couleur {meme}")
    print(f"duree {time.time()-t0:.1f} s")


if __name__ == "__main__":
    main()
