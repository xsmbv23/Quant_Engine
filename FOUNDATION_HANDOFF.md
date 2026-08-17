# Quant Engine — Foundation Handoff

This repository is Layer 1. It inherits a **frozen Forensic foundation** from `xsmbv23/Project_Brain_AI`.

## First rule

Do not reopen Brain infrastructure because durable PostgreSQL promotion is currently DENIED. That DENY is an immutable external limitation, not a runtime failure.

## Required reading

Before implementing any sensor, mechanism, function, or algorithm, read the normative foundation document:

`Project_Brain_AI/docs/architecture/FORENSIC_DATABASE_ADMISSION_CHAIN.md`

The chain is one Forensic FSM:

```text
DB_EXISTENCE
 -> DB_BINDING
 -> SECRET_RESOLUTION
 -> DB_TLS_ADMISSION
 -> NETWORK_ORIGIN_PROOF
 -> DB_ROUND_TRIP
 -> PROMOTION
```

PASS at one gate is only a prerequisite for the next gate. No PASS inheritance is permitted. UNKNOWN is not PASS. First FAIL/UNKNOWN stops downstream reachability.

## Layer 1 room model

Every sensor, mechanism, calculation function, or algorithm is an independent room:

```text
LAYER 1
  |
  +-- corridor key
  |
  +-- room key
  |
  +-- room admission
  |
  +-- optional inner latch for protected rooms
  |
  +-- room-local forensic evidence
  |
  +-- append-only action log
```

Corridor authorization and room authorization are distinct capabilities. A room must not be reachable merely because the corridor is valid.

Protected rooms may require an inner release/chime step controlled by the higher-trust owner of the room.

## Directionality

Layer 1 must use explicit directional edges. Do not create an implicit all-to-all graph. A downstream room may consume only declared upstream evidence. Cycles require an explicit architectural decision and must not appear accidentally.

## Role separation

- Brain = governance/control plane.
- Data = source truth.
- Quant Engine = calculation/algorithm layer.
- Sensor = observation only unless explicitly classified otherwise.
- Chat = communication interface only.

## Resource constraint

Render Free has a hard 512 MB boundary. The inherited conservative guard is 320 MiB. Quant Engine rooms must budget memory independently and avoid loading large datasets into Brain or Render health paths.

## Promotion boundary

Quant Engine must not assume it has durable Brain PostgreSQL authority. Until an authorized external Render binding exists and the full admission chain passes, durable Brain evidence remains unavailable.

## Successor protocol

Every action must:

1. record what was changed;
2. record exact evidence;
3. record PASS/DENY/UNKNOWN;
4. preserve historical failures;
5. define the next action;
6. never overwrite the meaning of a prior event.

The repository is the durable handoff. The chat window is not the memory authority.
