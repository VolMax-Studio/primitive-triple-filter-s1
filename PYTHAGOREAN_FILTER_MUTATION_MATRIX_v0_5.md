# Primitive-triple filter — final systematic gate mutation matrix (v0.5, PRE-GATE)

Scope: 18 explicit `if` guards in `validate_gate` and three idle subconditions.
All inputs use a deterministic **fake** beacon; the runner only calls `validate_gate`.
It never executes `run_family`, `--confirmatory`, a real beacon lookup or a BLS verification.

## Pinned bytes and method

- Benchmark SHA-256: `ca9a06a9a3b3d3b85c8ae571204489fbf6bbf59c20f1a54a8a817a4428383215`
- Specification SHA-256: `a89ca119b74d67744532489c9930cc4be2e42d8a2fefc86f9364463bf957a7ec`
- Characterization runner SHA-256: `63984aec1e8d8849d4ce27599e7f63ecbb1c5b4c71f6ebe8daa2bc98e6b5fad9`
- Raw observations JSON SHA-256: `7e12fc50d82254c0b7b1884f8e11d3e722bdbba07dd17cef754b81c3d0cabba1`
- The runner creates an isolated temporary module per mutation and reconstructs
  the synthetic record against **that module's script hash**. It compares exact
  rejection messages, not merely the presence of `SystemExit`.
- `KILLED` means a mutation changed a registered diagnostic outcome. It does
  not automatically mean that the mutation would accept an invalid real run.

## Every explicit guard

| # | Check | Result | Isolated witness |
|---:|---|---|---|
| 1 | Zapis gate nedostaje | KILLED | `no_record` |
| 2 | Status i SHA freeze vezivanja | KILLED | `freeze_binding` |
| 3 | Freeze dokaz i identitet | KILLED | `freeze_evidence` |
| 4 | Najavljeni prozor | KILLED | `announced_window` |
| 5 | Zakazani krug | KILLED | `scheduled_round` |
| 6 | Konstante lanca | KILLED | `chain_constants` |
| 7 | Dokaz /info | KILLED | `chain_evidence` |
| 8 | Lanac i krug beacona | KILLED | `beacon_chain_round` |
| 9 | URL kruga | KILLED | `beacon_url` |
| 10 | Dokaz beacona | KILLED | `beacon_evidence` |
| 11 | Dužine potpisa/nasumičnosti | KILLED | `signature_length` |
| 12 | SHA-256 potpisa | KILLED | `beacon_hash` |
| 13 | Opservacija pre objave | KILLED | `observed_before_release` |
| 14 | Budući beacon | KILLED | `future_beacon` |
| 15 | Dokaz o izvršenju | KILLED | `execution_evidence` |
| 16 | Idle uslovi zajedno | KILLED | `attested_before_observed, attested_after_registered` |
| 17 | ID pokušaja | KILLED | `attempt_id` |
| 18 | Prozor izvršenja | KILLED | `execution_window` |

Branch-level totals: **18 KILLED; 0 SURVIVED–test gap; 0 SURVIVED–covered elsewhere.**
Guard #1 is killed by loss of its exact error (the mutant raises `TypeError`);
guard #14 by loss of its early, specific rejection (the later window guard
would still reject). These results characterize observable gate behavior.

## Idle subconditions and equivalence

| Condition | Result | Witness or reason |
|---|---|---|
| `attested < observed` | KILLED | `attested_before_observed`: attestation at release +1 s, observation at release +3 s. |
| `attested > registered` | KILLED | `attested_after_registered`: registration at release +330 s, attestation at +360 s. |
| `now - attested > 2 h` | EQUIVALENT/REDUNDANT | SURVIVED independently; implied by the other guards. |

Proof of the last row for otherwise accepted records: `attested ≥ observed ≥ release`
and `now ≤ window_end = release + 7200 s`. Therefore
`now − attested ≤ 7200 s`. Removing only the 2 h predicate cannot admit
a record that all the remaining checks would reject. The predicate remains
in the benchmark as defense in depth. The **future-beacon** guard is likewise
redundant for final acceptance when the launch-window guard succeeds
(`now ≥ release + 300 s`), although its diagnostic reason is independently tested.

## Boundary of this result

- The 18-guard matrix does not assess BLS validity, public timestamps, honest
  reviewer identity, idle conditions in reality, or whether attempts were
  privately run or selectively abandoned. Those are external freeze/execution gates.
- `parse_utc` and the hex-decoding exception handler are helper/error paths
  outside the 18 explicit `if` guards enumerated here. No claim of exhaustive
  Python control-flow coverage is made.
- The freeze record should identify this exact matrix and explicitly record
  the redundant 2 h predicate. Nothing here ratifies a freeze or starts a
  confirmatory run.
