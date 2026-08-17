# QUANT-N003-PROOF — Real Multi-Day History Admission Contract

## Purpose

N003-PROOF is not allowed to claim temporal, sensitivity, causal, or anti-hardcode proof from a one-day fixture.

## Hard invariant

```text
NO_PARTIAL_TEMPORAL_CLAIM
```

If temporal coverage is below the required threshold, temporal/causal proof is `UNREACHED`, not `PASS`.

## Minimum viable real history

Strict proof minimum:

```text
>= 10 consecutive real-source dates
```

Preferred proof window:

```text
21–30 consecutive real-source dates
```

The strict minimum is an admission threshold, not a recommendation.

## Source truth requirements

Every admitted day must retain:

- source identifier
- source URL/locator or immutable source reference
- source retrieval timestamp
- source business/data date
- raw bytes identity SHA-256
- parser/schema version
- exact canonicalized representation SHA-256
- provenance chain

Forbidden:

- synthetic history
- generated/backfilled prices or outcomes
- silent interpolation
- silent fill
- silently replacing missing days
- deleting raw source evidence

## Coverage

```text
expected_dates = all dates in the declared proof interval
observed_dates = dates with independently evidenced real source data
coverage_ratio = |observed_dates| / |expected_dates|
```

Strict N003 admission requires:

```text
coverage_ratio = 1.0
```

and at least 10 consecutive observed dates.

Any gap makes strict temporal proof `UNREACHED` unless an explicit gap-aware protocol is being tested.

## Canonical freeze

The admitted dataset must be frozen before proof execution:

```text
RAW SOURCE SET
    -> raw-byte hashes
    -> provenance manifest
    -> canonical input envelope
    -> canonical_input SHA-256
    -> immutable evidence receipt
```

`canonical_input.py` remains the canonical JSON freeze primitive for the engine.

## Required proof sequence

```text
ACQUIRE REAL HISTORY
      ↓
VERIFY PROVENANCE
      ↓
VERIFY DATE CONTIGUITY
      ↓
FREEZE CANONICAL INPUT
      ↓
FRESH_1
      ↓
REPLAY_1
      ↓
REPLAY_2
      ↓
FRESH_2
      ↓
MUTATION / SENSITIVITY / CAUSAL / ANTI-HARDCODE
      ↓
PERSIST COMPACT FORENSIC RECEIPT
```

## Promotion rule

Until the real multi-day dataset satisfies this contract:

```text
N003-PROOF = IMPLEMENTED_NOT_PROVEN
N004 = LOCKED
```

No amount of unit-test success can override missing real history.
