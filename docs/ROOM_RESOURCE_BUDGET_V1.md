# LAYER 1 ROOM RESOURCE BUDGET V1

Every Quant Engine room must declare its resource class before implementation.

## Room classes

```text
R0 — pure bounded calculation
R1 — bounded single-shard sensor
R2 — multi-shard worker
R3 — historical/batch computation
R4 — training/optimization
```

R0/R1 may be invoked through a verified lightweight corridor only when their input/output bounds are explicit.

R2/R3/R4 must not execute inside the Render Free 512 MB Brain/UI process.

## Required room metadata

Each room must declare:

- estimated peak memory;
- expected input bytes/rows;
- expected output bytes/rows;
- CPU intensity;
- maximum shard count per invocation;
- timeout expectation;
- restart/resume point;
- evidence artifact ID;
- whether it requires an external worker.

## Hard rule

```text
NO RESOURCE BUDGET
        ↓
ROOM CANNOT OPEN
```

The door remains LOCKED until the resource budget is verified.

## Execution pattern

```text
Brain
  ↓ compact request
Corridor
  ↓
Room
  ↓ bounded execution
Artifact / Evidence
  ↓
Corridor
  ↓
Brain
```

Raw historical data must not be copied into Brain merely because a room needs it.
