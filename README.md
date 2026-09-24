# primitive-triple-filter-s1

**Status: PRE-GATE / NOT FROZEN / NO CONFIRMATORY RUN**

This repository contains the candidate specification, benchmark implementation, synthetic gate fixtures, mutation characterization, and historical candidate artifacts for the **Primitive-Triple Modular Filter** investigation (`primitive-triple-filter-s1`).

---

## 1. Scientific & Governance Boundary

- **No confirmatory run has been performed** (`confirmatory_run_performed: false`).
- **No signed freeze tag or freeze record exists** in this repository.
- v0.1 remains an exploratory pilot; v0.2, v0.3, and v0.4 failed independent review prior to freeze.
- Candidate v0.5 is a pre-gate candidate snapshot prepared for independent gate review.
- Prior local commit `8dd3b5b` was an exploratory preparation snapshot, not an obligatory base for remote history.
- The 18/18 result in gate characterization denotes that **all 18 explicit `if` guards in `validate_gate` are killed by exact diagnostic rejection messages**, and does **not** assert "100% coverage" of the entire program. Helper routines (such as `parse_utc` and hex error handling) and broader Python control flow remain outside this 18-guard boundary, as documented in `PYTHAGOREAN_FILTER_MUTATION_MATRIX_v0_5.md`.

---

## 2. Repository Structure

```text
primitive-triple-filter-s1/
├── README.md                                          # This repository record
├── .gitignore
├── PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_5.md       # Candidate confirmatory specification (v0.5)
├── pythagorean_filter_confirmatory_v0_5.py            # Benchmark & verification harness (v0.5)
├── pythagorean_filter_synthetic_gate_test_v0_5.py     # Deterministic synthetic gate fixtures (v0.5)
├── pythagorean_filter_gate_characterization_v0_5.py   # Mutation runner for 18 explicit gate guards (v0.5)
├── PYTHAGOREAN_FILTER_MUTATION_OBSERVATIONS_v0_5.json # Raw mutation observations (v0.5)
├── PYTHAGOREAN_FILTER_MUTATION_MATRIX_v0_5.md         # Diagnostic kill matrix & equivalence proofs (v0.5)
├── PYTHAGOREAN_FILTER_PRE_GATE_MANIFEST_v0_5.json     # Reviewed candidate manifest and prior artifact hashes
└── history/                                           # Earlier unratified candidate versions (provenance)
    ├── v0.1/
    │   ├── PYTHAGOREAN_FILTER_EXPERIMENT_v0_1.md
    │   ├── pythagorean_filter_benchmark_v0_1.py
    │   └── pythagorean_filter_results_v0_1.json
    ├── v0.2/
    │   ├── PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_2.md
    │   ├── pythagorean_filter_confirmatory_v0_2.py
    │   └── PYTHAGOREAN_FILTER_PRE_GATE_MANIFEST_v0_2.json
    ├── v0.3/
    │   ├── PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_3.md
    │   ├── pythagorean_filter_confirmatory_v0_3.py
    │   └── PYTHAGOREAN_FILTER_PRE_GATE_MANIFEST_v0_3.json
    └── v0.4/
        ├── PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_4.md
        ├── pythagorean_filter_confirmatory_v0_4.py
        └── PYTHAGOREAN_FILTER_PRE_GATE_MANIFEST_v0_4.json
```

---

## 3. Pinned SHA-256 Identifiers

All candidate and historical artifact digests are pinned in [PYTHAGOREAN_FILTER_PRE_GATE_MANIFEST_v0_5.json](PYTHAGOREAN_FILTER_PRE_GATE_MANIFEST_v0_5.json):

### Candidate v0.5
| File | SHA-256 |
|---|---|
| `PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_5.md` | `a89ca119b74d67744532489c9930cc4be2e42d8a2fefc86f9364463bf957a7ec` |
| `pythagorean_filter_confirmatory_v0_5.py` | `ca9a06a9a3b3d3b85c8ae571204489fbf6bbf59c20f1a54a8a817a4428383215` |
| `pythagorean_filter_synthetic_gate_test_v0_5.py` | `8f8dae40905c06590d1435eedcd7536b6ad0d17213100d1c65f5bf59392bd401` |
| `pythagorean_filter_gate_characterization_v0_5.py` | `63984aec1e8d8849d4ce27599e7f63ecbb1c5b4c71f6ebe8daa2bc98e6b5fad9` |
| `PYTHAGOREAN_FILTER_MUTATION_OBSERVATIONS_v0_5.json` | `7e12fc50d82254c0b7b1884f8e11d3e722bdbba07dd17cef754b81c3d0cabba1` |
| `PYTHAGOREAN_FILTER_MUTATION_MATRIX_v0_5.md` | `be36c18c0b1a806e60b38048eb32e70d63c5233a346d63d61b3f90f7fcb3b371` |

### Prior Unratified Candidates (`history/`)
- **v0.1**:
  - `PYTHAGOREAN_FILTER_EXPERIMENT_v0_1.md`: `f84bbcb1758e30fe0020aac05bf3ba52c08e5f436bd903df42645a8475d03b38`
  - `pythagorean_filter_benchmark_v0_1.py`: `a4eb615b33f77950aae4904df1f3c3865e37e28a85a6abe75dd4528eb7042182`
  - `pythagorean_filter_results_v0_1.json`: `305803ed09e66be3f6eaf201aac5ad859801a95e5253a58c1bf737c04a3c4ae4`
- **v0.2**:
  - `PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_2.md`: `bfd2d869b48bbae4265d4f0abc822727369ef881a4f670a9ecadc3b0d12fd05f`
  - `pythagorean_filter_confirmatory_v0_2.py`: `a5c29113873fe748af553ba503937916f04dc8cc6f03b7ba72703401cab80c31`
  - `PYTHAGOREAN_FILTER_PRE_GATE_MANIFEST_v0_2.json`: `f424af36fd5f54f745b9d84cbc17d44b5f257a1068a9cf0a05286d39bda8caf6`
- **v0.3**:
  - `PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_3.md`: `8b7264b9517af63b93a59a79521ec20a3908d72be78c3ab1488d223481f7d6e9`
  - `pythagorean_filter_confirmatory_v0_3.py`: `786b0cd56fa291aa4ba030261a2fd6b00e632dc7e5623ef5a5477a3a704d8155`
  - `PYTHAGOREAN_FILTER_PRE_GATE_MANIFEST_v0_3.json`: `9ce530426121eca92d1501bf811e530e4ddff0f2a43981d3d03952565dd1929c`
- **v0.4**:
  - `PYTHAGOREAN_FILTER_CONFIRMATORY_SPEC_v0_4.md`: `a85f3d97b15d29c58fc5e09c9f2d7513027b6a5fca0f11491f7796cefb798449`
  - `pythagorean_filter_confirmatory_v0_4.py`: `63ea935191f110a2afeb83b65f1467c8b2cb237544a3b86de5798aeb450a0407`
  - `PYTHAGOREAN_FILTER_PRE_GATE_MANIFEST_v0_4.json`: `2b9638364333214eab443f90103be39232240ee7fd8e5d69d4d4464bef917966`

---

## 4. Verification

To verify candidate consistency:

```bash
# 1. Run deterministic synthetic gate tests
python3 pythagorean_filter_synthetic_gate_test_v0_5.py

# 2. Run gate mutation characterization
python3 pythagorean_filter_gate_characterization_v0_5.py
```

---

## 5. Separate Lean proof track

The mathematical identity and modular-filter equivalence are maintained as a
separate proof artifact in `proof/lean-gcd-identity/`.  That directory has its
own pinned Lean/Mathlib environment, frozen hashes, end-to-end verifier, and CI
gate.

Closing or reproducing the Lean proof does **not** freeze, authorize, or execute
the v0.5 confirmatory performance benchmark.  The repository-level benchmark
status at the top of this file therefore remains `PRE-GATE / NOT FROZEN / NO
CONFIRMATORY RUN`.
