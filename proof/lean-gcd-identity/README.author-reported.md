# Primitive-triple filter: Lean proof artifact

This artifact proves, over integer coordinates, both:

1. `gcd(x,y) = gcd(y, gcd(m,n)^2)` for the composition of two primitive
   Pythagorean triples; and
2. `gcd(x,y)=1 ↔ gcd(y mod gcd(m,n), gcd(m,n))=1`.

No Euclidean parametrization, parity, positivity, or orientation hypotheses are
used. The proof source contains no `sorry` and declares no axioms.

## Pinned environment

- Lean: `v4.34.0`
- Mathlib tag: `v4.34.0`
- Mathlib commit used for the recorded build:
  `5ed2965256430c3649e86755f9576b54eca72435`

## Verification

```bash
lake update
lake build PrimitiveTripleFilter
lake env lean AxiomAudit.lean
```

Recorded local results:

- `lake build PrimitiveTripleFilter`: PASS, 1394 jobs
- `lake env lean AxiomAudit.lean`: exit code 0
- `#print axioms` for each public theorem reports only the standard
  Lean/Mathlib foundations `propext`, `Classical.choice`, and `Quot.sound`.

This is a new mathematical proof artifact. It does not modify or authorize the
v0.5 confirmatory benchmark, freeze, beacon selection, or performance run.
