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

## Room 01 — active implementation

`room_01_signal.py` is preserved as historical evidence.
`room_01_signal_v2.py` is preserved as a historical iteration.
`room_01_signal_v3.py` is the current deterministic feature/selection implementation.

### Mandatory correction

Recency exclusion is **not** applied before temporal feature extraction. Doing so would destroy T-1/T-2 observations and make temporal echo impossible to observe.

Correct order:

```text
bounded canonical window
  -> extract frequency + recency flag + T-1/T-2/T-7 + digit imbalance
  -> apply recency selection
  -> candidate output
```

Legacy V5.8/V16.0 cores provide research ideas only. Their Excel/stateful/crawler implementations are not copied into Room 01.

Room 01 output is a measurable raw signal, **not a probability or proof of predictive edge**.

## Resource boundary

Render Free 512 MB is a hard architectural boundary. Use bounded streaming/chunked execution and avoid whole-dataset materialization. Never trade forensic correctness for memory.

## Development gate

CI/test gate:

```text
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Foundation status

- Brain foundation: **FROZEN**
- N071 terminal DB decision: **IMMUTABLE DENY**
- Layer 1: **READY**
- Room 01: **V3 DETERMINISTIC FEATURE EXTRACTION + SELECTION**
- Staircase/promotion: **LOCKED**
