# Exploratory exact-gcd identity (not part of the v0.5 freeze candidate)

**Status: paper argument and finite check only; no Lean kernel PASS.** The pinned
v0.5 specification, script, tests, manifest and recorded observations are not
modified by this exploration. No confirmatory fixtures or future beacon were used.

Let `(a,b,m)` and `(c,d,n)` be primitive integer Pythagorean triples:
`a²+b²=m²`, `c²+d²=n²`, `gcd(|a|,|b|)=gcd(|c|,|d|)=1`. Set
`x=ac−bd`, `y=ad+bc`, and `q=gcd(|m|,|n|)` (so `q>0`).

## Candidate theorem and paper argument

The stronger target is **`gcd(|x|,|y|) = gcd(|y|,q²)`**. Consequently,
`gcd(|x|,|y|)=1 ↔ gcd(|y|,q)=1 ↔ gcd(|y| mod q,q)=1`.

1. Put `g=gcd(|x|,|y|)`. The ring identities
   `cx+dy=a n²`, `cy−dx=b n²`, `ax+by=c m²`, `ay−bx=d m²`
   show that `g` divides `a n²`, `b n²`, `c m²`, and `d m²`.
   Bézout for both primitive input legs yields `g∣n²` and `g∣m²`.
   The standard gcd-of-squares identity gives `g∣q²`. As `g∣y`,
   `g∣gcd(|y|,q²)`.
2. Put `h=gcd(|y|,q²)`. Since `q∣m` and `q∣n`, `q²∣mn`.
   Thus `h∣mn`; also `h∣y`. The norm identity
   `x²+y²=m²n²` gives `h²∣x²`. Integer square divisibility
   (`h²∣x² → h∣x`) gives `h∣gcd(|x|,|y|)`.
3. The two divisibilities and nonnegative gcds give equality. Finally,
   `gcd(|y|,q²)=1 ↔ gcd(|y|,q)=1` by prime divisors, and the
   modular equivalence is Euclid's gcd remainder identity.

The square-divisibility step is an explicit Lean proof obligation. This
argument is not a checked Lean artifact, and the finite check cannot prove it.

## Reproducible finite falsification attempt

From this directory run `python3 check_gcd_identity.py`. It enumerates
primitive triples with `|m|≤1000`, four orientations/sign patterns per Euclid
parameter pair, and four degenerate unit triples. Observed on Python 3.12:

```json
{"candidate_identity": "gcd(x,y) = gcd(y,gcd(m,n)^2)", "max_hypotenuse": 1000, "mismatches": 0, "nonprimitive_products": 32368, "ordered_compositions": 404496, "primitive_signed_oriented_triples": 636, "shared_hypotenuse_factor": 63360, "status": "FINITE_CHECK_ONLY_NOT_LEAN_PROOF"}
```

Coverage is a finite search of generated examples, not all integer triples.
There is no conclusion about asymptotic cost or cryptography.

## Kernel gate

Formalize the exact identity for all integer inputs under *only* the two norm
equations and two primitive-leg gcd assumptions, with no orientation assumption,
`sorry`, or new axioms. Check it in pinned Lean/Mathlib with the kernel; report
the toolchain and dependency revisions. Derive the primitive and modular filter
corollaries. Until then the public mathematical claim remains unverified.
