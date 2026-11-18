#!/bin/bash
# reproduce.sh -- rerun everything from scratch with a NEW label, then compare with the
# shipped certificates.
#
# Usage: scripts/reproduce.sh LABEL_SUFFIX        (run from the repository root)
# Environment: PYTHON (default: python3), PROC (worker processes, default: 3),
#              WRAP (optional command prefix, e.g. a memory-limited scope).
# Outputs: out/DISQP32_<suffix>_*.json, out/ILEP256_<suffix>_*.json, out/ILEP_S6A_<suffix>_*.json,
#          logs in out/.
# Version 1 (tag v1): DISQP32 and ILEP256. Version 2 adds the recertification of ILEP_S6A (the
# colouring presented for v6 >= 51), whose inputs are read from data/ILEP_S6A through ILE_DATA_DIR,
# and exact threshold checks of the shipped version-2 certificates.
set -euo pipefail
SUF=${1:?usage: scripts/reproduce.sh LABEL_SUFFIX}
PY=${PYTHON:-python3}
PROC=${PROC:-3}
WRAP=${WRAP:-}
mkdir -p out
D=DISQP32_$SUF
I=ILEP256_$SUF
S=ILEP_S6A_$SUF
stamp() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
stamp "certify $D"
$WRAP $PY -B certifier/certify.py DISQP 1/192 256 --N 32 --proc "$PROC" --rounds 4 --label "$D" --out out > "out/$D.certify.log" 2>&1
stamp "certify $I"
$WRAP $PY -B certifier/certify.py ILEP 1/203 1024 --pas 1 --proc "$PROC" --rounds 6 --label "$I" --out out > "out/$I.certify.log" 2>&1
stamp "certify $S"
$WRAP env ILE_DATA_DIR=data/ILEP_S6A $PY -B certifier/certify.py ILEP 1/239 1024 --pas 1 --proc "$PROC" --rounds 6 --label "$S" --out out > "out/$S.certify.log" 2>&1
for L in "$D" "$I" "$S"; do
  stamp "recompute and verify $L"
  $WRAP $PY -B certifier/recompute.py "$L" --dir out --proc "$PROC" > "out/$L.recompute.log" 2>&1
  $WRAP $PY -B verifier/verify.py "$L" --dir out --proc "$PROC" > "out/$L.verify.log" 2>&1
done
$PY -B verifier/u_bounds.py > "out/u_bounds_$SUF.log" 2>&1
$PY -B checks/check_threshold.py "$S" out 239 > "out/$S.threshold.log" 2>&1
# exact threshold checks of the shipped version-2 certificates (Fraction arithmetic, a few seconds)
for pair in ILEP_S5B:205 ILEP_S5E:232 ILEP_S6A:239 ILEP_S7_93:239; do
  $PY -B checks/check_threshold.py "${pair%%:*}" certificates "${pair##*:}" > "out/${pair%%:*}_shipped_$SUF.threshold.log" 2>&1
done
# compare with the shipped files (identical except for the "nom" field of the certificate)
for pair in "DISQP32:$D" "ILEP256:$I" "ILEP_S6A:$S"; do
  ref=${pair%%:*}; new=${pair##*:}
  cmp "certificates/${ref}_config.json" "out/${new}_config.json"
  diff <(sed "s/\"nom\": \"$new\"/\"nom\": \"$ref\"/" "out/${new}_certificat.json") "certificates/${ref}_certificat.json" > /dev/null
  echo "$ref: colouring and certificate identical to the shipped files (except the label)"
done
grep -h "RESULT\|VERDICT\|CONFIRMED\|THRESHOLD_\|OK: u(28)" out/*"_$SUF".*.log "out/u_bounds_$SUF.log"
stamp "done"
