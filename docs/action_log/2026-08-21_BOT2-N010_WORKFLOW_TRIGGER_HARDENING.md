# BOT2 / QUANT-N010 — Workflow Trigger Hardening

## Context
Brain canonical state remains authoritative and currently has `ACTION_SPACE=0`, `BRAIN-N125_WAIT_EXTERNAL`, and `PROMOTION=DENY`. This action is deliberately isolated to Quant Engine Layer 1 Room 01 and must not alter Brain admission authority.

## Change
Updated `.github/workflows/admission_check.yml` to run on controlled `push` events affecting:

- `contracts/**`
- `tools/**`
- `tests/**`
- `.github/workflows/admission_check.yml`
- `state/**`

`workflow_dispatch` remains available.

The workflow already emits a receipt explicitly labeled:

`evidence_kind = REPOSITORY_VERIFIER_EXECUTION`

and:

`external_runtime_truth = NOT_PROVEN`

so repository CI execution cannot be misinterpreted as external Render runtime truth.

## Exact evidence

Change commit:

`a416984ee39a50dd2419926c045c4826a1623a21`

Immediately after the change, the available workflow observation surface returned:

`workflow_runs = []`

Therefore **no workflow execution PASS is claimed**.

## Admission semantics

```text
Quant workflow trigger hardening = IMPLEMENTED
Workflow execution              = UNKNOWN
External runtime truth           = NOT_PROVEN
Brain promotion                  = DENY
Brain state mutation             = NONE
Room 02                          = LOCKED
Staircase                        = LOCKED
```

## Next

Observe an independently surfaced GitHub Actions run for the exact commit. If a run becomes observable, inspect its jobs/artifact receipt and classify it strictly as repository-execution evidence. Do not promote Brain from this evidence.
