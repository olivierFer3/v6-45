# v6 ≥ 51: certified bounds for non-5-colourable unit-distance graphs (version 2)

**Statement.** Every finite unit-distance graph in the Euclidean plane that is not 5-colourable
has **at least 244 edges and at least 51 vertices** (in the notation of de Grey–Parts:
e6 ≥ 244 and v6 ≥ 51). The previous best published bounds were e6 ≥ 182 and v6 ≥ 42 (de Grey–Parts).
A simpler colouring in this repository already gives e6 ≥ 193 and v6 ≥ 44.

The statement holds whether or not such graphs exist. They exist if and only if χ(ℝ²) ≥ 6.
The inequality χ(ℝ²) ≥ 6 has been announced in an OpenAI preprint (23 Sept. 2026), which we have not
checked; that preprint does not concern the bounds proved here.

The mathematical write-up is in [`note/v6_51.pdf`](note/v6_51.pdf) (source `note/v6_51.tex`).

**Status: computer-assisted proof, with AI-assisted checks only (which may share blind spots);
NOT reviewed by a human mathematician.**

## History

- **Version 1 (15 November 2026), tag `v1`:** e6 ≥ 204 and v6 ≥ 45 with the colouring ILEP256, and
  e6 ≥ 193, v6 ≥ 44 with DISQP32. Note `note/v6_45.pdf` (kept unchanged in this version). The OpenTimestamps
  proofs in `timestamps/` concern version 1 (commit 8a20bae).
- **Version 2 (this version):** e6 ≥ 244 and v6 ≥ 51 with the colouring **ILEP_S6A**. The certifier
  accepts a free island centre and free angles, and splits hexagons with one reflex vertex
  (`certifier/island.py`). Intermediate steps ILEP_S5B (v6 ≥ 46) and ILEP_S5E (v6 ≥ 50), a variant with a
  93-vertex island (ILEP_S7_93), an independent Monte Carlo check and the verification logs are added. The
  version-1 certificates are unchanged.

## The colourings

| label | role | pieces | island vertices | contributing pairs | certified p5 ≤ | 1/bound | e6 ≥ | v6 ≥ |
|---|---|---|---|---|---|---|---|---|
| DISQP32 | simple example (v1) | 52 | 32-gon | 394 | 51864759/10¹⁰ = 0.0051864759 | 192.81 | 193 | 44 |
| ILEP256 | version 1 | 260 | 256 | 1804 | 24616771/(5·10⁹) = 0.0049233542 | 203.11 | 204 | 45 |
| ILEP_S5B | intermediate | 260 | 256 | 1254 | 24135541/(5·10⁹) = 0.0048271082 | 207.16 | 208 | 46 |
| ILEP_S5E | intermediate | 516 | 512 | 3605 | 42565529/10¹⁰ = 0.0042565529 | 234.93 | 235 | 50 |
| **ILEP_S6A** | **presented** | 523 | 512 | 4754 | **41149783/10¹⁰ = 0.0041149783** | 243.01 | **244** | **51** |
| ILEP_S7_93 | variant (readable island) | 104 | 93 | 793 | 5137931/(1.25·10⁹) = 0.0041103448 | 243.29 | 244 | 51 |

The exact comparisons for the presented colouring are 41149783·239 = 9834798137 < 10¹⁰ (so p5 < 1/239) and
41149783·246 = 10122846618 > 10¹⁰ (so 1/246, the next threshold, is not reached).

**ILEP_S7_93: alert of the numerical check N.** ILEP_S7_93 has a better bound than ILEP_S6A but crosses no new
threshold. It passes the certifier, the exact checks E1–E6 of both verifiers (this version and version 1),
the recomputation of version 1 and the Monte Carlo check. The floating-point check N of `verifier/verify.py`
(not a proof) **fails** on two boxes, 263 and 264: the certified box bound exceeds the floating-point integral
by about 3·10⁻²¹ (relative margins 2.6·10⁻¹⁴ and 3.1·10⁻¹⁴), which is below the absolute floor 10⁻¹⁶ of the
error estimate of N. No box bound is below the integral. A diagnostic with Gauss–Legendre rules of 10, 20 and
30 nodes (`checks/diag_N.py`, log `checks/logs/ILEP_S7_93/diag_N.log`) gives quadrature differences of at most
4·10⁻²² in absolute value, 7 to 60 times smaller than the margin. The alert comes from the floor of the
tolerance of N, not from a missing contribution: in these boxes the Arb enclosure is almost exact. The check N
itself was not changed, and its alert is not lifted by the verifier. This is why ILEP_S6A, for which N passes
(minimum margin 5.7·10⁻¹⁰), is the presented colouring.

## The argument in three steps

1. **An explicit periodic 5-colouring c.** Four colours are placed on deformed hexagons, as in
   Gwyn–Stavrianos. The fifth colour is a rational polygon (the "island") placed near the midpoint of one
   horizontal hexagon edge out of four. In ILEP_S6A the island has 512 vertices, a free centre and free angles,
   and the hexagons of colours 0 and 2 are sheared until they are non-convex (one reflex vertex each, hidden
   inside an island). The certified colourings are the **exact rational colourings defined by the JSON files**
   `certificates/<label>_config.json`. Each file lists the period lattice and closed convex pieces with
   rational vertices and a colour. A point gets the colour of the piece of smallest index containing it
   modulo the lattice; boundaries are a null set.
2. **Certified bound on p5(c)**, the probability that a uniformly random unit segment is
   monochromatic, computed in exact rational arithmetic and Arb ball arithmetic (table above).
3. **From p5 to edges and vertices.**
   - Gwyn–Stavrianos, Lemma 2.10: a non-5-colourable unit-distance graph has at least
     1/p5(c) > 243.01 edges, hence at least 244 edges.
   - `verifier/u_bounds.py` recomputes in exact integer arithmetic u(n) ≤ B(n) for 22 ≤ n ≤ 52, where u(n) is
     the maximum number of edges of a unit-distance graph with n vertices (Alexeev–Mixon–Parshall for
     n = 22, Schade's lemma, Ágoston–Pálvölgyi Prop. 12). It gives u(45..50) ≤ 205, 212, 218, 225, 232, 239,
     the values listed by de Grey–Parts (arXiv:2303.14714, footnote 3). Since u(50) ≤ 239 < 244, a graph with
     at most 50 vertices has too few edges: at least 51 vertices.

## Contents

| path | content |
|---|---|
| `certificates/*_config.json` | the exact colourings (lattice `g1`, `g2`, cell area, convex pieces with colour) |
| `certificates/*_certificat.json` | the certificates: boxes of angles θ = xπ, x ∈ [x0, x1], with a certified rational upper bound of ∫F over each box, and the final bound |
| `data/input/` | floating-point inputs of ILEP256 and DISQP32 (version 1) |
| `data/<label>/` | floating-point inputs of the version-2 colourings (`ILE_hexagones.json`, `ILE_ile.json`, read through `ILE_DATA_DIR`) and the optimiser output `params.json` from which they were written. The "description" fields say "session 5 candidate" for all of them: they record the input format, not the date |
| `certifier/` | the certifier: `geometry.py` (exact convex geometry, Arb helpers), `core.py` (exact checks, pair enumeration, box bounds), `colourings.py`, `island.py` (constructions), `certify.py` (driver), `recompute.py` (recomputation from the JSON files) |
| `verifier/verify.py` | second verifier. It does not import the certifier and does not use python-flint: it uses `fractions.Fraction` for the exact checks and shapely/GEOS for the numerical check |
| `verifier/u_bounds.py` | exact recomputation of u(n) ≤ B(n) for 22 ≤ n ≤ 52, with assertions B(45..50) = 205, 212, 218, 225, 232, 239 |
| `checks/` | auxiliary checks: `check_threshold.py` (exact final arithmetic against 1/DEN), `verify_E1E6.py` (runs a given `verify.py`, e.g. that of tag `v1`, up to E6), `compare_pairs.py` (exact equality of the pair sets of the certifier and of the verifier), `check_decomposition.py` (exact check of the splitting of the hexagons for ILEP_S6A), `diag_N.py` (diagnostic of an alert of N) |
| `checks/logs/` | verification logs of the version-2 certificates (local paths rewritten; see its README) |
| `montecarlo/` | independent Monte Carlo estimate of p5 (`mc_p5.py`) and its results |
| `scripts/reproduce.sh` | full rerun with a new label (DISQP32, ILEP256, ILEP_S6A), followed by a byte comparison with the shipped files |
| `scripts/make_figure.py` | figures of the notes, with a zoom on one island (matplotlib; no role in the proof) |
| `proofs/preuves.md`, `proofs/relecture_preuves.md`, `proofs/relecture_preuves_v4.md` | written proofs of the certification steps (in French), and two AI reviews (version 1) |
| `proofs/decoupage.md` | version 2: proof that the validity of a certificate does not depend on the splitting into convex pieces (E1–E3 suffice for the tiling; E4 serves the completeness of the pairs) |
| `note/` | the notes: `v6_51.tex/pdf` (version 2, figure `fig_s6a.pdf`) and `v6_45.tex/pdf` (version 1, figure `fig_cellule.pdf`) |
| `timestamps/` | OpenTimestamps proofs of version 1 |
| `SHA256SUMS` | SHA-256 of every file of the repository |

JSON keys are in French and were kept as they are, so that the shipped files are byte-identical
to the regenerated ones. The keys are: `nom` = name/label, `pieces` = pieces, `couleur` = colour,
`sommets` = vertices, `aire_cellule` = cell area, `parametres` = parameters, `boites` = boxes,
`borne_integrale` = bound of the integral, `somme_bornes` = sum of the bounds,
`p_majorant_lisible` = readable upper bound, `cible` = target, `p_flottant` = floating-point
estimate (no role in the proof). In every ILEP configuration file `nom` is `ILEP1` (step `pas = 1`).

## What changed in the certifier (version 2)

Only `certifier/island.py` changes the construction; `core.py`, `geometry.py`, `certify.py` and
`colourings.py` are byte-identical to version 1. `recompute.py` and `verifier/verify.py` only print more
comparisons (1/205, 1/232, 1/239, 1/246); `verifier/u_bounds.py` extends the range of n and adds assertions.
In `island.py`:
- `ILE_DATA_DIR`: optional environment variable, the directory of `ILE_hexagones.json` and `ILE_ile.json`
  (default `data/input/`);
- `m_libre`, `psi_k` (optional keys of `ILE_ile.json`): free island centre and free angles; the number of
  island vertices is `len(rho_k)`;
- a hexagon with exactly one reflex vertex is split into a fan of triangles merged into convex parts.
  This splitting is not proved correct in general, and it does not need to be: the validity depends only on
  the final list of pieces, checked exactly by E1–E3 (`proofs/decoupage.md`). For ILEP256 the construction is
  unchanged (the regenerated files are byte-identical, see `scripts/reproduce.sh`).

These modifications and the splitting were reviewed by AI agents that had not written them (no decisive
remark); no human has reviewed them.

## What is checked, and by what

**The certifier** (`certifier/certify.py`, with python-flint 0.9.0) checks the following.
- **The tiling, exactly.** Every piece is strictly convex. This uses the true test: all turns are
  positive *and* the piece equals its convex hull, so star polygons are rejected. The piece areas
  sum to |det(g1, g2)|, and translates of pieces have disjoint interiors.
- **The reduction.** p5 = (1/(π|C|)) ∫₀^π Σ_(P,Q) area(P ∩ (Q − u(θ))) dθ. The sum runs over the
  same-colour pairs (P, Q) whose difference body meets the unit circle (table above). An angular filter is
  applied per box, and it is rigorous.
- **The bound on each box.** It is either
  - (M1) the Brunn–Minkowski concavity bound A ≤ (√A₀ + ∇A·d/(2√A₀))², with an exact gradient and
    an exact differentiability check, or
  - (M2) the Minkowski bound A ≤ area(P ∩ (Q ⊕ (−K))) for a rational rectangle K containing the
    arc.
- **The integration.** The integrals of cos/sin moments are computed in Arb balls. The sum is
  exact, and π is enclosed by Arb.
- **The role of floating point.** Floats are used only to choose the anchor point u₀, the bound
  and the boxes. They never enter the validity of the result.

**`certifier/recompute.py`** recomputes every box bound from the JSON files alone. It uses the
same library, so it is a recomputation, not an independent check.

**`verifier/verify.py`** does not import the certifier. It checks exactly the geometry, the pairs and
the rational additions; it does **not** recertify in interval arithmetic the box bounds, which rest on the
Arb certifier alone.
- **Exact checks** (`Fraction`):
  - E1: true strict convexity;
  - E2: areas;
  - E3: disjoint interiors, using separating edge lines;
  - E4: |a| ≥ 2 or |b| ≥ 2 puts every pair of pieces at distance > 1, so the list of translations
    of the pairs is complete;
  - E5: exact list of the contributing pairs;
  - E6: final arithmetic of the certificate, with π > 314159265358979/10¹⁴.
- **Numerical check N** (floating point, not a proof). For every box, the integral of F is
  recomputed with GEOS areas, explicit breakpoints and Gauss–Legendre quadrature. Every certified
  box bound must exceed it by more than an error estimate.
  - ILEP_S6A: minimum margin 5.7·10⁻¹⁰, recomputed value p ≈ 0.0041078081.
  - ILEP256: minimum margin 2.3·10⁻⁹, recomputed value p ≈ 0.0049196874. DISQP32: minimum margin 5.0·10⁻⁹.
  - ILEP_S7_93: alert on two boxes, explained above.
  - The agreement of the Gauss–Legendre computations with 6 and 10 nodes is a numerical consistency check,
    not a rigorous bound on quadrature or GEOS errors. The rigorous upper bounds rely exclusively on exact
    rational arithmetic and Arb interval enclosures.

**Additional checks of the version-2 certificates** (logs in `checks/logs/`):
- the **unmodified verifier and recomputation of version 1** (tag `v1`) were run on ILEP_S5B, ILEP_S5E,
  ILEP_S6A and ILEP_S7_93: E1–E6 pass and every box bound is confirmed;
- for ILEP_S5B and ILEP_S5E, the set of pairs of the certifier equals exactly the set E5 of the verifier;
- for ILEP_S6A, the splitting of the non-convex hexagons was checked exactly by another method
  (`checks/check_decomposition.py`), and `island.py` regenerates the shipped colouring byte for byte;
- the **Monte Carlo** estimate (`montecarlo/`, 4·10⁷ segments, code written without importing the project)
  gives 0.0041071 ± 1.0·10⁻⁵ for ILEP_S6A, below the certified bound. With this σ it would detect only an
  error of about 3·10⁻⁵ or more.

**Assumptions not checked by the code:**
- the inclusion principle of Arb (standard, documented by FLINT);
- Brunn–Minkowski;
- Gwyn–Stavrianos Lemma 2.10. The note gives a self-contained proof for periodic Borel colourings.
- Ágoston–Pálvölgyi Prop. 12;
- the bound u(22) ≤ 61 of Alexeev–Mixon–Parshall.

## How to rerun

Requirements: Python 3.12 and `pip install -r requirements.txt` (python-flint 0.9.0,
numpy 2.5.4, shapely 2.1.2). Run all commands from the repository root. Each command uses
`--proc` worker processes (3 by default); it uses at most 4 processes in total.

`certify.py` **overwrites** `out/<label>_*`, so always give a new `--label`. The shipped files in
`certificates/` are never written by these commands.

```bash
# 1. certification from scratch (writes out/<label>_config.json, out/<label>_certificat.json)
python3 -B certifier/certify.py DISQP 1/192 256 --N 32 --proc 3 --rounds 4 --label DISQP32_new --out out
python3 -B certifier/certify.py ILEP 1/203 1024 --pas 1 --proc 3 --rounds 6 --label ILEP256_new --out out
ILE_DATA_DIR=data/ILEP_S6A python3 -B certifier/certify.py ILEP 1/239 1024 --pas 1 --proc 3 --rounds 6 --label ILEP_S6A_new --out out
# (similarly: data/ILEP_S5B with 1/205, data/ILEP_S5E with 1/232, data/ILEP_S7_93 with 1/239)

# 2. the regenerated files are identical to the shipped ones (apart from the "nom" label field)
cmp certificates/ILEP_S6A_config.json out/ILEP_S6A_new_config.json
diff <(sed 's/"nom": "ILEP_S6A_new"/"nom": "ILEP_S6A"/' out/ILEP_S6A_new_certificat.json) certificates/ILEP_S6A_certificat.json

# 3. recomputation and second verification of the shipped certificates
python3 -B certifier/recompute.py ILEP_S6A --dir certificates
python3 -B verifier/verify.py ILEP_S6A --dir certificates
python3 -B checks/check_threshold.py ILEP_S6A certificates 239
python3 -B verifier/u_bounds.py

# 4. the verifier of version 1 on a version-2 certificate (E1-E6)
git show v1:verifier/verify.py > /tmp/verify_v1.py
python3 -B checks/verify_E1E6.py ILEP_S6A certificates /tmp/verify_v1.py

# 5. Monte Carlo (about 3-4 min, up to 0.6 GB of memory)
python3 -B montecarlo/mc_p5.py certificates/ILEP_S6A_config.json 4e7 20261119 1000000

# or steps 1-3 for DISQP32, ILEP256 and ILEP_S6A at once, with a new label suffix:
PYTHON=python3 scripts/reproduce.sh run1
```

On a memory-limited Linux machine we ran every command inside
`systemd-run --user --scope -p MemoryMax=1200M -p MemorySwapMax=0 -q …`, e.g.
`WRAP="systemd-run --user --scope -p MemoryMax=1200M -p MemorySwapMax=0 -q" PYTHON=venv/bin/python scripts/reproduce.sh run3`.

**Measured times (version 2).** On a laptop (Linux x86_64, Python 3.12.3, 3 worker processes), in a clean
clone, `scripts/reproduce.sh` ran in one go in 38 min 28 s (maximum resident set size of a single process 128 MB). Certifying ILEP_S6A takes about 10 min,
recomputing it about 10 min and verifying it about 3–4 min, each with a maximum resident set size below
130 MB. The version-1 measurements (DISQP32: seconds; ILEP256: 3–5 min per command) are in the README of
tag `v1`.

**Installing without `ensurepip`.** On systems where `python3 -m venv` fails because `ensurepip` is
missing, use:

```bash
python3 -m venv --without-pip venv
python3 -m pip --python venv/bin/python install -r requirements.txt
PYTHON=venv/bin/python scripts/reproduce.sh run2
```

## Limitations

- **No human review.** The certificates, the proofs, the code and its modifications have been checked only by
  AI-assisted checks (Claude), which may share blind spots. The Monte Carlo check and the reviews are
  independent of the certifier's code, not of the AI that wrote them.
- **The novelty search is not exhaustive.** It covered arXiv, the tables of contents of
  Geombinatorics 2022–2026, the Polymath16 threads and general web search. It did not cover the
  full text of recent Geombinatorics issues or Google Scholar.
- **χ(ℝ²) ≥ 6 is not established independently.** The bounds hold in any case.
- **Further improvements need new ideas.** v6 ≥ 52 would require p5 < 1/246 ≈ 0.0040650, about 1.3 % below
  ILEP_S6A; the optimisation within the present family of colourings has converged near p5 ≈ 0.0041075.
- **v5 ≥ 29.** It follows from e5 ≥ 99 (de Grey–Parts) and u(28) ≤ 96 (Alexeev–Mixon–Parshall,
  Thm. 1(b)); see `verifier/u_bounds.py`. As a secondary computation, not audited, not included
  here and not part of the results, the certifier also gives p4 ≤ 0.0101531397 < 1/98 for the
  4-colour hexagon tiling, consistent with e5 ≥ 99.

## Credits

- **H. Gwyn, J. Stavrianos**, *A finite graph approach to the probabilistic Hadwiger–Nelson
  problem*, arXiv:2008.07987v1 (2020); Geombinatorics 32(1) (2022). They introduced p_k, the
  edge bound of Lemma 2.10 and the hexagonal 4-colouring.
- **A. D. N. J. de Grey, J. Parts**, *On lower bounds of the order of k-chromatic unit distance
  graphs*, arXiv:2303.14714v1; Geombinatorics 32(2) (2022), 72. They replaced the disks of Gwyn–Stavrianos
  by the rounded dodecagons of Croft's tiling, rounded the bounds up and used the AP bound, obtaining
  e6 ≥ 182 and v6 ≥ 42. Their footnote 3 lists the upper bounds on u(n) used here.
- **Polymath16 thread** (seventeenth thread, comments of 28 and 30 June 2022 by the user ag24ag24 of the Polymath16 project): the
  hope for "a more impressive value than 42 using good 5-tilings", and the suggestion to take into
  account "regions that cannot contain a vertex of a mono edge".
- **P. Ágoston, D. Pálvölgyi**, *An improved constant factor for the unit distance problem*,
  arXiv:2006.06285v3; Studia Sci. Math. Hungar. 59 (2022) 40–57. This is the source of Prop. 12.
- **B. Alexeev, D. G. Mixon, H. Parshall**, *The Erdős unit distance problem for small point sets*,
  arXiv:2412.11914v2. This is the source of u(22) ≤ 61, Schade's lemma and u(28) ≤ 96.
- Software: FLINT/Arb via python-flint, shapely/GEOS, numpy.

## Use of AI

The construction, the optimisation, the certification code and its modifications, the proofs and the notes
were produced with Claude Code (Anthropic). Further AI agents (Claude) wrote the Monte Carlo check, reviewed
the modifications of the certifier and the splitting of the hexagons, and ran the verifiers; for version 1,
ChatGPT (OpenAI) also performed cross-checks (literature search, a reading of the arguments and execution of
the verifiers). All these checks are AI-assisted and may share blind spots; no human mathematician has
reviewed this work.

## Licence

Apache License 2.0, see `LICENSE`. Author: olivierFer3.
