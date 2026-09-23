#!/usr/bin/env python3
"""Deterministic gate-only checks with a fake beacon. Never runs benchmark fixtures."""

import copy
import hashlib
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pythagorean_filter_confirmatory_v0_5 as benchmark


FIXED_NOW = datetime(2026, 9, 23, 0, 3, tzinfo=timezone.utc)


class FixedClock(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED_NOW if tz is not None else FIXED_NOW.replace(tzinfo=None)


def iso(instant):
    return instant.isoformat()


def synthetic_record():
    approved = FIXED_NOW - timedelta(seconds=1000)
    genesis = datetime.fromtimestamp(benchmark.GENESIS_UNIX, timezone.utc)
    offset = approved - genesis
    target_microseconds = ((offset.days * 86400 + offset.seconds
                            + benchmark.BEACON_DELAY_SECONDS) * 1_000_000
                           + offset.microseconds)
    round_no = target_microseconds // (benchmark.PERIOD_SECONDS * 1_000_000) + 2
    release = datetime.fromtimestamp(
        benchmark.GENESIS_UNIX + (round_no - 1) * benchmark.PERIOD_SECONDS,
        timezone.utc,
    )
    signature = bytes(range(48))  # Fake, not BLS-verified; no beacon was used.
    script_hash = hashlib.sha256(Path(benchmark.__file__).read_bytes()).hexdigest()
    protocol_hash = hashlib.sha256(
        Path(benchmark.__file__).with_name(benchmark.PROTOCOL).read_bytes()
    ).hexdigest()
    return {
        "freeze": {
            "status": "APPROVED_FOR_CONFIRMATORY",  # Synthetic marker, never published.
            "script_sha256": script_hash,
            "protocol_sha256": protocol_hash,
            "reviewer": "synthetic-test-only",
            "approved_at_utc": iso(approved),
            "freeze_publication_evidence_url": "synthetic://freeze",
            "planned_attempt_id": "synthetic-test-only",
            "run_window_start_utc": iso(release + timedelta(seconds=300)),
            "run_window_end_utc": iso(release + timedelta(seconds=7200)),
            "scheduled_round": round_no,
        },
        "chain_info": {
            "hash": benchmark.CHAIN_HASH,
            "public_key": benchmark.CHAIN_PUBLIC_KEY,
            "genesis_time": benchmark.GENESIS_UNIX,
            "period": benchmark.PERIOD_SECONDS,
            "schemeID": "bls-unchained-g1-rfc9380",
            "source_url": f"https://api.drand.sh/{benchmark.CHAIN_HASH}/info",
            "reviewer": "synthetic-test-only",
            "evidence_url": "synthetic://chain-info",
        },
        "beacon": {
            "chain_hash": benchmark.CHAIN_HASH,
            "round": round_no,
            "source_url": (
                f"https://api.drand.sh/v2/chains/{benchmark.CHAIN_HASH}/rounds/{round_no}"
            ),
            "signature_hex": signature.hex(),
            "randomness_hex": hashlib.sha256(signature).hexdigest(),
            "observed_at_utc": iso(release + timedelta(seconds=3)),
            "verified_by": "synthetic-test-only",
            "verification_evidence_url": "synthetic://beacon",
        },
        "execution": {
            "idle_operator": "synthetic-test-only",
            "idle_attested_at_utc": iso(FIXED_NOW - timedelta(seconds=240)),
            "idle_method": "synthetic",
            "attempt_id": "synthetic-test-only",
            "registered_at_utc": iso(FIXED_NOW - timedelta(seconds=10)),
            "attempt_ledger_evidence_url": "synthetic://attempt",
        },
    }


def verify_record(record, expected_error=None):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "fake-gate.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        try:
            benchmark.validate_gate(str(path))
        except SystemExit as error:
            if expected_error is None or str(error) != expected_error:
                raise AssertionError(
                    f"expected {expected_error!r}, got {str(error)!r}"
                ) from error
        else:
            if expected_error is not None:
                raise AssertionError(
                    f"invalid synthetic record was accepted (expected {expected_error!r})"
                )


def verify_known_answer_and_boundaries():
    """Literal published quicknet schedule; only the test clock is synthetic."""
    global FIXED_NOW
    original_now = FIXED_NOW
    try:
        assert benchmark.GENESIS_UNIX == 1692803367
        assert benchmark.PERIOD_SECONDS == 3
        assert benchmark.BEACON_DELAY_SECONDS == 600
        assert benchmark.LAUNCH_DELAY_SECONDS == 300
        assert benchmark.LAUNCH_END_SECONDS == 7200

        # approved + 600 s is exactly release(999): the chosen round must
        # therefore be 1000, the first round STRICTLY after that instant.
        record = synthetic_record()
        record["freeze"].update({
            "approved_at_utc": "2023-08-23T15:49:21Z",
            "scheduled_round": 1000,
            "run_window_start_utc": "2023-08-23T16:04:24Z",
            "run_window_end_utc": "2023-08-23T17:59:24Z",
        })
        record["beacon"].update({
            "round": 1000,
            "source_url": (
                f"https://api.drand.sh/v2/chains/{benchmark.CHAIN_HASH}/rounds/1000"
            ),
            "observed_at_utc": "2023-08-23T15:59:27Z",
        })
        record["execution"]["idle_attested_at_utc"] = "2023-08-23T15:59:34Z"

        # Each registration coincides with the simulated launch. Attestation
        # precedes every launch, and even at +7201 s it is less than 2 h old.
        for clock, expected_error in (
            ("2023-08-23T16:04:23Z", "registration and launch must be in announced window"),
            ("2023-08-23T16:04:24Z", None),
            ("2023-08-23T17:59:24Z", None),
            ("2023-08-23T17:59:25Z", "registration and launch must be in announced window"),
        ):
            FIXED_NOW = datetime.fromisoformat(clock.replace("Z", "+00:00"))
            boundary_record = copy.deepcopy(record)
            boundary_record["execution"]["registered_at_utc"] = clock
            verify_record(boundary_record, expected_error)
    finally:
        FIXED_NOW = original_now


def main():
    original_clock = benchmark.datetime
    benchmark.datetime = FixedClock
    try:
        clean = synthetic_record()
        # 23:59 idle attestation, 00:03 execution: crossing midnight is valid.
        assert clean["execution"]["idle_attested_at_utc"][:10] != iso(FIXED_NOW)[:10]
        verify_record(clean)

        def reject(edit, expected_error):
            modified = copy.deepcopy(clean)
            edit(modified)
            verify_record(modified, expected_error)

        bad_chain = "independent chain-info check disagrees with pinned constants"
        reject(lambda r: r["chain_info"].__setitem__("genesis_time", 1689232296),
               bad_chain)
        reject(lambda r: r["chain_info"].__setitem__("public_key", "00" * 96),
               bad_chain)
        def short_signature(r):
            signature = bytes(range(47))
            r["beacon"]["signature_hex"] = signature.hex()
            r["beacon"]["randomness_hex"] = hashlib.sha256(signature).hexdigest()
        reject(short_signature, "beacon randomness/signature length invalid")
        reject(lambda r: r["execution"].__setitem__("attempt_id", "wrong-id"),
               "registered attempt ID does not match freeze")
        release = datetime.fromtimestamp(
            benchmark.GENESIS_UNIX + (clean["freeze"]["scheduled_round"] - 1) * 3,
            timezone.utc,
        )
        def register_before_window(r):
            # Preserve the correct attestation order so only the window fails.
            r["execution"]["idle_attested_at_utc"] = iso(release + timedelta(seconds=50))
            r["execution"]["registered_at_utc"] = iso(release + timedelta(seconds=100))
        reject(register_before_window, "registration and launch must be in announced window")
        def attest_after_registration(r):
            # Both timestamps remain inside the launch window; only order fails.
            r["execution"]["registered_at_utc"] = iso(release + timedelta(seconds=330))
            r["execution"]["idle_attested_at_utc"] = iso(release + timedelta(seconds=360))
        reject(attest_after_registration,
               "idle attestation must follow beacon and be within 2 hours")
        reject(lambda r: r["execution"].__setitem__(
            "idle_attested_at_utc", iso(FIXED_NOW - timedelta(hours=3))
        ), "idle attestation must follow beacon and be within 2 hours")
        verify_known_answer_and_boundaries()
        print("SYNTHETIC GATE PASS: seven expected rejection reasons; "
              "literal quicknet round 1000 and four launch boundaries")
    finally:
        benchmark.datetime = original_clock


if __name__ == "__main__":
    main()
