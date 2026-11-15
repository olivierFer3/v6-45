# v6 ≥ 45: certified bounds for non-5-colourable unit-distance graphs

**Statement.** Every finite unit-distance graph in the Euclidean plane that is not 5-colourable
has **at least 204 edges and at least 45 vertices** (in the notation of de Grey–Parts:
e6 ≥ 204 and v6 ≥ 45). The previous best bounds were e6 ≥ 182 and v6 ≥ 42 (de Grey–Parts).
A simpler colouring in this repository already gives e6 ≥ 193 and v6 ≥ 44.

The statement holds whether or not such graphs exist. They exist if and only if χ(ℝ²) ≥ 6.
The inequality χ(ℝ²) ≥ 6 has been announced in an OpenAI preprint (23 Sept. 2026), which we have not
checked; that preprint does not concern the bounds proved here.

The mathematical write-up is in [`note/v6_45.pdf`](note/v6_45.pdf) (source `note/v6_45.tex`).

**Status: computer-assisted proof, with AI-assisted cross-checks only (which may share blind spots);
NOT yet reviewed by a human mathematician.**

## The argument in three steps

1. **An explicit periodic 5-colouring c.** Four colours are placed on (slightly deformed)
   hexagons, as in Gwyn–Stavrianos. The fifth colour is a 256-vertex rational polygon (the
   "island") placed on the midpoint of one horizontal hexagon edge out of four. The certified
   colourings are the **exact rational colourings defined by the JSON files**
   `certificates/ILEP256_config.json` and `certificates/DISQP32_config.json`. Each file lists the
   period lattice and closed convex pieces with rational vertices and a colour. A point gets the
   colour of the piece of smallest index containing it modulo the lattice; boundaries are a null set.
2. **Certified bound on p5(c)**, the probability that a uniformly random unit segment is
   monochromatic. It is computed in exact rational arithmetic and Arb ball arithmetic:
   - **ILEP256:** p5 ≤ 24616771/(5·10⁹) = 0.0049233542 < 1/203. The check is exact:
     24616771·203 = 4997204513 < 5·10⁹.
   - **DISQP32:** p5 ≤ 51864759/10¹⁰ = 0.0051864759 < 1/192. The check is exact:
     51864759·192 = 9958033728 < 10¹⁰.
3. **From p5 to edges and vertices.**
   - Gwyn–Stavrianos, Lemma 2.10: a non-5-colourable unit-distance graph has at least
     1/p5(c) > 203.1 edges, hence at least 204 edges.
   - Ágoston–Pálvölgyi, Prop. 12, gives u(44) ≤ 198 < 204, where u(n) is the maximum number of
     edges of a unit-distance graph with n vertices. Hence at least 45 vertices.
   - For DISQP32, u(43) ≤ 192 < 193 gives at least 44 vertices.

## Contents

| path | content |
|---|---|
| `certificates/*_config.json` | the exact colourings (lattice `g1`, `g2`, cell area, convex pieces with colour) |
| `certificates/*_certificat.json` | the certificates: boxes of angles θ = xπ, x ∈ [x0, x1], with a certified rational upper bound of ∫F over each box, and the final bound |
| `data/input/` | floating-point inputs of the construction (hexagon displacements, island radii, DISQ parameters) |
| `certifier/` | the certifier: `geometry.py` (exact convex geometry, Arb helpers), `core.py` (exact checks, pair enumeration, box bounds), `colourings.py`, `island.py` (constructions), `certify.py` (driver), `recompute.py` (recomputation from the JSON files) |
| `verifier/verify.py` | second verifier. It does not import the certifier and does not use python-flint: it uses `fractions.Fraction` for the exact checks and shapely/GEOS for the numerical check |
| `verifier/u_bounds.py` | exact recomputation of u(n) ≤ B(n) for 22 ≤ n ≤ 46 (AMP, Schade, Ágoston–Pálvölgyi Prop. 12) |
| `scripts/reproduce.sh` | full rerun with a new label, followed by a byte comparison with the shipped files |
| `scripts/make_figure.py` | figure of the note, with a zoom on one island (matplotlib; no role in the proof) |
| `proofs/preuves.md`, `proofs/relecture_preuves.md` | written proofs of the certification steps, and their AI review (in French), updated to the distributed code |
| `note/` | the note (PDF, LaTeX source, figure) |
| `SHA256SUMS` | SHA-256 of every file of the repository |

JSON keys are in French and were kept as they are, so that the shipped files are byte-identical
to the regenerated ones. The keys are: `nom` = name/label, `pieces` = pieces, `couleur` = colour,
`sommets` = vertices, `aire_cellule` = cell area, `parametres` = parameters, `boites` = boxes,
`borne_integrale` = bound of the integral, `somme_bornes` = sum of the bounds,
`p_majorant_lisible` = readable upper bound, `cible` = target, `p_flottant` = floating-point
estimate (no role in the proof).

## What is checked, and by what

**The certifier** (`certifier/certify.py`, with python-flint 0.9.0) checks the following.
- **The tiling, exactly.** Every piece is strictly convex. This uses the true test: all turns are
  positive *and* the piece equals its convex hull, so star polygons are rejected. The piece areas
  sum to |det(g1, g2)|, and translates of pieces have disjoint interiors.
- **The reduction.** p5 = (1/(π|C|)) ∫₀^π Σ_(P,Q) area(P ∩ (Q − u(θ))) dθ. The sum runs over the
  same-colour pairs (P, Q) whose difference body meets the unit circle: 394 pairs for DISQP32 and
  1804 for ILEP256. An angular filter is applied per box, and it is rigorous.
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
the rational additions; it does **not** recertify in interval arithmetic each of the 1280 box bounds
(256 + 1024), which rest on the Arb certifier alone.
- **Exact checks** (`Fraction`):
  - E1: true strict convexity;
  - E2: areas;
  - E3: disjoint interiors, using separating edge lines;
  - E4: |a| ≥ 2 or |b| ≥ 2 puts every pair of pieces at distance > 1, so the list of translations
    is complete;
  - E5: exact list of the contributing pairs (394 and 1804);
  - E6: final arithmetic of the certificate, with π > 314159265358979/10¹⁴.
- **Numerical check N** (floating point, not a proof). For every box, the integral of F is
  recomputed with GEOS areas, explicit breakpoints and Gauss–Legendre quadrature. Every certified
  box bound must exceed it.
  - ILEP256: minimum margin 2.3·10⁻⁹. The Gauss–Legendre computations with 6 and 10 nodes agree to
    about 10⁻¹⁸; this agreement is a numerical consistency check, not a rigorous bound on quadrature
    or GEOS errors. The rigorous upper bounds rely exclusively on exact rational arithmetic and Arb
    interval enclosures. Recomputed value: p ≈ 0.0049196874.
  - DISQP32: minimum margin 5.0·10⁻⁹, recomputed value p ≈ 0.0051253154.

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

# 2. the regenerated files are identical to the shipped ones (apart from the "nom" label field)
cmp certificates/ILEP256_config.json out/ILEP256_new_config.json
diff <(sed 's/"nom": "ILEP256_new"/"nom": "ILEP256"/' out/ILEP256_new_certificat.json) certificates/ILEP256_certificat.json

# 3. recomputation and second verification of the shipped certificates
python3 -B certifier/recompute.py ILEP256 --dir certificates
python3 -B verifier/verify.py ILEP256 --dir certificates
python3 -B verifier/verify.py DISQP32 --dir certificates
python3 -B verifier/u_bounds.py

# or everything at once, with a new label suffix:
PYTHON=python3 scripts/reproduce.sh run1
```

On a memory-limited Linux machine we ran every command inside
`systemd-run --user --scope -p MemoryMax=1200M -p MemorySwapMax=0 -q …`.

**Measured times and memory.** The measurements were taken on a laptop (Linux x86_64, Python
3.12.3, 3 worker processes) in two clean-clone tests: run 1 timed each command with `/usr/bin/time -v`
and the cgroup's `memory.peak`, and run 2 ran `scripts/reproduce.sh` in one go and took the times
printed by the scripts. Wall times depend on the machine load; expect the range below. "Max RSS" is
that of the largest single process; "peak (all)" covers all processes.

| command | wall time (run 1 / run 2) | max RSS | peak (all) |
|---|---|---|---|
| `certify.py DISQP … 256` | 8 s / 11 s | 34 MB | — |
| `certify.py ILEP … 1024` | 3 min 11 s / 4 min 34 s | 44 MB | 85 MB |
| `recompute.py DISQP32` | 15 s / 17 s | 34 MB | — |
| `recompute.py ILEP256` | ≈ 3 min of CPU / 4 min 09 s | 43 MB | 84 MB |
| `verify.py DISQP32` | 3 s / 6 s | 40 MB | 96 MB |
| `verify.py ILEP256` | 1 min 01 s / 1 min 43 s | 72 MB | 155 MB |
| `u_bounds.py` | < 1 s | 10 MB | — |
| `scripts/reproduce.sh` (everything) | — / 11 min | | |

In run 1 the machine was suspended during `recompute.py ILEP256`, so only its CPU time is
meaningful.

**Installing without `ensurepip`.** On systems where `python3 -m venv` fails because `ensurepip` is
missing, run 2 used:

```bash
python3 -m venv --without-pip venv
python3 -m pip --python venv/bin/python install -r requirements.txt
PYTHON=venv/bin/python scripts/reproduce.sh run2
```

## Limitations

- **No human review yet.** The certificate, the proofs and the code have been checked only by
  AI-assisted cross-checks, which may share blind spots.
- **The novelty search is not exhaustive.** It covered arXiv, the tables of contents of
  Geombinatorics 2022–2026, the Polymath16 threads and general web search. It did not cover the
  full text of recent Geombinatorics issues or Google Scholar.
- **χ(ℝ²) ≥ 6 is not established independently.** The bounds hold in any case.
- **Further improvements need new ideas.** v6 ≥ 46 would require p5 < 1/205, and the colouring
  here has p5 ≈ 0.00491969. A finer certificate for ILEP256 (2048 boxes, p5 ≤ 0.0049204506) was
  computed but is not included and not claimed.
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
  e6 ≥ 182 and v6 ≥ 42.
- **Polymath16 thread** (seventeenth thread, comments of 28 and 30 June 2022, user ag24ag24): the
  hope for "a more impressive value than 42 using good 5-tilings", and the suggestion to take into
  account "regions that cannot contain a vertex of a mono edge".
- **P. Ágoston, D. Pálvölgyi**, *An improved constant factor for the unit distance problem*,
  arXiv:2006.06285v3; Studia Sci. Math. Hungar. 59 (2022) 40–57. This is the source of Prop. 12.
- **B. Alexeev, D. G. Mixon, H. Parshall**, *The Erdős unit distance problem for small point sets*,
  arXiv:2412.11914v2. This is the source of u(22) ≤ 61, Schade's lemma and u(28) ≤ 96.
- Software: FLINT/Arb via python-flint, shapely/GEOS, numpy.

## Use of AI

The construction, the certification code, the proofs and the note were produced with Claude Code
(Anthropic). Additional AI agents and ChatGPT (OpenAI) performed cross-checks: literature search, a
reading of the arguments, execution of the verifiers and an independent Monte Carlo estimate of p5.
These checks are AI-assisted and may share blind spots; no human mathematician has reviewed this
work yet.

## Licence

Apache License 2.0, see `LICENSE`. Author: [Author].
