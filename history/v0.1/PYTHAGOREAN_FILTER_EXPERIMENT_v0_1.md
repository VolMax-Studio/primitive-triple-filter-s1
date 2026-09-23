# Primitive-triple branch filter — exploratory experiment v0.1

Status: **EXPLORATORY / PILOT**. The mathematical domain criterion has a paper proof.
The supplied Lean fragments have not passed the Lean kernel. This document is not a
G2 PASS, a novelty claim, a complexity theorem, or an authorization to publish.

## Claims separated

- **Mathematics:** given two primitive integer Pythagorean triples and their
  complex-coordinate product `(x,y)`, primitiveness is equivalent to
  `gcd((a*d+b*c) mod q, q) == 1`, where `q = gcd(m,n)`.
- **Software correctness:** on each constructed input, the filter and direct
  full-coordinate `gcd(x,y)` must agree on both the decision and, if accepted,
  the returned coordinates. Zero mismatches is a required validity condition.
- **Performance:** an implementation-specific comparison of elapsed time per
  candidate, with input construction excluded and every operation in each
  decision path included. No inference about all inputs, all hardware, or
  asymptotic running time follows from this pilot.

## Candidate families and controls

Base triples are generated as `(u²-v², 2uv, u²+v²)` using odd `u`, even `v`,
`gcd(u,v)=1` and a pinned PRNG seed. Verify both Pythagorean equality and
primitive coordinates for every input. Construct independent base hypotenuses
with gcd one. The five families are:

| Family | Shared hypotenuse factor | Orientation | Expected result |
| --- | --- | --- | --- |
| coprime_accept | `q=1` | independent | accept |
| small_accept | `q=5` | both multiplied by `3+4i` | accept |
| small_reject | `q=5` | one by `3+4i`, other by `3-4i` | reject |
| large_accept | `q≈B/2` bits | both carry a shared large primitive factor with matching orientation | accept |
| large_reject | `q≈B/2` bits | shared large factor in opposite orientations | reject |

The cofactors' hypotenuses must be pairwise coprime and coprime to the shared
factor. This creates controlled accept/reject cases; it is **not** a sample of
the frequency of either outcome among arbitrary triples. Algebraic construction
and the independently computed direct `gcd` both check the expected label.

## Compared programs and timing

`direct`: compute both full coordinates, compute their gcd, and return the pair
only if primitive. `filtered`: compute `q=gcd(m,n)`; for `q>1`, compute all four
required input residues, the modular `y` and `gcd(r,q)`; compute full coordinates
only if accepted. Both get the same already constructed input triples and must
return exactly the same value. No cached `q` or residues are supplied to the
dynamic method. Timing includes all allocations and operations inside each
method. Exclude fixture generation and validity checks from both timings.

The pilot uses nominal input-coordinate sizes 1,024 / 8,192 / 65,536 / 100,000
bits, respectively 12 / 6 / 3 / 2 independent pairs per family, 7 / 7 / 5 / 5
repeated timings per batch, alternating method order, with GC disabled only
during measurement. The reported statistic is the ratio of batch medians in
microseconds per pair. Repeated timings on the *same* pairs are not independent
observations; small samples at 100,000 bits make these pilot ratios unstable.
The raw timing arrays, seed, Python/platform information, and script SHA-256
are recorded in `pythagorean_filter_results_v0_1.json`.

## Pilot result and interpretation

All 20 family/size cells had zero direct-vs-filter mismatches. At 100,000-bit
nominal inputs, the median direct/filter ratios were: `q=1` accept 2.87;
`q=5` accept 2.79 and reject 4.67; large `q` accept 1.54 and reject 1.71.
These are measurements of the listed Python implementation on one runtime.
The large-`q` rows contain only two independent pairs each.

## Next controlled gate

1. Assemble an exact Lean project with toolchain, dependency revision, full
   source and executable command. Kernel-check every used lemma and final domain
   criterion; reject any `sorry`, new axioms, or placeholder assumptions in the
   main theorem. A clean paper proof and pre-execution review are not PASS.
2. Independently review fixture construction, validity assertions, code bytes,
   environment and primary comparison before a fresh measurement. Freeze those
   items, including seed policy. Pilot results cannot become confirmatory by
   relabeling them.
3. For a confirmatory performance test, use at least 30 fresh constructed pairs
   in the 100,000-bit large-`q` reject family; use paired timings and randomized
   order, retain raw samples and environment details. Register the precise
   analysis and acceptance rule *before* running it; distinguish correctness
   from speed. Include large-`q` accepts as a cost control.
4. Public reporting, if later warranted, should describe a known mathematical
   setting and a bounded, reproducible implementation comparison. It must not
   imply a new encryption scheme or a general complexity breakthrough.

The analogy to `battery-deposit-semantics-s2` concerns order of evidence and
gates only; its historical G2 status does not transfer to this experiment.
