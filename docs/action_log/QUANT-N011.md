# QUANT-N011 — Layer 1 Workflow Boundary Hardening

## Scope

Safe parallel prerequisite work while Brain remains `WAIT_EXTERNAL_OBSERVATION` and `action_space=0`.

This action does **not** unlock Room 02, does not alter Brain state, and does not create promotion authority.

## Change

Hardened `.github/workflows/admission_check.yml` with:

- `permissions: contents: read`;
- explicit 10-minute job timeout;
- non-cancelling concurrency group so an active evidence-producing run is not silently replaced;
- existing semantic receipt boundary retained;
- existing `external_runtime_truth: NOT_PROVEN` retained;
- existing `promotion: DENY` retained.

## Forensic meaning

The workflow receipt remains evidence that repository verifiers executed in GitHub Actions. It is **not** evidence that Render runtime truth is healthy.

```text
GITHUB_WORKFLOW_PASS
    !=
RENDER_RUNTIME_PASS
```

and:

```text
WORKFLOW_TRIGGERED
    !=
WORKFLOW_PASS
```

The second distinction is especially important: an observable workflow execution receipt is required before N010 can close, but the receipt itself must still preserve the separate runtime-truth boundary.

## Render/OOM

No bulk dataset is loaded. No Render compute surface is changed. The change is workflow metadata/security hardening only.

## Current limitation

The available GitHub observation surface has previously returned zero observable workflow runs for the exact validator commit. Therefore CI status remains UNKNOWN until an independently observable exact-current workflow receipt is available.

## Next

`QUANT-N012` — audit the Room 01 source/collector boundary for reverse edges, generic page-number truth leakage, ad/redirect contamination, unbounded buffering, and source/semantic hash confusion. Keep all changes local and non-promotional.
