# Primitive-triple filter — candidate confirmatory specification v0.3

State: **PRE-GATE / NOT FROZEN / NO CONFIRMATORY RUN**. v0.1 remains an
exploratory pilot; v0.2 failed review before freeze. Neither supplies
confirmatory observations. This repair changes the primary comparator and
exercises the full benchmark path under a separate smoke seed.

## C1 — bounded performance claim and comparators

At nominally 100,000-bit input coordinates in a constructed family with a
large common hypotenuse factor `q` and a rejected product, compare the dynamic
modular filter against **`direct`**, the fastest measured available arithmetic
baseline for this family. `direct` computes full `(x,y)` and `gcd(x,y)`.
`optimized` computes `gcd(m,n)` first and skips the coordinate gcd if `q=1`;
it is diagnostic only. `filtered` computes `q`, then the modular `y` test, and
computes full coordinates only for accepted candidates. All methods return the
same accepted coordinates or `None` for rejection.

The prior `optimized` baseline is slower than `direct` when `q>1`; using it as
the primary comparator would exaggerate the reported speed ratio. The `q=1`
control isolates savings from a smaller-operand gcd and is **not pruning**.
`large_accept` quantifies overhead when the filter cannot discard a candidate.
Any rejection-specific benefit is interpreted with both acceptance and
rejection controls in view; the primary test compares `direct` with `filtered`
in the `large_reject` family only.

The pilot already made a ratio above 1 likely. A threshold at 1.00 tests a
predictable implementation advantage, **not** a risky mathematical prediction,
novel algorithmic complexity class or encryption improvement. A later release
must say so.

## C2 — future seed and fixture custody

The confirmatory seed is **not present in this artifact**. After an independent
review of exact script/spec bytes, record a signed or publicly timestamped
freeze approval containing the SHA-256 of each, an `approved_at_utc` timestamp,
the reviewer, and the *future* scheduled `quicknet` round. Choose the first
round strictly after `approved_at_utc + 600 seconds`, using the pinned drand
quicknet chain hash, genesis and period:

```text
chain hash   52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971
genesis     1689232296 UNIX seconds; round 1 at genesis
period      3 seconds
round       floor((approved_at_utc + 600 - genesis) / 3) + 2
```

After that round is published, fetch the exact round from
`https://api.drand.sh/v2/chains/<chain hash>/rounds/<round>` and archive its
JSON, source URL, signature and randomness. An independent reviewer must verify
the beacon signature against the pinned chain through a drand client, document
the client/version and evidence, and verify publication after the freeze.
The Python script checks round selection, source URL, timestamps, lengths and
`SHA-256(signature) = randomness`; **this hash check is not BLS signature
verification** and cannot establish that a freeze record was honestly
timestamped. Missing external verification is a gate failure. If the selected
beacon is unavailable, defer the run; do not choose a different round after
seeing its output.

Seed construction is byte exact:

```text
SHA256( ASCII("pythagorean-filter-v0.3") || 0x00 ||
        script_sha256_bytes || spec_sha256_bytes || chain_hash_bytes ||
        round_uint64_big_endian || beacon_randomness_bytes )
```

Each family's fixture/order/bootstrap stream is independently derived as
`SHA256(ASCII(seed_hex + "|" + label + "|" + family))`, interpreted as a big
endian integer for Python `random.Random`. Labels are `fixtures`, `order`,
`bootstrap`. The smoke mode uses a separate literal seed, 256-bit fixtures and
discarded timings. Neither v0.1 nor v0.2 seed is used for v0.3 fixtures.

Construct primitive base triples with odd `u`, even `v`, `gcd(u,v)=1`, high bits
set and `(u²-v², 2uv, u²+v²)`. In `large_reject` and `large_accept`, use a
shared large primitive factor of roughly half the input bit length, pairwise
coprime hypotenuse cofactors, and opposite/same conjugation respectively.
`coprime_accept` has `q=1`. Construct 30 distinct pairs in each family; reject
duplicate full-input digests across families. Check both input triples,
intended `q`, expected accept/reject label and exact agreement of the three
methods before timing. Check each measured return against the oracle **after**
the timer stops; any mismatch aborts with no performance verdict.

The conjugate orientation is only a fixture construction technique. It is
**not** a hypothesis of the Lean domain theorem.

## C3 — unit, timing and pre-registered analysis

One independently generated pair is one analysis unit. For each pair, warm all
three methods once, then take eight rounds in separately randomized method
order. `time.perf_counter_ns` encloses only each method call. Disable garbage
collection during each timed call; enable it for warmup, output comparison,
hashing, bootstrap and serialization. Fixture construction, prevalidation and
post-timer comparison are excluded equally for all methods.

For each pair calculate the median of eight elapsed nanosecond measurements
for each method. Primary pair ratio is `R_i = median(direct_i) /
median(filtered_i)`. Primary statistic is the median of the 30 `R_i` in
`large_reject`. Bootstrap the 30 ratios with replacement 10,000 times using
the family-specific bootstrap stream; for each resample take its median. Sort
the 10,000 medians and use zero-based indices 250 and 9749 as the 95%
percentile interval. **Primary rule: lower endpoint > 1.00.** No larger
minimum effect is claimed. `optimized` and the two acceptance families are
descriptive controls, not extra ways to satisfy the primary rule.

## C4 — complete-path smoke, environment and outcomes

`--smoke` must run `run_family` end to end for all three families on three
256-bit pairs each, including timed calls, every comparison, bootstrap and
JSON serialization. Its timings are discarded and do not use the beacon.
`--confirmatory` requires a gate record binding reviewed code/spec hashes,
prepublished freeze evidence, selected future beacon round, verified beacon
evidence and a same-day operator attestation that the machine was idle under a
stated method. That attestation is human evidence, not inferred from load
average. The output records Python version, platform, CPU model from
`/proc/cpuinfo` when present, affinity/core count, available governor/turbo
settings, and load averages before and after execution. Unsupported system
fields are recorded as null rather than guessed.

- **INVALID / BLOCKED:** missing or non-conforming independent freeze/beacon
  evidence; fixture collision or invalid triple; any comparator disagreement
  during precheck, warmup or a timed call; missing raw measurements or
  environment evidence. Do not issue a performance PASS/FAIL.
- **PERFORMANCE PASS:** valid 30-pair primary run and bootstrap interval lower
  endpoint strictly above 1.00.
- **PERFORMANCE FAIL:** valid primary run with lower endpoint at or below 1.00.
  Keep it; never tune and relabel it confirmatory.

The script records a threshold result as `EXECUTED_NOT_ADJUDICATED`; an
independent reviewer must adjudicate the bytes, environment, beacon, paired
data and exact analysis before a performance verdict. This benchmark gate can
run while Lean work proceeds. Public mathematical claims require a separate
Lean kernel PASS on the **complete** domain theorem, with dependencies pinned
and no `sorry` or unsupported axioms. A later Zenodo deposit is a distinct
release decision with narrow claim scope.

## References for the selected beacon (review at freeze)

- drand HTTP API and independently verified client guidance:
  https://docs.drand.love/developer/http-api/
- drand quicknet chain hash and 3-second period:
  https://docs.drand.love/developer/API-v2/drand-http-api/
- drand protocol genesis/round convention:
  https://docs.drand.love/docs/specification/
