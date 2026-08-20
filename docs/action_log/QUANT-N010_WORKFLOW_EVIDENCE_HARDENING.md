# QUANT-N010 — Workflow Evidence Hardening

## Status

`IMPLEMENTED_AS_LOCAL_PREREQUISITE`

## Change

Added `docs/WORKFLOW_EVIDENCE_PROTOCOL_V1.md` to make evidence classes explicit and prevent cross-Bot confusion between repository state, CI execution, runtime execution, and research evidence.

## Core invariant

```text
repository file != workflow execution receipt
workflow execution != runtime execution
runtime execution != research evidence
PASS does not inherit
UNKNOWN is not PASS
```

## Why this is required

The Brain foundation currently records CI observation as unknown when an exact-current workflow receipt is not observable. Quant Engine may continue safe local engineering, but it must not turn local verification into a claim about external execution.

## Security / Forensic effect

- no promotion authority added
- no Brain gate reopened
- no credential handling added
- no source data loaded into Brain
- no Render memory boundary changed
- historical evidence remains append-only

## Next handoff

Continue only with bounded Layer 1 research/replay work whose outputs are explicitly classified as research evidence. Any claim about CI or Render runtime requires its corresponding external receipt.
