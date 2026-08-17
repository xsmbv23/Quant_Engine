# Quant Engine Layer 1 — Admission Contract

## Frozen upstream

The Brain/Forensic foundation is frozen. Do not reopen or weaken infrastructure gates.

Canonical upstream repository: `xsmbv23/Project_Brain_AI`

Canonical next action: `QUANT-N001`

## One Forensic admission chain

Database admission is ONE FSM, not multiple Forensic systems:

```text
DB_EXISTENCE -> DB_BINDING -> SECRET_RESOLUTION -> DB_TLS_ADMISSION -> NETWORK_ORIGIN_PROOF -> DB_ROUND_TRIP -> PROMOTION
```

A PASS at one gate is only a prerequisite for the next gate. It never grants inherited permission.

First FAIL or UNKNOWN stops reachability to later gates. Later gates are UNREACHED, not PASS and not FAIL.

## Layer 1 security model

Each sensor, mechanism, function, and algorithm is an independent room.

```text
corridor_key + room_key
```

are distinct capabilities. A protected room may additionally require an inner release/chime response.

Directional layer edges must be explicit. No implicit cycles.

## Responsibility boundaries

- Brain = governance/control plane.
- Quant Engine = calculation/measurement layer.
- Data = source truth.
- Sensors = observation only.
- Algorithms/functions = calculation only.
- Chat = communication interface only.

Quant Engine must not assume durable Brain PostgreSQL access. Durable DB promotion is currently denied by an external binding limitation.

## Resource constraint

Render Free 512 MB is a hard boundary. Architectural guard is 320 MiB. No room may bulk-load large source datasets. Streaming, bounded windows, raw-input hashing, deterministic ordering, and causal-only input are mandatory where applicable.

## Input Adapter N002

The next room is the Input Adapter. It is transport-only and must not perform feature engineering, signal filtering, or normalization.

Required properties:

- stream source records rather than bulk-loading history;
- preserve canonical causal order;
- reject lookahead/future records;
- enforce bounded window policy;
- hash raw input bytes, not transformed data;
- emit compact deterministic output;
- record room-level forensic evidence.

## Promotion rule

Layer 1 may advance only when its room contract and tests provide their own evidence. Never infer PASS from an upstream PASS.
