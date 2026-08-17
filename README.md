# Quant_Engine

Layer 1 Intelligence / Execution Plane for XSMB Forensic / Fosennic architecture.

## Authority

`xsmbv23/Project_Brain_AI` is the frozen Governance and persistent-memory control plane.
`xsmbv23/Quant_Engine` is the active Layer 1 execution plane.
The chat window is communication only and is never the source of truth.

The Brain foundation is frozen. Its database admission chain is **one ordered Forensic FSM**:

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

Every sensor, mechanism, function, or algorithm is a room with:

- immutable room identity/version;
- explicit input/output contract;
- explicit dependency list;
- explicit inbound corridor;
- explicit capability names;
- source/code hashes;
- verification evidence;
- resource/memory budget;
- fail-closed behavior.

A Quant Engine room is a **function boundary, not a second security boundary**. Brain remains the authority for corridor admission, permission graph, and Forensic governance.

Conceptually:

```text
corridor_key + room_key -> admitted function call
```

A protected room may additionally require an inner release from Brain. Quant Engine cannot self-grant that release.

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

## Room 01

`contracts/room_01_signal.json` defines the first room. Its implementation is intentionally a deterministic skeleton until real canonical data is admitted. It must not invent a signal merely to produce a green demo.

The first receipt contains only compact forensic metadata:

```text
input_hash
output_hash
runtime_ms
memory_bytes
```

## Resource boundary

Render Free 512 MB is a hard architectural boundary. Use bounded streaming/chunked execution and avoid whole-dataset materialization. Never trade forensic correctness for memory.

## Development gate

CI runs the room contract tests before any intelligence is added.

```text
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Foundation status

- Brain foundation: **FROZEN**
- N071 terminal DB decision: **IMMUTABLE DENY**
- Layer 1: **READY**
- Room 01: **CONTRACT + DETERMINISTIC SKELETON ONLY**
- Staircase/promotion: **LOCKED**
