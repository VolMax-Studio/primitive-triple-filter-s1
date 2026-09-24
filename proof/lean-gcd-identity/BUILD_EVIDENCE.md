# Build evidence and scope

- Artifact: `primitive-triple-filter-s1/proof/lean-gcd-identity`
- Status before external CI: `SPREMNO ZA NEZAVISNI GEJT`
- Final ratifier: Ivan Nestorov

## Frozen mathematical source

```text
5b97b0a5eea88415f98783443c4f15fc3b4d1030fd3b0e99826110795a0216f5  PrimitiveTripleFilter.lean
```

This is byte-for-byte the A source later imported by
`primitive-composition-square-content-s1`.  The closure work does not modify
that file or either public theorem statement.

## Pinned environment

```text
Lean v4.34.0
Lean commit 293d5d0c0c3f3dded4688b3ccd6a33939ac5102b
Mathlib v4.34.0
Mathlib commit 5ed2965256430c3649e86755f9576b54eca72435
```

## Gate obligations

1. All frozen hashes match before and after execution.
2. The Mathlib revision in `lake-manifest.json` is exact.
3. The forbidden-token scan executes fail-closed.
4. `lake build PrimitiveTripleFilter` passes.
5. The `y = 0` conjugate witness passes.
6. Both public theorems report only
   `[propext, Classical.choice, Quot.sound]`.

The GitHub Actions run is the authoritative external execution record.  A
successful run supplies independent-machine kernel reproduction; it does not
self-ratify novelty or the separate v0.5 performance benchmark.
