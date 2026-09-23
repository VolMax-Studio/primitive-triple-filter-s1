#!/usr/bin/env python3
"""Candidate benchmark; requires frozen artifacts and future verified beacon.

--smoke exercises the entire execution and JSON path on a separate seed.
--confirmatory requires an externally reviewed freeze record and beacon data.
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
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROTOCOL = "PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_5.md"
BITS = 100_000
N_PAIRS = 30
REPEATS = 8
BOOTSTRAP_DRAWS = 10_000
FAMILIES = ("large_reject", "large_accept", "coprime_accept")
CHAIN_HASH = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"
CHAIN_PUBLIC_KEY = (
    "83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e76018"
    "3c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63a"
    "af4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a"
)
GENESIS_UNIX = 1692803367
PERIOD_SECONDS = 3
BEACON_DELAY_SECONDS = 600
LAUNCH_DELAY_SECONDS = 300
LAUNCH_END_SECONDS = 7200


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
    if math.gcd(a, b) != 1 or math.gcd(c, d) != 1:
        raise AssertionError("input triple is not primitive")
    if a*a + b*b != m*m or c*c + d*d != n*n:
        raise AssertionError("input does not satisfy Pythagorean identity")
    q = math.gcd(m, n)
    if family == "coprime_accept":
        if q != 1:
            raise AssertionError("q=1 control mismatch")
    else:
        if q.bit_length() < bits // 3:
            raise AssertionError("large-q fixture mismatch")
    expected = direct(pair)
    if expected[0] != (family != "large_reject"):
        raise AssertionError("fixture outcome mismatch")
    if optimized(pair) != expected or filtered(pair) != expected:
        raise AssertionError("comparator prevalidation mismatch")
    return expected, q.bit_length()


def measure_pair(pair, expected, order_rng, repeats):
    gc.enable()
    for fn in METHODS.values():  # untimed warmup, then check every result
        if fn(pair) != expected:
            raise AssertionError("warmup call disagrees with oracle")
    samples = {name: [] for name in METHODS}
    for _ in range(repeats):
        order = list(METHODS)
        order_rng.shuffle(order)
        for name in order:
            gc.disable()
            try:
                start = time.perf_counter_ns()
                got = METHODS[name](pair)
                duration = time.perf_counter_ns() - start
            finally:
                gc.enable()
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
    rows = []
    for (pair, expected, q_bits), digest in zip(validated, digests):
        samples, med = measure_pair(pair, expected, order_rng, repeats)
        rows.append({
            "input_sha256": digest,
            "q_bits": q_bits,
            "input_coord_bits": max(abs(z).bit_length() for triple in pair for z in triple[:2]),
            "expected_accept": expected[0],
            "checks": "oracle equality checked before and after every timed call; abort on mismatch",
            "samples_ns": samples,
            "pair_median_ns": med,
            "ratio_optimized_over_filtered": med["optimized"]/med["filtered"],
            "ratio_direct_over_filtered": med["direct"]/med["filtered"],
        })
    ratios = [row["ratio_direct_over_filtered"] for row in rows]
    lo, hi = bootstrap_interval(ratios, boot_rng, BOOTSTRAP_DRAWS)
    return {
        "family": family, "pairs": rows, "n_independent_pairs": n_pairs,
        "primary_baseline": "direct",
        "median_pair_ratio_direct_over_filtered": statistics.median(ratios),
        "pair_bootstrap_95pct_percentile_ci": [lo, hi],
        "primary_rule_result": (
            "MEETS_THRESHOLD" if lo > 1 else "DOES_NOT_MEET_THRESHOLD"
        ) if family == "large_reject" else "CONTROL_ONLY",
    }


def validate_gate(record_path):
    if not record_path:
        raise SystemExit("--gate-record is required for --confirmatory")
    record = json.loads(Path(record_path).read_text(encoding="utf-8"))
    freeze = record.get("freeze", {})
    beacon = record.get("beacon", {})
    chain_info = record.get("chain_info", {})
    execution = record.get("execution", {})
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    protocol_path = Path(__file__).with_name(PROTOCOL)
    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    required = {
        "status": "APPROVED_FOR_CONFIRMATORY",
        "script_sha256": script_hash,
        "protocol_sha256": protocol_hash,
    }
    if any(freeze.get(key) != value for key, value in required.items()):
        raise SystemExit("freeze record does not bind script and protocol")
    if not all(freeze.get(k) for k in
               ("reviewer", "approved_at_utc", "freeze_publication_evidence_url",
                "planned_attempt_id", "run_window_start_utc", "run_window_end_utc")):
        raise SystemExit("freeze record lacks independent review evidence")
    approved = parse_utc(freeze["approved_at_utc"])
    since_genesis = approved - datetime.fromtimestamp(GENESIS_UNIX, timezone.utc)
    target_microseconds = ((since_genesis.days * 86400 + since_genesis.seconds
                            + BEACON_DELAY_SECONDS) * 1_000_000
                           + since_genesis.microseconds)
    expected_round = target_microseconds // (PERIOD_SECONDS * 1_000_000) + 2
    release_unix = GENESIS_UNIX + (expected_round - 1) * PERIOD_SECONDS
    release = datetime.fromtimestamp(release_unix, timezone.utc)
    window_start = release + timedelta(seconds=LAUNCH_DELAY_SECONDS)
    window_end = release + timedelta(seconds=LAUNCH_END_SECONDS)
    if (parse_utc(freeze["run_window_start_utc"]) != window_start
            or parse_utc(freeze["run_window_end_utc"]) != window_end):
        raise SystemExit("announced run window disagrees with selected round")
    if freeze.get("scheduled_round") != expected_round:
        raise SystemExit("scheduled beacon round does not follow freeze timestamp")
    expected_chain_info = {
        "hash": CHAIN_HASH,
        "public_key": CHAIN_PUBLIC_KEY,
        "genesis_time": GENESIS_UNIX,
        "period": PERIOD_SECONDS,
        "schemeID": "bls-unchained-g1-rfc9380",
        "source_url": f"https://api.drand.sh/{CHAIN_HASH}/info",
    }
    if any(chain_info.get(k) != v for k, v in expected_chain_info.items()):
        raise SystemExit("independent chain-info check disagrees with pinned constants")
    if not chain_info.get("reviewer") or not chain_info.get("evidence_url"):
        raise SystemExit("independent chain-info evidence missing")
    if beacon.get("chain_hash") != CHAIN_HASH or beacon.get("round") != expected_round:
        raise SystemExit("beacon chain or round mismatch")
    source = f"https://api.drand.sh/v2/chains/{CHAIN_HASH}/rounds/{expected_round}"
    if beacon.get("source_url") != source:
        raise SystemExit("beacon source URL mismatch")
    if not all(beacon.get(k) for k in
               ("randomness_hex", "signature_hex", "observed_at_utc",
                "verified_by", "verification_evidence_url")):
        raise SystemExit("beacon evidence incomplete")
    try:
        randomness = bytes.fromhex(beacon["randomness_hex"])
        signature = bytes.fromhex(beacon["signature_hex"])
    except (TypeError, ValueError) as error:
        raise SystemExit("beacon fields are not hex") from error
    if len(randomness) != 32 or len(signature) != 48:
        raise SystemExit("beacon randomness/signature length invalid")
    if hashlib.sha256(signature).digest() != randomness:
        raise SystemExit("beacon signature does not hash to given randomness")
    observed = parse_utc(beacon["observed_at_utc"])
    if observed < release:
        raise SystemExit("beacon observed before scheduled release")
    if datetime.now(timezone.utc) < release:
        raise SystemExit("scheduled future beacon is not available yet")
    if not all(execution.get(k) for k in
               ("idle_operator", "idle_attested_at_utc", "idle_method",
                "attempt_id", "registered_at_utc", "attempt_ledger_evidence_url")):
        raise SystemExit("execution lacks operator idle attestation")
    attested = parse_utc(execution["idle_attested_at_utc"])
    registered = parse_utc(execution["registered_at_utc"])
    now = datetime.now(timezone.utc)
    if (attested < observed or attested > registered
            or now - attested > timedelta(hours=2)):
        raise SystemExit("idle attestation must follow beacon and be within 2 hours")
    if execution["attempt_id"] != freeze["planned_attempt_id"]:
        raise SystemExit("registered attempt ID does not match freeze")
    if not (window_start <= registered <= now <= window_end):
        raise SystemExit("registration and launch must be in announced window")
    seed_material = (b"pythagorean-filter-v0.5\x00" + bytes.fromhex(script_hash)
                     + bytes.fromhex(protocol_hash) + bytes.fromhex(CHAIN_HASH)
                     + expected_round.to_bytes(8, "big") + randomness)
    return script_hash, protocol_hash, hashlib.sha256(seed_material).hexdigest(), record


def parse_utc(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as error:
        raise SystemExit("invalid UTC timestamp") from error
    if dt.tzinfo is None or dt.utcoffset().total_seconds() != 0:
        raise SystemExit("timestamp must specify UTC")
    return dt


def environment_snapshot():
    model = None
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.lower().startswith("model name"):
                model = line.partition(":")[2].strip()
                break
    except OSError:
        pass
    paths = {
        "cpu0_governor": "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor",
        "intel_pstate_no_turbo": "/sys/devices/system/cpu/intel_pstate/no_turbo",
        "cpufreq_boost": "/sys/devices/system/cpu/cpufreq/boost",
    }
    status = {}
    for label, path in paths.items():
        try:
            status[label] = Path(path).read_text().strip()
        except OSError:
            status[label] = None
    governors = {}
    for path in Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/scaling_governor"):
        try:
            governors[path.parent.parent.name] = path.read_text().strip()
        except OSError:
            governors[path.parent.parent.name] = None
    status["governors_by_cpu"] = dict(sorted(governors.items()))
    return {
        "cpu_model": model or platform.processor(),
        "cpu_count": os.cpu_count(),
        "cpu_affinity_count": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "load_average_1_5_15": os.getloadavg() if hasattr(os, "getloadavg") else None,
        "frequency_controls": status,
    }


def main():
    started_at_utc = datetime.now(timezone.utc).isoformat()
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", action="store_true")
    mode.add_argument("--confirmatory", action="store_true")
    parser.add_argument("--gate-record")
    args = parser.parse_args()
    if args.smoke:
        if args.gate_record:
            parser.error("smoke never consumes a gate record")
        smoke_seed = "smoke-only-separate-stream-v0.5"
        seen = set()
        result = [run_family(256, 3, 2, family, smoke_seed, seen) for family in FAMILIES]
        json.loads(json.dumps(result))
        print("SMOKE PASS: end-to-end 9 separate-seed fixtures, timings, bootstrap, JSON; discarded")
        return
    script_hash, protocol_hash, seed_hex, record = validate_gate(args.gate_record)
    seen_inputs = set()
    environment_before = environment_snapshot()
    results = [run_family(BITS, N_PAIRS, REPEATS, family, seed_hex, seen_inputs)
               for family in FAMILIES]
    result = {
        "status": "EXECUTED_NOT_ADJUDICATED",
        "script_sha256": script_hash,
        "protocol_sha256": protocol_hash,
        "gate_record": record,
        "started_at_utc": started_at_utc,
        "derived_seed_hex": seed_hex,
        "python": sys.version,
        "platform": platform.platform(),
        "environment_before": environment_before,
        "environment_after": environment_snapshot(),
        "bits": BITS,
        "repeats_per_pair": REPEATS,
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "results": results,
    }
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
