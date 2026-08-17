# Quant_Engine

Layer 1 Intelligence / Execution Plane for XSMB Forensic / Fosennic architecture.

This repository is intentionally **empty of trading intelligence at foundation stage**.

## Authority

`Project_Brain_AI` is the frozen Governance and persistent-memory control plane.

`Quant_Engine` is the active Layer 1 execution plane for future sensors, mechanisms,
functions and algorithms.

The chat window is communication only and is never the source of truth.

## Critical separation rule

> **A Room in Quant Engine is a function boundary, not a second security boundary.**

Quant Engine MUST NOT recreate Brain's corridor locks, permission graph, Forensic
admission FSM, or another governance system.

Security/admission authority remains in Brain. Quant Engine implements governed
execution once its room contract has been admitted.

## Room model

Every sensor/mechanism/function/algorithm is a separately governed room with:

- room identity and version;
- input/output contract;
- dependency declaration;
- allowed callers;
- allowed corridors;
- required capabilities;
- lineage and source hashes;
- verification evidence;
- fail-closed door state.

Room-local contracts validate execution boundaries, but they do not become a new
Forensic authority.

## Brain Forensic admission semantics

There is **ONE** Forensic database admission FSM:

```text
DB_EXISTENCE
 -> DB_BINDING
 -> SECRET_RESOLUTION
 -> DB_TLS_ADMISSION
 -> NETWORK_ORIGIN_PROOF
 -> DB_ROUND_TRIP
 -> PROMOTION
```

A PASS at one gate is only a prerequisite for evaluating the next gate. It never
inherits forward. The first FAIL or UNKNOWN stops reachability; later gates are
`UNREACHED`, not `PASS` or `FAIL`.

The foundation currently has a terminal immutable external-limitation DENY for
durable PostgreSQL binding. Quant Engine MUST NOT reopen or reinterpret that state.

## Layer 1 first milestone

The first execution frame is intentionally minimal:

```text
CANONICAL DATA
  -> INPUT ADAPTER
  -> ROOM 01 / SIGNAL FUNCTION
  -> SCORING
  -> OUTPUT
```

Success criterion:

```text
RUN -> OUTPUT -> MEASURABLE RESULT
```

Do not build multi-room orchestration, heavy corridor abstractions, duplicate
permission systems, or duplicate forensic layers before the first real end-to-end
signal result exists.

## Resource boundary

Render Free 512 MB is a hard architectural boundary. Keep the Brain runtime dataset-free
and use bounded, streaming/chunked work in execution components. A 320 MiB guard is
the conservative Brain runtime guard. Never trade forensic correctness for memory.

## Foundation status

- Brain foundation: **FROZEN**
- N071 terminal DB decision: **IMMUTABLE DENY**
- Layer 1 design: **READY**
- Staircase/promotion: **LOCKED**
- Next execution milestone: **QUANT-N001**
