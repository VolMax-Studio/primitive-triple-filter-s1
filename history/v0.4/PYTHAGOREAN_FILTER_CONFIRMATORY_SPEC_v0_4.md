# Primitive-triple filter — candidate confirmatory specification v0.4

State: **PRE-GATE / NOT FROZEN / NO CONFIRMATORY RUN**. v0.1 remains an
exploratory pilot; v0.2 failed review before freeze. Neither supplies
confirmatory observations. v0.3 failed independent review before freeze on
chain genesis and one-attempt custody. No confirmatory observations exist.

## C1 — bounded performance claim and comparators

At nominally 100,000-bit input coordinates in a constructed family with a
large common hypotenuse factor `q` and a rejected product, compare the dynamic
modular filter against **`direct`**. In the independent review's exploratory
dry run (`n=3`, separate seed), `direct` was faster than the other available
comparator for this family. `direct` computes full `(x,y)` and `gcd(x,y)`.
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
genesis     1692803367 UNIX seconds; round 1 at genesis
period      3 seconds
round       floor((approved_at_utc + 600 - genesis) / 3) + 2
```

**Independent chain-constant check (separate freeze-review checklist item):**
obtain the selected mainnet chain's `/info` from
`https://api.drand.sh/52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971/info`;
verify `hash = 52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971`,
`genesis_time = 1692803367`, `period = 3`, and
`schemeID = bls-unchained-g1-rfc9380` against the pinned values above.
Record reviewer and evidence URL in the gate record's `chain_info`. Independently
recheck the scheduled round's release timestamp against these values. Agreement
between script and specification alone does not pass this check.

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
SHA256( ASCII("pythagorean-filter-v0.4") || 0x00 ||
        script_sha256_bytes || spec_sha256_bytes || chain_hash_bytes ||
        round_uint64_big_endian || beacon_randomness_bytes )
```

Each family's fixture/order/bootstrap stream is independently derived as
`SHA256(ASCII(seed_hex + "|" + label + "|" + family))`, interpreted as a big
endian integer for Python `random.Random`. Labels are `fixtures`, `order`,
`bootstrap`. The smoke mode uses a separate literal seed, 256-bit fixtures and
discarded timings. Earlier seeds are not used for v0.4 fixtures.

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
evidence, independently checked chain constants, a registered attempt, and an
operator attestation that the machine was idle under a stated method. The
attestation must follow the beacon observation, precede attempt registration,
and be no older than two hours when the script starts, regardless of UTC date.
That attestation is human evidence, not inferred from load
average. The output records Python version, platform, CPU model from
`/proc/cpuinfo` when present, affinity/core count, available governor/turbo
settings, and load averages before and after execution. Unsupported system
fields are recorded as null rather than guessed.

**Exactly one confirmatory attempt.** In the public freeze record, announce a
unique planned attempt ID and the exact UTC launch window from selected round
release plus 300 seconds through release plus 7,200 seconds (inclusive).
Before starting the process, publicly timestamp the attempt ID, script/spec
SHA-256, selected beacon round and signature, exact command, host ID and
operator in an append-only attempt ledger;
put its evidence URL and registration time in `execution`. The script checks
the registered ID, timing and presence of evidence and refuses a start outside
the announced window. Independent review checks the public timestamps and
ledger; the script cannot establish that those external records are genuine.

The **first invocation** of `--confirmatory` with this frozen package and
selected round consumes the single attempt, including failures, crashes and
interruptions. Record and publicly disclose every invocation and its start,
finish/interrupt time, command, exit status, stdout and stderr byte files and
their SHA-256 values (empty streams have the usual SHA-256). Immediately upon
process exit or interruption, before examining or interpreting the output,
submit the stdout SHA-256 to an independent public timestamp service; target
completion within five minutes and record actual submission/receipt timestamps
and evidence URL. Publish the raw streams and the complete attempt ledger
whether the outcome is PASS, FAIL or INVALID. Missing, late or unverifiable
registration, ledger entry, stdout timestamp or streams makes the result
INVALID / BLOCKED. A further attempt is exploratory and cannot replace this
one; a fresh confirmatory study requires a newly frozen protocol and a new
future beacon. Local code cannot prevent attempts on other hosts, so independent
public-ledger review is part of the acceptance gate.

- **INVALID / BLOCKED:** missing or non-conforming independent freeze/beacon
  evidence, missing attempt ledger/timestamp, repeated or out-of-window attempt;
  fixture collision or invalid triple; any comparator disagreement during
  precheck, warmup or a timed call; missing raw measurements or environment
  evidence. Do not issue a performance PASS/FAIL.
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
- drand's mainnet quicknet `/info` values and 48-byte G1 signatures:
  https://docs.drand.love/blog/2023/10/16/quicknet-is-live/
