# Verification logs of the version-2 certificates

These are the logs of the runs that produced and checked the certificates `ILEP_S5B`, `ILEP_S5E`, `ILEP_S6A`
and `ILEP_S7_93` (and the Monte Carlo control run on `ILEP256`). They were run on a laptop (Linux x86_64,
Python 3.12.3, python-flint 0.9.0) under `/usr/bin/time -v`, whose report ends each log. **Local absolute
paths were rewritten** to the repository-relative names (`certificates/`, `data/<label>/`, `checks/...`,
`python`); nothing else was changed. The runs were made before the files were moved into this repository, in
the order: certify, threshold check, verify (N included), verify of version 1 (E1–E6), recompute of version 1,
Monte Carlo.

**Code used.**
- `certify.log`: `certifier/certify.py` with the modified `certifier/island.py` (free centre and angles,
  splitting of non-convex hexagons). The code was the same as in this commit except for docstrings, comments
  and printed comparisons; `core.py`, `geometry.py`, `certify.py` and `colourings.py` are byte-identical to
  version 1 (tag `v1`). The inputs were read through `ILE_DATA_DIR=data/<label>`.
- `check_threshold.log`: an earlier version of `checks/check_threshold.py` (same exact checks, French output;
  `SEUIL_OK` = threshold check passed).
- `verify.log`: `verifier/verify.py` of version 2 (it differs from version 1 only by the printed comparisons).
- `verify_v1_E1E6.log`, `recompute_v1.log`: the **unmodified version-1** `verifier/verify.py` (up to E6, via
  `checks/verify_E1E6.py`) and `certifier/recompute.py` of tag `v1`.
- `compare_pairs.log` (S5B, S5E): `checks/compare_pairs.py`, run against the version-1 code.
- `check_decomposition.log`, `regenerate_config.log` (S6A): exact check of the splitting of the non-convex
  hexagons (`checks/check_decomposition.py`), and regeneration of the colouring by `island.py` with a result
  identical to `certificates/ILEP_S6A_config.json` (the small regeneration script is not included; the same
  regeneration is done by `scripts/reproduce.sh`).
- `diag_N.log` (S7_93): `checks/diag_N.py`, the diagnostic of the alert of the numerical check N.
- `mc.log`: `montecarlo/mc_p5.py` (see `montecarlo/README.md`).
- `ILEP_S6A/recompute_v2.log` (added after the external audit of version 2): `certifier/recompute.py` of this
  version (which also prints the comparison with 1/243), run once on the shipped certificate with `--proc 3`;
  its header gives the exact versions of python, python-flint, numpy and mpmath of the interpreter used.
- `ILEP_S6A/check_threshold_243.log`, `ILEP_S7_93/check_threshold_243.log` (same date):
  `checks/check_threshold.py` of this version against the threshold 1/243.

**Results.**

| label | certified bound | verify (E1–E6 / N) | verify v1 E1–E6 | recompute v1 | Monte Carlo |
|---|---|---|---|---|---|
| ILEP_S5B | 24135541/(5·10⁹) | passed / passed | passed | confirmed | 0.0048140 ± 1.1·10⁻⁵ |
| ILEP_S5E | 42565529/10¹⁰ | passed / passed | passed | confirmed | 0.0042476 ± 1.0·10⁻⁵ |
| ILEP_S6A | 41149783/10¹⁰ | passed / passed (min margin 5.7·10⁻¹⁰) | passed | confirmed | 0.0041071 ± 1.0·10⁻⁵ |
| ILEP_S7_93 | 5137931/(1.25·10⁹) | passed / **alert** (2 boxes) | passed | confirmed | 0.0041073 ± 1.0·10⁻⁵ |

The alert of N for ILEP_S7_93 is explained in the README of the repository: in boxes 263 and 264 the certified
bound exceeds the numerical estimate of the integral by about 3·10⁻²¹ (relative 2.6·10⁻¹⁴ and 3.1·10⁻¹⁴), below the
absolute floor 10⁻¹⁶ of the error estimate of N; no box bound is below the numerical estimate of the integral; the check N
itself still fails for this variant.
