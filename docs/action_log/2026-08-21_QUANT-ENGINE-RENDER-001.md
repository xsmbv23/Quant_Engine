# QUANT-ENGINE-RENDER-001 — Render Execution Boundary

## Decision

Create a dedicated Render service for `xsmbv23/Quant_Engine` rather than placing Layer 1 computation inside `Project_Brain_AI`.

This is an infrastructure boundary, not a promotion event.

## Topology

```text
SOURCE / DATA
xsmbv23/xsmb-quant
        |
        v
QUANT ENGINE
xsmbv23/Quant_Engine
        |
        v
LAYER 1 ROOMS
Research / Backtest / Edge / EV / Risk
        |
        v
COMPACT EVIDENCE
        |
        v
PROJECT BRAIN
Governance / Forensic Admission
```

Brain remains the governance authority. Quant Engine never becomes a second governance system and never inherits Brain permissions.

## Render service

- name: `quant-engine`
- service id: `srv-da3k09c9v7es73fnu460`
- URL: `https://quant-engine-rj1k.onrender.com`
- plan: Free
- region: Singapore
- runtime: Python
- instances: 1
- `WEB_CONCURRENCY=1`
- memory guard: 320 MiB
- auto deploy: enabled

## Exact runtime evidence

Deployment:

```text
dep-da3k0ac9v7es73fnu5gg
```

Commit:

```text
fe478179c4164f7a3a51ecfcf7c6e373b88f1874
```

Build:

```text
Build successful
```

Runtime:

```text
Running 'python render_server.py'
Your service is live
```

Observed memory in the measured window:

```text
28,221,440 bytes
```

This is approximately 26.9 MiB and is far below the 320 MiB architectural guard.

## Important security boundary

The Render creation surface currently exposes a public URL. Therefore the service intentionally exposes only:

- `/health`
- `/governance`

Both surfaces return non-secret metadata only.

No canonical dataset is loaded at boot. No synthetic fallback exists. No research computation endpoint is exposed yet. This prevents a public HTTP caller from accidentally becoming a data-ingestion or computation path before an explicit room admission contract exists.

## Forensic state

```text
RENDER SERVICE          = LIVE
RUNTIME BOUNDARY        = PASS
MEMORY GUARD            = PASS
DATASET AT BOOT         = NONE
SYNTHETIC FALLBACK      = FORBIDDEN
COMPUTE API             = LOCKED
PROMOTION               = DENY
ACTION                  = DENY
STAIRCASE               = LOCKED
```

## Non-equivalence rule

Creation of the Render service does NOT imply:

```text
SOURCE_TRUTH = PASS
DATA_ADMISSION = PASS
BACKTEST = PASS
EDGE = PASS
EV = PASS
PROMOTION = PASS
ACTION = PASS
```

Each remains a separate local evidence gate. PASS is prerequisite only and never propagates forward.

## Next action

Preserve the current Brain N116 wait state. The next Quant Engine action is to define the first explicit room execution admission contract and bounded execution protocol without unlocking promotion or action authority.
