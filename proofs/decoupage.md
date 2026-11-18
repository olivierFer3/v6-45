# The validity of a certificate does not depend on the splitting into convex pieces

*Version 2. Adapted from §4 of an AI review of the splitting of non-convex hexagons in `certifier/island.py`
(the reviewer was an agent that had written neither the code nor the certificates). No human review.*

## Setting

`certifier/island.py` produces a list of closed convex polygons P₁, …, P_N with rational vertices and a colour
each, written to `<label>_config.json`. Since version 2 it can split a hexagon with **one** reflex vertex r
into the fan of triangles (r, V_{r+k}, V_{r+k+1}), k = 1..4, merged greedily into strictly convex parts
(this is used by ILEP_S6A and ILEP_S7_93 for the hexagons of colours 0 and 2). The correctness of this fan
splitting is **not proved in general**: a polygon with one reflex vertex need not be star-shaped from that
vertex, and simplicity of the hexagon is not tested. The point of this note is that no such proof is needed.

The certifier (`core.verify`) and the second verifier (`verifier/verify.py`) check exactly, on the list read
from the JSON file and on nothing else:

- **E1** every P_i is strictly convex and counter-clockwise (all turns > 0 and P_i equals its convex hull);
- **E2** Σ area(P_i) = |C| = |det(g₁, g₂)|;
- **E3** for (i, g) ≠ (j, h) in {1..N} × G, the interiors of P_i + g and P_j + h are disjoint. By translation
  it suffices to test P_i and P_j + t with t = h − g; if x ∈ P_i and x − t ∈ P_j then
  |t| ≤ |x| + |x − t| ≤ 2 R_max (R_max = largest norm of a vertex), so the finite list tested is complete.

## Claim

E1, E2 and E3 imply that the G-translates of the pieces tile the plane: they cover ℝ² and have pairwise
disjoint interiors. Hence the colouring "colour of the piece containing the point" is well defined outside a
null set, which is what the definition of the areas A_PQ(u) and of p5 needs (the validity of the
*bound* on p5 needs more, see "Scope of E1–E3" below).

## Proof

Let G = ℤg₁ + ℤg₂ with |C| > 0, let π : ℝ² → T = ℝ²/G be the quotient map and μ the Haar measure of T, of
total mass |C|.

1. By E1 each P_i is a compact convex set, and the shoelace formula gives its true area, which is > 0. Its
   boundary is a null set.
2. By E3, π is injective on the disjoint union of the interiors int P_i. Hence
   μ(π(∪ P_i)) = Σ area(P_i) = |C| by E2 (boundaries are null).
3. So π(∪ P_i) has full measure in T, and U = ∪_{i, g} (P_i + g) = π⁻¹(π(∪ P_i)) has a null complement.
4. U is closed, being a locally finite union of compact sets (a bounded set meets only finitely many
   translates). Thus ℝ² ∖ U is an open null set, hence empty.
5. The translates therefore cover the plane, and by E3 their interiors are pairwise disjoint: they tile ℝ².

None of these steps involves the hexagons, the island or the way the list was produced. The splitting only
*proposes* the list; the list is checked exactly afterwards. A wrong splitting can therefore only make E1, E2
or E3 fail, or produce another colouring, which is then valid and certified for what it is. It can never
produce a false certificate.

## Scope of E1–E3 (added after the external audit of version 2)

E1–E3 guarantee only that the final pieces **represent a tiling**, hence a well-defined colouring; this is
all that the splitting can affect. They do **not** by themselves validate the bound on p5. The validity of
the bound also requires:

- the **completeness of the contributing pairs** (E4–E5 in `verifier/verify.py`; the certifier enumerates
  the pairs independently, and for ILEP_S5B and ILEP_S5E the two sets were compared and found equal);
- the **correctness of the Arb box bounds** (inclusion principle of Arb, Brunn–Minkowski for (M1), the
  Minkowski inclusion for (M2)).

E6 checks the **sum of the recorded box bounds** and the final arithmetic (partition of [0, 1], sum equal to
`somme_bornes`, division by π_low·|C|, comparison with the readable bound). It does **not** check the
construction of each individual box bound; that is redone by `certifier/recompute.py` (same library,
python-flint, so a recomputation rather than an independent proof; log
`checks/logs/ILEP_S6A/recompute_v2.log`).

Which program tests what, for ILEP_S6A (counts read from the logs):

- the certifier (`certifier/core.py`, run by `certify.py` and again by `recompute.py`) tests the disjointness
  of interiors on **78897** pairs (prefilter: disks centred at the mean of the vertices, exact intersection
  area 0; `checks/logs/ILEP_S6A/certify.log`, `recompute_v1.log`, `recompute_v2.log`);
- the second verifier (`verifier/verify.py`, E3) tests **14691** pairs (prefilter: bounding boxes; test: a
  separating edge line; `checks/logs/ILEP_S6A/verify.log`, `verify_v1_E1E6.log`).

## Role of E4

E4 is **not** used for the tiling. It shows that translations with |a| ≥ 2 or |b| ≥ 2 put every pair of points
at distance > 1, so that the list of contributing pairs of E5 (and of the certifier) is complete; this is what
makes the bound on p5 complete. The completeness of the translations needed for the tiling is the bound
|t| ≤ 2 R_max inside E3.

## Remarks

- The identification "pieces of colour c = hexagon c minus the islands" is descriptive only; the certificate
  does not use it. For ILEP_S6A it was checked exactly, independently of the certifier, by
  `checks/check_decomposition.py` (log `checks/logs/ILEP_S6A/check_decomposition.log`): each piece of
  colour c < 4 lies in hexagon c, meets no island translate, and the areas add up exactly.
- The winding number 1 of the island is checked in floating point only by `island.py` (exactly by
  `checks/check_decomposition.py` for S6A). This plays no role in the validity, for the same reason.
- E1–E3 pass for every certificate of this repository, both with the verifier of this version and with the
  unmodified verifier of version 1 (tag `v1`), see `checks/logs/`.
