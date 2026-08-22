# Quant Engine — Canonical Boundary V1

## Responsibility

This repository is the quantitative/data plane. It owns data ingestion, temporal data foundation, reconciliation, canonical quantitative datasets, causal feature engineering, edge research, probability/outcome models, payout/cost models, EV, backtest/replay, prediction ledger and quantitative P&L/ROI analysis.

## It must not own

- BOT1 canonical governance state.
- Project Brain admission authority.
- Worker allocation authority.
- Render deployment policy.
- Cross-bot promotion decisions.

## Canonical quantitative pipeline

`source observation -> raw artifact -> provenance/hash -> temporal foundation -> multi-source reconciliation -> canonical dataset -> causal feature -> feature lineage/replay -> edge research -> probability -> payout/cost -> EV -> OOS/WFO -> robustness/drift -> prediction ledger -> P&L/ROI`

## Hard quantitative rules

- Edge is not a signal.
- Backtest success is not proof of edge.
- Feature lineage must be reproducible.
- No lookahead.
- Multiple-testing control is required for broad hypothesis search.
- OOS and walk-forward validation are required before admission.
- EV is evaluated independently of Edge discovery.
- EV is checked at pair, set, strategy, day and portfolio levels where applicable.
- EV < 0, UNKNOWN, NaN, +Inf or -Inf is a hard deny for action.
- Zero bets is a valid result.
- Replay failure invalidates edge admission.

## Memory rules

Collectors/backfills are streaming and bounded. Never bulk-load the full historical range into RAM. Prefer one-day/page processing, persist, release memory, then advance.

## File organization target

- `collectors/` — source adapters only.
- `data/` — raw/temporal/reconciliation/data contracts.
- `features/` — causal feature engine and lineage.
- `research/` — hypotheses, tests, multiple-testing control.
- `edge/` — edge admission and stability.
- `models/` — probability/outcome models.
- `economics/` — payout, cost, EV.
- `backtest/` — replay and walk-forward.
- `ledger/` — prediction/decision records.
- `tests/` — quantitative and forensic regression.
- `contracts/` — machine-readable invariants.
- `docs/` — architecture/runbooks only.
- `orchestration/` — adapters only; no governance authority.

Existing files are migrated only after dependency and workflow audit.
