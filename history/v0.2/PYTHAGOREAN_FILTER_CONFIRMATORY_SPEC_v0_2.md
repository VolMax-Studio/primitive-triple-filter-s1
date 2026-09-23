# Primitive-triple filter — candidate confirmatory specification v0.2

State: **PRE-GATE / NOT FROZEN / NO CONFIRMATORY RUN**.
This is a proposed repair after the v0.1 pilot and external BLOCKED review.
The pilot remains exploratory; its seed, data and timings cannot be reused as
confirmatory observations. This text and its companion script require an
independent artifact review, versioned bytes and an explicit gate record before
`--confirmatory` is allowed. Lean verification can proceed concurrently, but no
public claim of mathematical verification may rely on this benchmark before the
full Lean theorem has a kernel PASS with the toolchain and imports pinned.
The v0.1 result field `correctness_mismatches: 0` was an assertion-gated
constant, not a measured counter; its batch repetitions were not independent
pair observations. Neither field is promoted to confirmatory evidence.

## C1 — claim and comparators

Primary claim is confined to this Python implementation, this constructed
input family and environment: at nominally 100,000-bit input coordinates with
a large shared `q` and opposite Gaussian orientation (so the candidate is
rejected), the modular filter is faster per candidate than an optimized
arithmetic baseline that already uses `gcd(m,n)` to accept `q=1` immediately.
No novelty, general asymptotic, encryption, or population-wide frequency claim.

Three programs receive the same already generated inputs:

1. `direct`: compute full `x,y` and their gcd, return coordinates only on accept.
2. `optimized`: compute `q=gcd(m,n)`, compute full `x,y`, accept for `q=1`,
   otherwise test `gcd(x,y)`. This is the **primary baseline**.
3. `filtered`: compute `q`; if `q>1`, reduce four input coordinates modulo `q`,
   compute `r=(ad+bc) mod q` and `gcd(r,q)`; compute full `x,y` only if accepted.

`direct` is an explanatory naive baseline. The `q=1` control isolates the
smaller-operand gcd shortcut, which is **not branch pruning**. The large-`q`
accept control measures the filter overhead when nothing is cut. The difference
between reject and accept cells is descriptive and is not itself the primary
statistic because their arithmetic paths differ.

## C2 — fixture generation and fresh seed

Confirmatory seed, generated after the pilot and recorded before any v0.2 run:

```text
0186c26d4907c55309ecc09c23cfecf8
```

Each family obtains an independent Python `Random` stream seeded by the integer
SHA-256 of ASCII `seed_hex + "|fixtures|" + family`; method-order and bootstrap
streams use separate labels. Family iteration order cannot change fixtures.
The `--smoke` mode uses a different literal seed and 256-bit inputs, so it never
consumes any confirmatory fixture or performance stream. Do not inspect
confirmatory fixtures or timings before review and freeze.

Primitive base triples use odd `u`, even `v`, `gcd(u,v)=1`, high bits set and
`(u²-v², 2uv, u²+v²)`. At each size, independent base triples are selected by
rejection sampling until their hypotenuses are pairwise coprime. For the large
`q` families, multiply both by a common primitive factor whose hypotenuse has
roughly half the nominal input bit length; conjugate that factor in the second
input for `large_reject` and keep the same orientation for `large_accept`.
The `coprime_accept` family has `q=1`. Each family contains exactly 30 distinct
generated pairs (distinct full-input SHA-256 digests), with no pair shared
across families. Every pair is checked for primitive input coordinates,
Pythagorean identity, the intended `q`, expected outcome, and exact agreement
among all three comparator returns before measurement. The measured calls are
also compared with the cached oracle after each timer stops.

## C3 — timing unit and analysis

Nominal bit length `B=100000`. The independent unit is one constructed pair,
**not** a repeat of a batch. For each pair, warm up all three methods once
outside timing, then perform eight paired rounds. Each round times all three
methods once in an order randomized from the separate order stream. The timer
is Python `time.perf_counter_ns`; disable garbage collection only during timed
rounds. Input generation, prevalidation, hashing and output comparison after
timer stop are excluded from every method. The methods themselves include all
arithmetic and allocation for their decision and required output.

For each pair and method, take the median of its eight measured durations in
nanoseconds. Define its ratio `R_i = median(optimized_i)/median(filtered_i)`.
Primary statistic `R = median(R_i)` across **30 independent pairs** in
`large_reject`; no batch mean or pseudo-replication. Resample the 30 ratios
with replacement 10,000 times using the independent bootstrap stream;
calculate each resample median, sort the 10,000 medians, and take sorted
indices `250` and `9749` (zero based) for the percentile 95% interval.
The primary performance acceptance rule is **lower endpoint > 1.00**.
No minimum factor such as 4× is prespecified. Secondary `large_accept` and
`coprime_accept` ratios and raw timings are descriptive; no success inference
from them.

## C4 — outcomes and stop conditions

- **INVALID / BLOCKED:** no valid independent gate record bound to exact script,
  spec and seed; input validity fails; labels or input digests duplicate;
  either precheck or any measured call differs between methods; raw timings or
  environment metadata are missing. Do not report a performance PASS/FAIL.
- **PERFORMANCE PASS:** valid run, 30 primary pairs, zero comparator mismatches,
  and primary 95% interval lower endpoint strictly greater than 1.00.
- **PERFORMANCE FAIL:** valid run with the lower endpoint at or below 1.00.
  Keep the result; do not retune the acceptance rule and relabel it confirmatory.

`PERFORMANCE PASS` never implies Lean kernel PASS, mathematical novelty, or
crypto strength. A script-produced decision remains `EXECUTED_NOT_ADJUDICATED`
until independent review of environment, bytes, fixture digests and raw output.

## C5 — independent gate and later release

Before the run, an independent reviewer must check script/spec membership,
exact SHA-256s, fresh seed, fixed fixtures policy, comparators, analysis,
validity conditions, Python runtime and CPU environment description. Freeze
the reviewed bytes and approve a separate JSON gate record containing:
`status=APPROVED_FOR_CONFIRMATORY`, `script_sha256`, `protocol_sha256`,
`seed_hex`, `reviewer`, `approved_at_utc`. The executable checks those fields
and hashes before allowing `--confirmatory`. This mechanical check cannot
establish reviewer independence on its own. Version and retain the full gate
record, command, stdout, raw results and environment. The historical gate for
`battery-deposit-semantics-s2` does not count as this project's gate.

Lean artifact review must independently bind the **complete domain theorem**,
toolchain, imports, helper lemmas and absence of `sorry`/unsupported axioms;
modular-filter-only proofs do not close it. A performance run may occur after
its own reviewed freeze while Lean work continues. Public mathematical claims
wait for the Lean gate; public performance claims wait for the benchmark gate
and independent result review. Any later Zenodo deposit is a separate release
decision with narrowly stated claim scope.
