#!/bin/bash
# reproduce.sh -- rerun everything from scratch with a NEW label, then compare with the
# shipped certificates.
#
# Usage: scripts/reproduce.sh LABEL_SUFFIX        (run from the repository root)
# Environment: PYTHON (default: python3), PROC (worker processes, default: 3),
#              WRAP (optional command prefix, e.g. a memory-limited scope).
# Outputs: out/DISQP32_<suffix>_*.json, out/ILEP256_<suffix>_*.json, logs in out/.
set -euo pipefail
SUF=${1:?usage: scripts/reproduce.sh LABEL_SUFFIX}
PY=${PYTHON:-python3}
PROC=${PROC:-3}
WRAP=${WRAP:-}
mkdir -p out
D=DISQP32_$SUF
I=ILEP256_$SUF
$WRAP $PY -B certifier/certify.py DISQP 1/192 256 --N 32 --proc "$PROC" --rounds 4 --label "$D" --out out > "out/$D.certify.log" 2>&1
$WRAP $PY -B certifier/certify.py ILEP 1/203 1024 --pas 1 --proc "$PROC" --rounds 6 --label "$I" --out out > "out/$I.certify.log" 2>&1
for L in "$D" "$I"; do
  $WRAP $PY -B certifier/recompute.py "$L" --dir out --proc "$PROC" > "out/$L.recompute.log" 2>&1
  $WRAP $PY -B verifier/verify.py "$L" --dir out --proc "$PROC" > "out/$L.verify.log" 2>&1
done
$PY -B verifier/u_bounds.py > out/u_bounds.log 2>&1
# compare with the shipped files (identical except for the "nom" field of the certificate)
for pair in "DISQP32:$D" "ILEP256:$I"; do
  ref=${pair%%:*}; new=${pair##*:}
  cmp "certificates/${ref}_config.json" "out/${new}_config.json"
  diff <(sed "s/\"nom\": \"$new\"/\"nom\": \"$ref\"/" "out/${new}_certificat.json") "certificates/${ref}_certificat.json" > /dev/null
  echo "$ref: colouring and certificate identical to the shipped files (except the label)"
done
grep -h "RESULT\|VERDICT\|CONFIRMED" out/*"_$SUF".*.log
