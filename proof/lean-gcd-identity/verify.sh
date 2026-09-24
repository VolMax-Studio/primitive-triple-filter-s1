#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "$0")"

expected_proof_sha="5b97b0a5eea88415f98783443c4f15fc3b4d1030fd3b0e99826110795a0216f5"
expected_mathlib_rev="5ed2965256430c3649e86755f9576b54eca72435"

actual_proof_sha="$(sha256sum PrimitiveTripleFilter.lean | cut -d' ' -f1)"
if [[ "$actual_proof_sha" != "$expected_proof_sha" ]]; then
  echo "FAIL: frozen Lean proof hash mismatch" >&2
  exit 1
fi

actual_mathlib_rev="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(next(p["rev"] for p in d["packages"] if p["name"] == "mathlib"))' lake-manifest.json)"
if [[ "$actual_mathlib_rev" != "$expected_mathlib_rev" ]]; then
  echo "FAIL: Mathlib manifest revision mismatch" >&2
  exit 1
fi

sha256sum -c SHA256SUMS

if ! command -v grep >/dev/null 2>&1; then
  echo "FAIL: grep is required for the forbidden-token scan" >&2
  exit 1
fi

proof_files=(PrimitiveTripleFilter.lean YZeroTest.lean AxiomAudit.lean)
forbidden_pattern='(^|[^[:alnum:]_`])(sorry|admit)([^[:alnum:]_`]|$)|native_decide|^[[:space:]]*axiom([[:space:]]|$)'

set +e
forbidden_output="$(grep -En -- "$forbidden_pattern" "${proof_files[@]}" 2>&1)"
forbidden_rc=$?
set -e

case "$forbidden_rc" in
  0)
    printf '%s\n' "$forbidden_output" >&2
    echo "FAIL: forbidden proof escape found" >&2
    exit 1
    ;;
  1)
    ;;
  *)
    printf '%s\n' "$forbidden_output" >&2
    echo "FAIL: forbidden-token scan did not execute cleanly (grep rc=$forbidden_rc)" >&2
    exit 1
    ;;
esac

lake build PrimitiveTripleFilter
lake build Mathlib.Tactic.NormNum.GCD
lake env lean YZeroTest.lean
lake env lean AxiomAudit.lean
sha256sum -c SHA256SUMS

echo "PASS: primitive-triple-filter-s1 Lean proof"
