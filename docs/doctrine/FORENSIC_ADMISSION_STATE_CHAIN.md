# FORENSIC ADMISSION STATE CHAIN — ROOM 01 INHERITANCE

This file inherits the authoritative doctrine from `xsmbv23/Project_Brain_AI`.

## Mandatory rules

```text
ONE_FORENSIC_FSM
PASS_AT_GATE_IS_PREREQUISITE_ONLY
NO_PASS_INHERITANCE
UNKNOWN_IS_NOT_PASS
DEFAULT_DENY
INVARIANT_MUST_REDUCE_UNCERTAINTY_OF_A_SPECIFIC_GATE
READINESS_IS_OBSERVABILITY_ONLY
DRY_RUN_IS_SHADOW_ONLY
DRY_RUN_OUTPUT_IS_NON_EVIDENTIAL
BUFFER != ENGINE_INPUT
PARTIAL != TRUTH
COLLECTION != ADMISSION
SIMULATION != EVIDENCE
```

## Gate chain

```text
EXISTENCE -> BINDING -> TLS_ADMISSION -> ROUND_TRIP -> PROMOTION
```

A PASS at one gate does not imply PASS at another gate. Evidence must belong to the gate being claimed.

## Dry-run

Dry-run may use explicitly marked rejected/non-canonical rehearsal data for debugging and memory measurement, but it must never:

- create canonical state;
- promote data;
- change admission;
- feed real engine input;
- alter collector behavior;
- create a dependency back into acquisition.

## Successor protocol

Every Bot must read Brain state, Quant state, latest action log, and this doctrine before acting. Every action must identify the exact gate whose uncertainty it reduces and persist evidence before promotion.
