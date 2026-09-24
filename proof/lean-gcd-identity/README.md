# Lean gcd identity — reproducible gate artifact

This directory freezes the first formal rung of the primitive-Pythagorean
composition investigation.  Over integer coordinates it proves:

```text
gcd(x,y) = gcd(y, gcd(m,n)^2)
```

and its modular primitivity criterion:

```text
gcd(x,y) = 1 ↔ gcd(y mod gcd(m,n), gcd(m,n)) = 1.
```

The theorem uses only two primitive right-triangle hypotheses and the defining
equations for `x` and `y`.  It adds no parity, positivity, orientation, or
nonzero-coordinate assumptions.

## Frozen source and environment

- `PrimitiveTripleFilter.lean` SHA-256:
  `5b97b0a5eea88415f98783443c4f15fc3b4d1030fd3b0e99826110795a0216f5`
- Lean: `v4.34.0`
- Lean commit: `293d5d0c0c3f3dded4688b3ccd6a33939ac5102b`
- Mathlib: `v4.34.0`
- Mathlib commit: `5ed2965256430c3649e86755f9576b54eca72435`

The original author-side report is preserved unchanged in
`README.author-reported.md`.

## Reproduction

Do **not** run `lake update`: `lake-manifest.json` is a frozen input and must
not be re-resolved.  Fetching the Mathlib cache is optional:

```bash
# Optional acceleration:
lake exe cache get

# Authoritative end-to-end gate:
./verify.sh
```

The verifier checks all hashes before and after the build, rejects a changed
Mathlib revision, performs a fail-closed forbidden-token scan, builds the
kernel proof, runs the complete-cancellation `y = 0` test, and checks guarded
axiom output for both public theorems.

## Scope boundary

This proof artifact is independent of the v0.5 benchmark track.  It does not
freeze or authorize the confirmatory performance run, and makes no claim about
speed, cryptography, publication priority, or mathematical novelty.  The
identity should be treated as likely classical/folklore unless a literature
review establishes otherwise.
