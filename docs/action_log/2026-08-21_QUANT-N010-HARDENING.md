# QUANT-N010 — Workflow Evidence Hardening Revision

## Scope

Safe parallel prerequisite only. This does not unlock Brain, Room 02, promotion, or any downstream E2E segment.

## Change

The GitHub admission workflow now emits stronger execution provenance in its repository-execution receipt:

- workflow reference
- workflow SHA
- event name
- ref
- actor
- run ID
- run attempt
- commit SHA
- tree hash
- source-set SHA-256
- timestamp

The receipt remains explicitly:

```text
execution_status = PASS
external_runtime_truth = NOT_PROVEN
promotion = DENY
pass_inheritance = false
unknown_is_not_pass = true
```

The receipt validator now requires these provenance fields.

## Why

A workflow receipt must prove that GitHub actually executed the repository verifier. It must not be confused with Render runtime truth. Adding provenance strengthens evidence without changing the authority boundary.

## Current status

The push created commit:

```text
e83955c28bf152e5ffa42c4a0db2eb27b9819b02
```

The following workflow execution is expected to be observable through GitHub's workflow surface, but no PASS is claimed until that external observation is actually returned.

## Forensic decision

```text
N010 = STILL_PENDING_EXTERNAL_CI
Brain state = UNCHANGED
Room 02 = LOCKED
Staircase = LOCKED
Promotion = DENY
```
