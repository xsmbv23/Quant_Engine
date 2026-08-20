# QUANT-N010 — Parallel Foundation Admission Hardening

## Purpose

This action is safe to execute while Brain remains in `WAIT_EXTERNAL_OBSERVATION`.
It does not unlock Layer 1 promotion and does not create a second Forensic security system.

## Change

Added `foundation_admission.py` as a **read-only semantic mirror** of the frozen Brain admission chain:

```text
DB_EXISTENCE
 -> DB_BINDING
 -> SECRET_RESOLUTION
 -> DB_TLS_ADMISSION
 -> NETWORK_ORIGIN_PROOF
 -> DB_ROUND_TRIP
 -> PROMOTION
```

The module enforces three invariants for Quant-side reasoning:

1. A gate is reachable only after its immediate predecessor is explicitly `PASS`.
2. `UNKNOWN`, `FAIL`, and `UNREACHED` are not pass-through states.
3. A later `PASS` without its own prerequisite `PASS` is rejected as `PASS_WITHOUT_LOCAL_PREREQUISITE`.

## Security boundary

Quant Engine is an execution/research plane. Brain remains the sole authority for corridor admission, capability policy, Forensic governance, and persistent promotion state.

This module therefore has **no mutation authority** and cannot write Brain state.

## Tests added

`tests/test_foundation_admission.py` covers:

- first-gate reachability;
- UNKNOWN/FAIL stopping downstream reachability;
- incomplete chain remaining inadmissible;
- inherited PASS rejection;
- complete explicit PASS chain acceptance.

## Render/OOM

No heavy dataset operation is introduced. The change is metadata-only and bounded. No whole historical dataset is loaded.

## Next

`QUANT-N011` — audit all Layer 1 rooms for accidental gate reinterpretation, reverse-edge creation, hidden promotion paths, and any unbounded data materialization before adding further intelligence.
