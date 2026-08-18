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

The graph remains intentionally acyclic:

```text
CANONICAL REAL DATA
        -> INPUT_ADAPTER
        -> ROOM_01_SIGNAL
        -> ROOM_02_EDGE_DETECTOR
        -> SCORE / EV EVIDENCE
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
  -> anchor_date - 2 calendar day = T-2
  -> anchor_date - 7 calendar day = T-7
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

## Room 02 — Edge Detector V1

`room_02_edge_detector.py` is the first mathematical research room.

Its first hypothesis is deliberately narrow:

> Does the historical frequency prior available at day `t` contain OOS information about number presence at `t+1`?

The room computes only evidence:

```text
feature at t
   -> OOS conditional probability
   -> baseline probability
   -> probability delta
   -> permutation p-value
   -> optional explicit payoff EV
   -> EDGE_CANDIDATE / NO_EDGE_PROVEN
```

### Hard research rules

- no target leakage
- training-only threshold selection
- no in-sample claim as an edge
- permutation test required
- explicit payoff model for EV
- Kelly is downstream and cannot manufacture an edge
- multiple-testing correction before promotion
- `EDGE_CANDIDATE` is not trade authorization

The full protocol is in `docs/EDGE_SEARCH_PROTOCOL_V1.md`.

## Replay and evidence

Replay remains first-class. A research result must be reproducible from canonical input, room signature, parameters, and compact evidence hashes. Debug state is not part of the canonical output hash.

## Resource boundary

Render Free 512 MB is a hard architectural boundary. Use bounded streaming/chunked execution and avoid whole-dataset materialization. Heavy historical research must run outside the Brain runtime. Never trade forensic correctness for memory.

## Development gate

```text
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Current status

- Brain foundation: **FROZEN**
- N071 terminal DB decision: **IMMUTABLE DENY** due external binding limitation
- Layer 1: **ACTIVE RESEARCH / PROMOTION LOCKED**
- Room 01: **V4 DATE-ALIGNED + DOMAIN-LOCKED + DENSITY-GUARDED + REPLAYABLE**
- Room 02: **WALK-FORWARD + OOS + PERMUTATION-GATED; REAL-DATA RESULT NOT YET CLAIMED**
- Staircase/promotion: **LOCKED**
