# QUANT-N010 — Bounded Room 01 Verification

## Authority

This action is a **Layer 1 / Room 01 repository-execution action only**.

It must not mutate Brain state, must not promote canonical data, and must not unlock Room 02 or the staircase.

## Required execution

1. Verify source contracts.
2. Verify semantic parser contracts.
3. Run bounded repository unit tests.
4. Emit a real GitHub workflow execution receipt.
5. Keep `external_runtime_truth = NOT_PROVEN` unless independently observed elsewhere.

## Immutable constraints

- Real source only.
- No synthetic history.
- No backfill/interpolation/silent fill/replacement.
- Raw evidence is never deleted.
- `UNKNOWN_IS_NOT_PASS`.
- `UNREACHED_IS_NOT_PASS`.
- PASS is local prerequisite only.
- No PASS inheritance.
- Brain remains governance authority.
- Quant Engine remains Layer 1 Room 01.
- Room 02 remains locked.
- Staircase remains locked.
- Render Free 512 MB is a hard boundary; 320 MiB guard remains mandatory.
- Workflow PASS is repository-execution evidence, not external runtime truth.

## Expected receipt

The workflow receipt must identify the exact GitHub run, attempt, commit SHA, execution timestamp and evidence kind. It must explicitly state that external runtime truth is not proven.

## Success condition

N010 is complete only when the workflow execution is independently observable and the receipt is available. No Brain promotion state changes as a result.
