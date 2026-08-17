# N003 — Replay Truth / Forensic Invariants

## Architectural status

`N003` is an invariant-layer contract, not an implementation detail.

No `QUANT-N004` signal/ML/alpha expansion is admissible until N003 is proven.

## Invariants

### 1. Typed hash domain

The canonical hash domain MUST distinguish:

```text
INT   != FLOAT
INT   != STRING
BOOL  != INT
DECIMAL != INT
```

The serializer MUST NOT normalize these into the same scalar representation.
Non-finite floats are forbidden.

### 2. Deterministic sequence order

Lists/tuples are semantic ordered sequences. Their order is part of the hash domain.
Unordered `set` / `frozenset` values are forbidden from canonicalization.
Any upstream construction from an unordered container MUST explicitly establish deterministic order before hashing.

### 3. Float domain

Layer 1 should prefer integer/fixed-domain values.
Where a float is unavoidable in an evidence envelope, it MUST be represented with an explicit float type tag and fixed decimal precision. It MUST never be silently collapsed into an integer, string, or Decimal representation.

### 4. Execution signature

A replay receipt MUST identify:

- room version
- code hash
- Python version
- Python implementation
- OS
- platform signature
- architecture
- dependency hash

Wall-clock values MUST NOT enter the execution signature.

### 5. Input boundary

The replay input file is read-only.
Replay consumes one byte snapshot, verifies file identity metadata before/after the read, then operates from that snapshot. A mutation during acquisition is `DENY`.

Replay MUST NOT mutate source input.

### 6. Pure replay boundary

After input acquisition, replay MUST be a pure computation over the frozen input and explicitly supplied configuration.

Forbidden dependencies include:

- network
- subprocess
- random
- wall clock
- environment lookups
- hidden filesystem reads

The replay module is statically checked for obvious external/runtime dependencies.

## Evidence identity

The target equality is:

```text
FRESH_1 == REPLAY_1 == REPLAY_2 == FRESH_2
```

for the same canonical input and pinned room version.

## Critical semantic rule

```text
REPRODUCIBLE != CORRECT
```

A matching hash proves consistency with the declared execution path. It does NOT prove that the algorithm, data, model, or business rule is correct.

Therefore:

```text
REPRODUCIBILITY = EVIDENCE OF CONSISTENCY
CORRECTNESS      = SEPARATE UNPROVEN CLAIM
```

The system MUST permit the state:

```json
{"reproducibility":"PASS","correctness":"NOT_PROVEN"}
```

and MUST NOT upgrade correctness merely because replay hashes match.

## Promotion rule

```text
N003 PASS
    -> permits consideration of QUANT-N004

N003 FAIL / UNKNOWN
    -> QUANT-N004 LOCKED
```

## Successor instruction

A future AI agent MUST read this contract before modifying canonicalization, replay, receipts, or room execution. Any change to this contract requires a new numbered forensic action and invalidates prior assumptions until re-proven.
