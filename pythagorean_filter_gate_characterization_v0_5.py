#!/usr/bin/env python3
"""Characterize all 18 explicit validate_gate guards with synthetic data.

No network, genuine beacon, fixture generation, or confirmatory run is used.
Each mutation runs on a temporary copy of the benchmark and its specification.
"""

import ast
import copy
import hashlib
import importlib.util
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pythagorean_filter_confirmatory_v0_5 as original
import pythagorean_filter_synthetic_gate_test_v0_5 as fixtures

SOURCE = Path(original.__file__).read_text(encoding="utf-8")
FIXED_NOW = fixtures.FIXED_NOW
ISO = fixtures.iso
IDLE_MESSAGE = "idle attestation must follow beacon and be within 2 hours"


def set_field(section, key, value):
    def edit(record):
        record[section][key] = value
    return edit


def release_of(record):
    seconds = (original.GENESIS_UNIX
               + (record["freeze"]["scheduled_round"] - 1) * original.PERIOD_SECONDS)
    return datetime.fromtimestamp(seconds, timezone.utc)


def short_signature(record):
    signature = bytes(range(47))
    record["beacon"]["signature_hex"] = signature.hex()
    record["beacon"]["randomness_hex"] = hashlib.sha256(signature).hexdigest()


def announced_window_shift(record):
    start = datetime.fromisoformat(record["freeze"]["run_window_start_utc"])
    record["freeze"]["run_window_start_utc"] = ISO(start + timedelta(seconds=1))


def before_release(record):
    record["beacon"]["observed_at_utc"] = ISO(release_of(record) - timedelta(seconds=1))


def future_release(record):
    approved = FIXED_NOW - timedelta(seconds=300)
    delta = approved - datetime.fromtimestamp(original.GENESIS_UNIX, timezone.utc)
    micros = ((delta.days * 86400 + delta.seconds + original.BEACON_DELAY_SECONDS)
              * 1_000_000 + delta.microseconds)
    round_no = micros // (original.PERIOD_SECONDS * 1_000_000) + 2
    release = datetime.fromtimestamp(
        original.GENESIS_UNIX + (round_no - 1) * original.PERIOD_SECONDS,
        timezone.utc,
    )
    record["freeze"].update({
        "approved_at_utc": ISO(approved),
        "scheduled_round": round_no,
        "run_window_start_utc": ISO(release + timedelta(seconds=300)),
        "run_window_end_utc": ISO(release + timedelta(seconds=7200)),
    })
    record["beacon"].update({
        "round": round_no,
        "source_url": (
            f"https://api.drand.sh/v2/chains/{original.CHAIN_HASH}/rounds/{round_no}"
        ),
        "observed_at_utc": ISO(release + timedelta(seconds=3)),
    })
    record["execution"].update({
        "idle_attested_at_utc": ISO(release + timedelta(seconds=10)),
        "registered_at_utc": ISO(release + timedelta(seconds=330)),
    })


def attest_before_observation(record):
    record["execution"]["idle_attested_at_utc"] = ISO(
        release_of(record) + timedelta(seconds=1)
    )


def attest_after_registration(record):
    release = release_of(record)
    record["execution"]["registered_at_utc"] = ISO(release + timedelta(seconds=330))
    record["execution"]["idle_attested_at_utc"] = ISO(release + timedelta(seconds=360))


def register_before_window(record):
    release = release_of(record)
    record["execution"]["idle_attested_at_utc"] = ISO(release + timedelta(seconds=50))
    record["execution"]["registered_at_utc"] = ISO(release + timedelta(seconds=100))


# number, label, edit (None means no gate-record path), required exact error.
CASES = [
    (1, "no_record", None, "--gate-record is required for --confirmatory"),
    (2, "freeze_binding", set_field("freeze", "status", "NO"),
     "freeze record does not bind script and protocol"),
    (3, "freeze_evidence", set_field("freeze", "reviewer", ""),
     "freeze record lacks independent review evidence"),
    (4, "announced_window", announced_window_shift,
     "announced run window disagrees with selected round"),
    (5, "scheduled_round", set_field("freeze", "scheduled_round", -1),
     "scheduled beacon round does not follow freeze timestamp"),
    (6, "chain_constants", set_field("chain_info", "public_key", "00" * 96),
     "independent chain-info check disagrees with pinned constants"),
    (7, "chain_evidence", set_field("chain_info", "evidence_url", ""),
     "independent chain-info evidence missing"),
    (8, "beacon_chain_round", set_field("beacon", "chain_hash", "wrong"),
     "beacon chain or round mismatch"),
    (9, "beacon_url", set_field("beacon", "source_url", "wrong"),
     "beacon source URL mismatch"),
    (10, "beacon_evidence", set_field("beacon", "verified_by", ""),
     "beacon evidence incomplete"),
    (11, "signature_length", short_signature,
     "beacon randomness/signature length invalid"),
    (12, "beacon_hash", set_field("beacon", "randomness_hex", "00" * 32),
     "beacon signature does not hash to given randomness"),
    (13, "observed_before_release", before_release,
     "beacon observed before scheduled release"),
    (14, "future_beacon", future_release,
     "scheduled future beacon is not available yet"),
    (15, "execution_evidence", set_field("execution", "idle_operator", ""),
     "execution lacks operator idle attestation"),
    (16, "attested_before_observed", attest_before_observation, IDLE_MESSAGE),
    (16, "attested_after_registered", attest_after_registration, IDLE_MESSAGE),
    (17, "attempt_id", set_field("execution", "attempt_id", "wrong"),
     "registered attempt ID does not match freeze"),
    (18, "execution_window", register_before_window,
     "registration and launch must be in announced window"),
]


def observed_result(module, edit):
    saved_clock, saved_module = module.datetime, fixtures.benchmark
    module.datetime = fixtures.FixedClock
    fixtures.benchmark = module
    try:
        if edit is None:
            try:
                module.validate_gate(None)
            except SystemExit as error:
                return str(error)
            except Exception as error:
                return type(error).__name__
            return None
        record = copy.deepcopy(fixtures.synthetic_record())
        edit(record)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            try:
                module.validate_gate(str(path))
            except SystemExit as error:
                return str(error)
            except Exception as error:
                return type(error).__name__
            return None
    finally:
        module.datetime = saved_clock
        fixtures.benchmark = saved_module


def load_mutant(mutated_source, directory):
    path = Path(directory) / "pythagorean_filter_confirmatory_v0_5.py"
    path.write_text(mutated_source, encoding="utf-8")
    protocol = Path(original.__file__).with_name(original.PROTOCOL)
    (Path(directory) / original.PROTOCOL).write_bytes(protocol.read_bytes())
    spec = importlib.util.spec_from_file_location("temporary_gate_mutant", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def explicit_guards():
    tree = ast.parse(SOURCE)
    gate = next(node for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == "validate_gate")
    guards = sorted((node for node in ast.walk(gate) if isinstance(node, ast.If)),
                    key=lambda node: node.lineno)
    if len(guards) != 18:
        raise AssertionError(f"expected 18 explicit guards, found {len(guards)}")
    return guards


def remove_guard_condition(node):
    # Byte offsets are safe here: the target tests are all ASCII.
    lines = SOURCE.splitlines(keepends=True)
    start = sum(len(line) for line in lines[:node.test.lineno - 1]) + node.test.col_offset
    end = sum(len(line) for line in lines[:node.test.end_lineno - 1]) + node.test.end_col_offset
    return SOURCE[:start] + "False" + SOURCE[end:]


def run():
    for _, label, edit, expected in CASES:
        actual = observed_result(original, edit)
        if actual != expected:
            raise AssertionError(f"original {label}: expected {expected!r}, got {actual!r}")
    if observed_result(original, lambda record: None) is not None:
        raise AssertionError("original rejected valid synthetic gate")
    rows = []
    for number, node in enumerate(explicit_guards(), start=1):
        source = remove_guard_condition(node)
        with tempfile.TemporaryDirectory() as directory:
            mutant = load_mutant(source, directory)
            kills = [label for _, label, edit, expected in CASES
                     if observed_result(mutant, edit) != expected]
            rows.append({"guard": number, "line": node.lineno,
                         "condition": ast.get_source_segment(SOURCE, node.test),
                         "status": "KILLED" if kills else "SURVIVED",
                         "killed_by": kills})
    subconditions = [
        ("attested_before_observed", "attested < observed", "False"),
        ("attested_after_registered", "attested > registered", "False"),
        ("idle_age_2h", "now - attested > timedelta(hours=2)", "False"),
    ]
    subrows = []
    for label, needle, replacement in subconditions:
        if SOURCE.count(needle) != 1:
            raise AssertionError(f"mutation target {label} ambiguous")
        with tempfile.TemporaryDirectory() as directory:
            mutant = load_mutant(SOURCE.replace(needle, replacement, 1), directory)
            kills = [case_label for _, case_label, edit, expected in CASES
                     if observed_result(mutant, edit) != expected]
            subrows.append({"condition": label, "status": "KILLED" if kills else "SURVIVED",
                            "killed_by": kills})
    print(json.dumps({
        "scope": "synthetic validate_gate; no real beacon or benchmark run",
        "benchmark_sha256": hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest(),
        "spec_sha256": hashlib.sha256(
            Path(original.__file__).with_name(original.PROTOCOL).read_bytes()
        ).hexdigest(),
        "cases": len(CASES), "guards": rows, "subconditions": subrows,
    }, indent=2))


if __name__ == "__main__":
    run()
