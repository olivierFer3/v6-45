# Monte Carlo check of p5 (floating point, not a proof)

`mc_p5.py` estimates p5, the probability that a uniformly random unit segment is monochromatic, for a colouring
file `<label>_config.json`. It was written from scratch, by an AI agent that had not written the certifier, and
it imports no code of this repository: it reads only the JSON file and uses numpy and shapely. Comments and
printed keywords are in French (`graine` = seed, `lot` = batch, `segments_exclus` = discarded segments,
`points_non_couverts` = uncovered points, `ecart_type` = standard deviation, `meme_couleur` = same colour).

**Method.** Rational vertices are converted to doubles. Each piece is checked to be convex and is turned into
normalised half-planes. The translates `piece + i g1 + j g2` meeting the cell are listed per square of a
256 × 256 grid in lattice coordinates. For each segment, the origin is `s g1 + t g2` with `s, t ~ U[0, 1)`,
the angle is `θ ~ U[0, 2π)`, and both end points are reduced modulo the lattice and tested against all
candidate pieces of their square. A point covered by no piece (tolerance 1e-12), or by the interior of two or
more pieces, is counted separately; there were none. The standard deviation is σ = √(p(1−p)/n).

```bash
python3 -B montecarlo/mc_p5.py certificates/ILEP_S6A_config.json 4e7 20261119 1000000
```

## Results (n = 4·10⁷ segments each, 8·10⁷ points tested each, 0 uncovered, 0 doubly covered)

| colouring | seed | Monte Carlo p5 | σ | certified bound | deviation from the bound | log |
|---|---|---|---|---|---|---|
| ILEP256 (control, version 1) | 20261119 | 0.0049223000 | 1.11·10⁻⁵ | 0.0049233542 (floating value 0.0049196874) | −0.09σ (+0.24σ from the floating value) | `checks/logs/ILEP256/mc.log` |
| ILEP_S5B (intermediate) | 20261120 | 0.0048140000 | 1.09·10⁻⁵ | 0.0048271082 | −1.20σ | `checks/logs/ILEP_S5B/mc.log` |
| ILEP_S5E (intermediate) | 20261121 | 0.0042476000 | 1.03·10⁻⁵ | 0.0042565529 | −0.87σ | `checks/logs/ILEP_S5E/mc.log` |
| **ILEP_S6A (presented)** | 20261119 | 0.0041070500 | 1.01·10⁻⁵ | 0.0041149783 | −0.78σ | `checks/logs/ILEP_S6A/mc.log` |
| ILEP_S7_93 (variant) | 20261119 | 0.0041072750 | 1.01·10⁻⁵ | 0.0041103448 | −0.30σ | `checks/logs/ILEP_S7_93/mc.log` |

No estimate exceeds the corresponding certified bound. The control ILEP256 is recovered. S6A and S7_93 used the same seed, so their two estimates are correlated.

**Limits.** With σ ≈ 10⁻⁵, this check can only detect an error of the certificate of about 3·10⁻⁵ or more. It
is independent of the certifier's code, not of the AI that wrote both. The rigour rests on exact rational
arithmetic and Arb ball arithmetic.

## Where the gain comes from (heuristic)

A decomposition by colour (n = 10⁷, σ ≈ 2·10⁻⁵) of ILEP256 and ILEP_S5E, an intermediate step on the way to
ILEP_S6A, gave the following, in units of 10⁻³:

| | ILEP256 intra / inter | ILEP_S5E intra / inter |
|---|---|---|
| colours 0 + 2 | 1.156 / 0.452 | 0.845 / 0.414 |
| colours 1 + 3 | 2.387 / 0.830 | 1.679 / 0.846 |
| colour 4 (island) | 0.032 / 0.079 | 0.191 / 0.271 |
| total | 4.936 | 4.246 |

"Intra" counts the segments with both end points in the same region and "inter" those with end points in two
distinct translates. The intra contribution of the four hexagons drops by 29 % (3.54 → 2.52), partly offset by
the island, which is longer and now contains unit chords, and by a small increase of the inter part. In
ILEP_S5E the hexagons of colours 0/2 are sheared into oblique elongated shapes (area 0.540 → 0.588, minimal
width 0.74 → 0.93), the hexagons 1/3 shrink by 7 %, and all hexagon regions have a diameter only slightly
above 1 (1.12–1.13). A plausible explanation, not proved: when the diameter of a region exceeds 1 only
slightly, the measure of the unit segments inside it depends very non-linearly on that excess and on the shape
of opposite corners. ILEP_S6A continues the same deformation, until the hexagons 0/2 become non-convex (one
reflex vertex each).
