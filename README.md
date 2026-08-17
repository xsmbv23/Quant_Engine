# Quant_Engine

Layer 1 Intelligence / Execution Plane for XSMB Forensic / Fosennic architecture.

## Authority

`xsmbv23/Project_Brain_AI` is the frozen Governance and persistent-memory control plane.
`xsmbv23/Quant_Engine` is the active Layer 1 execution plane.
The chat window is communication only and is never the source of truth.

## Frozen Brain foundation

The Brain database admission chain is **one ordered Forensic FSM**:

```text
DB_EXISTENCE
 -> DB_BINDING
 -> SECRET_RESOLUTION
 -> DB_TLS_ADMISSION
 -> NETWORK_ORIGIN_PROOF
 -> DB_ROUND_TRIP
 -> PROMOTION
```

PASS is prerequisite only; it never inherits forward. UNKNOWN is not PASS. The first FAIL or UNKNOWN stops reachability and later gates remain `UNREACHED`. Quant Engine must never reopen or reinterpret the frozen Brain foundation.

## Room model

Every sensor, mechanism, function, or algorithm is a room with immutable identity/version, explicit I/O contract, dependencies, inbound corridor, capabilities, source/code hashes, verification evidence, resource/memory budget, and fail-closed behavior.

A Quant Engine room is a **function boundary, not a second security boundary**. Brain remains the authority for corridor admission, permission graph, and Forensic governance.

## Layer 1 directional graph

The first graph is intentionally acyclic:

```text
CANONICAL REAL DATA
        -> INPUT_ADAPTER
        -> ROOM_01_SIGNAL
        -> SCORE
        -> OUTPUT_RECEIPT
```

No implicit reverse edge and no implicit cycle is allowed.

## Room 01 — V4 temporal/domain hardening

`room_01_signal.py`, `room_01_signal_v2.py`, and `room_01_signal_v3.py` are preserved as historical evidence. `room_01_signal_v4.py` is the current temporal/domain-hardened implementation.

### First-class time index

Temporal identity is carried by `DayRecord(date, values)`. T-1/T-2/T-7 are resolved from the **calendar date**, never from record position.

```text
anchor_date
  -> anchor_date - 1 calendar day = T-1
  -> anchor_date - 2 calendar days = T-2
  -> anchor_date - 7 calendar days = T-7
```

Invariant:

```text
TEMPORAL_FEATURES MUST BE DATE-ALIGNED, NOT INDEX-ALIGNED
```

### Missing-day semantics

Default policy is `STRICT`: a missing calendar day is a hard deny.
Explicit `GAP_AWARE` is allowed for measurement/research and never fabricates a day; an unavailable temporal observation is represented by a gap flag and does not shift T-1/T-2/T-7.

Synthetic fill is forbidden.

### Numeric domain lock

Every canonical day must contain exactly 27 integer values in `0..99`.

```text
VALUE_DOMAIN = integer[0..99], cardinality=27
```

Out-of-domain values or wrong daily cardinality are hard deny conditions.

### Feature density guard

Density is an explicit measurable diagnostic. Default threshold is `0.10` over the 100-value universe and default action is `WARNING`. A DENY action must be explicitly requested with a threshold; density is never silently converted into a decision.

### Replay

Replay is first-class:

```text
python replay.py receipt.json
```

Only allow-listed room versions may replay. The replay bundle carries canonical input and expected feature/output hashes. Same canonical input + same room signature must reproduce the same feature snapshot and output hash.

## Resource boundary

Render Free 512 MB is a hard architectural boundary. Use bounded streaming/chunked execution and avoid whole-dataset materialization. Never trade forensic correctness for memory.

## Development gate

```text
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Current status

- Brain foundation: **FROZEN**
- N071 terminal DB decision: **IMMUTABLE DENY** due external binding limitation
- Layer 1: **READY**
- Room 01: **V4 DATE-ALIGNED + DOMAIN-LOCKED + DENSITY-GUARDED + REPLAYABLE**
- Staircase/promotion: **LOCKED**
