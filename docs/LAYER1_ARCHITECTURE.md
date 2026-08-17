# Quant Engine Layer 1 — Architecture

## Authority boundary

`Project_Brain_AI` is the frozen Governance Control Plane and persistent-memory authority.
`Quant_Engine` is the Layer 1 execution plane.

Quant Engine does **not** recreate Brain security, the Forensic admission FSM, or the permission graph.

## Directional graph

The initial graph is intentionally acyclic:

```text
CANONICAL REAL DATA
        │
        ▼
 INPUT_ADAPTER
        │
        ▼
 ROOM_01_SIGNAL
        │
        ▼
 SCORE
        │
        ▼
 OUTPUT_RECEIPT
```

No implicit reverse edge exists. No room may call a later room by convention. Dependencies must be declared explicitly in the room contract.

## Corridor / room model

A corridor is the declared communication path between two governed components.
A room is a single execution boundary: sensor, mechanism, function, algorithm, or scoring operation.

```text
corridor_key + room_key -> admitted function call
```

These keys are **capabilities**, not replacements for Brain's security authority.

A protected room may additionally require an inner release controlled by Brain. Quant Engine cannot self-grant that release.

## Room contract

Every room declares:

- immutable room ID;
- version;
- layer;
- role (`sensor`, `mechanism`, `function`, `algorithm`, `adapter`);
- input schema;
- output schema;
- dependency rooms;
- allowed inbound corridors;
- required capability names;
- source/code hash;
- evidence policy;
- resource budget;
- fail-closed behavior.

## Observation vs calculation

Sensors observe and report. They do not calculate portfolio decisions.

Calculation engines transform admitted inputs into deterministic outputs.

```text
SENSOR = OBSERVATION ONLY
ENGINE = CALCULATION ONLY
```

A sensor cannot silently become an execution engine.

## Memory discipline

Render Free 512 MB is a hard boundary.

Layer 1 must prefer:

- streaming reads;
- bounded chunks;
- iterator-based transforms;
- compact receipts;
- no whole-dataset materialization;
- no duplicate copies of large frames;
- explicit per-room memory budgets.

Brain's 320 MiB guard remains a Brain runtime rule. Quant Engine must define its own measured budget without weakening the Brain guard.

## First milestone

Do not build a full multi-room orchestration framework first.

First prove one real execution path:

```text
REAL CANONICAL DATA
 -> INPUT ADAPTER
 -> ROOM_01_SIGNAL
 -> SCORE
 -> HASHED RECEIPT
```

No synthetic data, no lookahead, and no guessed source values.
