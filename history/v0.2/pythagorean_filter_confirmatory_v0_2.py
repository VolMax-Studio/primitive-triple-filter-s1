#!/usr/bin/env python3
"""Candidate confirmatory benchmark. Never run before an independent gate record.

--smoke uses a separate seed, small fixtures, and no confirmatory measurements.
--confirmatory requires a reviewed gate record binding this script and protocol.
"""

import argparse
import gc
import hashlib
import json
import math
import os
import platform
import random
import statistics
import sys
import time
from pathlib import Path

SEED_HEX = "0186c26d4907c55309ecc09c23cfecf8"
PROTOCOL = "PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_2.md"
BITS = 100_000
N_PAIRS = 30
REPEATS = 8
BOOTSTRAP_DRAWS = 10_000
FAMILIES = ("large_reject", "large_accept", "coprime_accept")


def rng_for(seed, label):
    key = hashlib.sha256((seed + "|" + label).encode("ascii")).digest()
    return random.Random(int.from_bytes(key, "big"))


def primitive(bits, rng):
    k = max(4, bits // 2)
    while True:
        u = rng.getrandbits(k - 1) | (1 << (k - 1)) | 1
        v = (rng.getrandbits(k - 1) | (1 << (k - 1))) & ~1
        if u != v and math.gcd(u, v) == 1:
            return u*u - v*v, 2*u*v, u*u + v*v


def product(z, w):
    a, b, m = z
    c, d, n = w
    return a*c - b*d, a*d + b*c, m*n


def make_pair(bits, family, rng):
    if family == "coprime_accept":
        while True:
            left, right = primitive(bits, rng), primitive(bits, rng)
            if math.gcd(left[2], right[2]) == 1:
                return left, right
    if family in ("large_reject", "large_accept"):
        while True:
            shared = primitive(bits // 2, rng)
            left, right = primitive(bits // 2, rng), primitive(bits // 2, rng)
            if (math.gcd(shared[2], left[2]) == 1
                    and math.gcd(shared[2], right[2]) == 1
                    and math.gcd(left[2], right[2]) == 1):
                break
        sign = -1 if family == "large_reject" else 1
        other = (shared[0], sign * shared[1], shared[2])
        return product(shared, left), product(other, right)
    raise ValueError(family)


def direct(pair):
    (a, b, _), (c, d, _) = pair
    x, y = a*c - b*d, a*d + b*c
    good = math.gcd(x, y) == 1
    return good, (x, y) if good else None


def optimized(pair):
    (a, b, m), (c, d, n) = pair
    q = math.gcd(m, n)
    x, y = a*c - b*d, a*d + b*c
    good = q == 1 or math.gcd(x, y) == 1
    return good, (x, y) if good else None


def filtered(pair):
    (a, b, m), (c, d, n) = pair
    q = math.gcd(m, n)
    if q > 1:
        r = ((a % q)*(d % q) + (b % q)*(c % q)) % q
        if math.gcd(r, q) != 1:
            return False, None
    return True, (a*c - b*d, a*d + b*c)


METHODS = {"direct": direct, "optimized": optimized, "filtered": filtered}


def input_digest(pair):
    h = hashlib.sha256()
    for z in pair:
        for value in z:
            magnitude = abs(value).to_bytes((abs(value).bit_length()+7)//8 or 1, "big")
            h.update(b"-" if value < 0 else b"+")
            h.update(len(magnitude).to_bytes(8, "big"))
            h.update(magnitude)
    return h.hexdigest()


def validate(pair, family, bits):
    (a, b, m), (c, d, n) = pair
    assert math.gcd(a, b) == math.gcd(c, d) == 1
    assert a*a + b*b == m*m and c*c + d*d == n*n
    q = math.gcd(m, n)
    if family == "coprime_accept":
        assert q == 1
    else:
        assert q.bit_length() >= bits // 3
    expected = direct(pair)
    assert expected[0] == (family != "large_reject")
    assert optimized(pair) == expected and filtered(pair) == expected
    return expected, q.bit_length()


def measure_pair(pair, expected, order_rng, repeats):
    for fn in METHODS.values():  # untimed warmup, then check every result
        assert fn(pair) == expected
    samples = {name: [] for name in METHODS}
    for _ in range(repeats):
        order = list(METHODS)
        order_rng.shuffle(order)
        for name in order:
            start = time.perf_counter_ns()
            got = METHODS[name](pair)
            duration = time.perf_counter_ns() - start
            if got != expected:
                raise AssertionError("timed call disagrees with oracle")
            samples[name].append(duration)
    med = {key: statistics.median(value) for key, value in samples.items()}
    return samples, med


def bootstrap_interval(ratios, rng, draws):
    # Percentile CI over independent pairs; fixed order-statistic indices.
    n = len(ratios)
    estimates = sorted(statistics.median(ratios[rng.randrange(n)] for _ in range(n))
                       for _ in range(draws))
    return estimates[int(.025*draws)], estimates[int(.975*draws)-1]


def run_family(bits, n_pairs, repeats, family, seed, seen_inputs):
    fixture_rng = rng_for(seed, "fixtures|" + family)
    order_rng = rng_for(seed, "order|" + family)
    boot_rng = rng_for(seed, "bootstrap|" + family)
    pairs = [make_pair(bits, family, fixture_rng) for _ in range(n_pairs)]
    digests = [input_digest(pair) for pair in pairs]
    if len(set(digests)) != n_pairs or any(digest in seen_inputs for digest in digests):
        raise AssertionError("duplicate fixture within or across families")
    seen_inputs.update(digests)
    validated = [(pair, *validate(pair, family, bits)) for pair in pairs]
    gc_state = gc.isenabled()
    gc.disable()
    rows = []
    try:
        for (pair, expected, q_bits), digest in zip(validated, digests):
            samples, med = measure_pair(pair, expected, order_rng, repeats)
            rows.append({
                "input_sha256": digest,
                "q_bits": q_bits,
                "input_coord_bits": max(abs(z).bit_length() for triple in pair for z in triple[:2]),
                "expected_accept": expected[0],
                "prevalidation_comparisons_checked": 2,
                "warmup_calls_checked": len(METHODS),
                "timed_calls_checked": repeats * len(METHODS),
                "samples_ns": samples,
                "pair_median_ns": med,
                "ratio_optimized_over_filtered": med["optimized"]/med["filtered"],
                "ratio_direct_over_filtered": med["direct"]/med["filtered"],
            })
    finally:
        if gc_state:
            gc.enable()
    ratios = [row["ratio_optimized_over_filtered"] for row in rows]
    lo, hi = bootstrap_interval(ratios, boot_rng, BOOTSTRAP_DRAWS)
    return {
        "family": family, "pairs": rows, "n_independent_pairs": n_pairs,
        "median_pair_ratio_optimized_over_filtered": statistics.median(ratios),
        "pair_bootstrap_95pct_percentile_ci": [lo, hi],
        "primary_rule_result": (
            "MEETS_THRESHOLD" if lo > 1 else "DOES_NOT_MEET_THRESHOLD"
        ) if family == "large_reject" else "CONTROL_ONLY",
    }


def validate_gate(record_path):
    if not record_path:
        raise SystemExit("--gate-record is required for --confirmatory")
    record = json.loads(Path(record_path).read_text(encoding="utf-8"))
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    protocol_path = Path(__file__).with_name(PROTOCOL)
    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    required = {
        "status": "APPROVED_FOR_CONFIRMATORY",
        "script_sha256": script_hash,
        "protocol_sha256": protocol_hash,
        "seed_hex": SEED_HEX,
    }
    if any(record.get(key) != value for key, value in required.items()):
        raise SystemExit("gate record does not match script, protocol or seed")
    if not record.get("reviewer") or not record.get("approved_at_utc"):
        raise SystemExit("gate record lacks reviewer or timestamp")
    return script_hash, protocol_hash, record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", action="store_true")
    mode.add_argument("--confirmatory", action="store_true")
    parser.add_argument("--gate-record")
    args = parser.parse_args()
    if args.smoke:
        if args.gate_record:
            parser.error("smoke never consumes a gate record")
        smoke_seed = "smoke-only-separate-stream-v0.2"
        for family in FAMILIES:
            rng = rng_for(smoke_seed, "fixtures|" + family)
            for _ in range(3):
                pair = make_pair(256, family, rng)
                validate(pair, family, 256)
        print("SMOKE PASS: 9 separate-seed fixtures; no confirmatory timings")
        return
    script_hash, protocol_hash, record = validate_gate(args.gate_record)
    seen_inputs = set()
    result = {
        "status": "EXECUTED_NOT_ADJUDICATED",
        "script_sha256": script_hash,
        "protocol_sha256": protocol_hash,
        "gate_record": record,
        "seed_hex": SEED_HEX,
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "bits": BITS,
        "repeats_per_pair": REPEATS,
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "results": [run_family(BITS, N_PAIRS, REPEATS, family, SEED_HEX, seen_inputs)
                    for family in FAMILIES],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
