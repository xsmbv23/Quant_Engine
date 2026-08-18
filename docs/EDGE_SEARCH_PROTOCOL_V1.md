# Edge Search Protocol V1

## Purpose

The Quant Engine exists to discover measurable predictive information, not merely to produce governance artifacts. Governance remains mandatory, but it is a gate around research, not the research objective.

## Research chain

```text
CANONICAL REAL DATA
        |
        v
FEATURE EXTRACTOR
        |
        v
TIME-SAFE TARGET ALIGNMENT
        |
        v
TRAIN / OUT-OF-SAMPLE SPLIT
        |
        +--> CONDITIONAL PROBABILITY
        |
        +--> PROBABILITY DELTA
        |
        +--> PERMUTATION TEST
        |
        +--> PAYOFF / EV MODEL
        |
        v
EDGE CANDIDATE or NO EDGE PROVEN
```

## Non-negotiable rules

1. No synthetic production data.
2. A feature at time `t` may use only observations available at or before `t`.
3. A target for a prediction made at `t` must be observed strictly after `t`.
4. Thresholds used to select test observations are learned from training data only.
5. Out-of-sample results are never mixed back into training thresholds.
6. A positive in-sample result is not an edge.
7. A positive OOS delta without a statistical robustness check is not an edge.
8. Permutation p-value is evidence against a label-random null, not proof of profitability.
9. EV is computed only from an explicit payoff model; probability alone is insufficient.
10. Kelly is downstream of a validated edge and must never manufacture one.
11. Multiple-testing control is required before promoting a family of discovered patterns.
12. All candidate results must remain replayable from compact inputs, code version, and parameter hash.

## Current Room 02

`room_02_edge_detector.py` currently implements one deliberately narrow hypothesis:

> Does a number's historical frequency prior to day `t` provide OOS information about its presence on day `t+1`?

It uses:

- walk-forward temporal separation
- training-only quantile threshold
- OOS conditional probability
- OOS probability delta versus baseline
- deterministic permutation test
- optional explicit payoff EV
- minimum sample guards

Status values are:

- `EDGE_CANDIDATE`: statistical screening passed the configured delta and permutation threshold.
- `NO_EDGE_PROVEN`: no edge passed the screen.

`EDGE_CANDIDATE` is **not** a trade authorization.

## Next hypotheses

Room 02 should expand one hypothesis at a time:

1. entropy deviation
2. transition / Markov structure
3. recency-conditioned drift
4. digit-head / digit-tail conditional drift
5. interaction effects
6. multiple-hypothesis correction
7. rolling walk-forward stability
8. payoff-aware EV and only then Kelly sizing

Each hypothesis must have its own feature definition, null hypothesis, OOS protocol, and replay signature.

## Memory boundary

Do not materialize the entire historical universe inside the Render Brain runtime. Heavy historical research belongs in bounded external execution. Brain stores governance/evidence envelopes, not bulk research matrices.
