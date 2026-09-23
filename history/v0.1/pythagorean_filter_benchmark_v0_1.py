#!/usr/bin/env python3
"""Reproducible, constructed-family benchmark for primitive-triple pruning.

This measures an integer-arithmetic implementation, not a Lean proof or an
asymptotic complexity bound. Run with Python 3.10+ and no dependencies.
"""

import gc
import hashlib
import json
import platform
import random
import statistics
import sys
import time
from math import gcd
from pathlib import Path


SEED = 20260922
FAMILIES = (
    "coprime_accept",
    "small_accept",
    "small_reject",
    "large_accept",
    "large_reject",
)


def primitive(bits, rng):
    k = max(3, bits // 2)
    while True:
        u = rng.getrandbits(k) | 1
        v = rng.getrandbits(k) & ~1
        if v and u != v and gcd(u, v) == 1:
            return u * u - v * v, 2 * u * v, u * u + v * v


def multiply(z, w):
    a, b, m = z
    c, d, n = w
    return a * c - b * d, a * d + b * c, m * n


def make_pair(bits, family, rng):
    if family == "coprime_accept":
        while True:
            left, right = primitive(bits, rng), primitive(bits, rng)
            if gcd(left[2], right[2]) == 1:
                return left, right
    if family.startswith("small_"):
        while True:
            left, right = primitive(bits, rng), primitive(bits, rng)
            if gcd(left[2], right[2]) == 1 and left[2] % 5 and right[2] % 5:
                break
        sign = -1 if family.endswith("reject") else 1
        return multiply(left, (3, 4, 5)), multiply(right, (3, 4 * sign, 5))
    if family.startswith("large_"):
        while True:
            shared = primitive(bits // 2, rng)
            left, right = primitive(bits // 2, rng), primitive(bits // 2, rng)
            if (gcd(shared[2], left[2]) == 1
                    and gcd(shared[2], right[2]) == 1
                    and gcd(left[2], right[2]) == 1):
                break
        sign = -1 if family.endswith("reject") else 1
        conjugated = (shared[0], sign * shared[1], shared[2])
        return multiply(shared, left), multiply(conjugated, right)
    raise ValueError(family)


def direct(pair):
    (a, b, _), (c, d, _) = pair
    x, y = a * c - b * d, a * d + b * c
    return (True, (x, y)) if gcd(x, y) == 1 else (False, None)


def filtered(pair):
    (a, b, m), (c, d, n) = pair
    q = gcd(m, n)
    if q > 1:
        r = ((a % q) * (d % q) + (b % q) * (c % q)) % q
        if gcd(r, q) != 1:
            return False, None
    return True, (a * c - b * d, a * d + b * c)


def timed_batch(fn, pairs):
    start = time.perf_counter_ns()
    for pair in pairs:
        fn(pair)
    return (time.perf_counter_ns() - start) / len(pairs) / 1000


def main():
    bits_list = (1024, 8192) if "--quick" in sys.argv else (1024, 8192, 65536, 100000)
    results = []
    rng = random.Random(SEED)
    for bits in bits_list:
        count = 12 if bits <= 1024 else 6 if bits <= 8192 else 3 if bits <= 65536 else 2
        repeats = 7 if bits <= 8192 else 5
        for family in FAMILIES:
            pairs = [make_pair(bits, family, rng) for _ in range(count)]
            expected = family.endswith("accept")
            for pair in pairs:
                (a, b, m), (c, d, n) = pair
                if not (gcd(a, b) == gcd(c, d) == 1
                        and a*a + b*b == m*m and c*c + d*d == n*n):
                    raise AssertionError("invalid input triple")
                q = gcd(m, n)
                if (family.startswith("small_") and q != 5
                        or family.startswith("large_") and q.bit_length() < bits // 3
                        or family == "coprime_accept" and q != 1):
                    raise AssertionError("wrong shared-hypotenuse family")
                if direct(pair) != filtered(pair) or direct(pair)[0] != expected:
                    raise AssertionError("decision or output mismatch")
            direct(pairs[0]); filtered(pairs[0])  # warmup; excluded
            samples = {"direct": [], "filtered": []}
            gc_enabled = gc.isenabled()
            gc.disable()
            try:
                for rep in range(repeats):
                    order = ("direct", "filtered") if rep % 2 == 0 else ("filtered", "direct")
                    for name in order:
                        fn = direct if name == "direct" else filtered
                        samples[name].append(timed_batch(fn, pairs))
            finally:
                if gc_enabled:
                    gc.enable()
            dmed = statistics.median(samples["direct"])
            fmed = statistics.median(samples["filtered"])
            results.append({
                "nominal_input_bits": bits,
                "family": family,
                "pairs": count,
                "repeats": repeats,
                "median_input_coord_bits": statistics.median(
                    max(abs(p[0][0]).bit_length(), abs(p[0][1]).bit_length(),
                        abs(p[1][0]).bit_length(), abs(p[1][1]).bit_length()) for p in pairs),
                "median_q_bits": statistics.median(gcd(p[0][2], p[1][2]).bit_length() for p in pairs),
                "direct_us": samples["direct"],
                "filtered_us": samples["filtered"],
                "median_direct_us": dmed,
                "median_filtered_us": fmed,
                "direct_over_filtered": dmed / fmed,
                "correctness_mismatches": 0,
            })
    output = {
        "seed": SEED,
        "python": sys.version,
        "platform": platform.platform(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "clock": "perf_counter_ns; microseconds per pair; paired alternating order",
        "results": results,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
