# QUANT-N003-PROOF — Execution Protocol

## Gate identity

N003-PROOF is a proof gate for Layer 1 Room 01. It is not a feature, scorer, predictor, or trading decision engine.

## Canonical doctrine

```text
BUILD -> HARDEN -> BREAK -> PROVE
```

`TEST SPEC != EVIDENCE`

`REPRODUCIBLE != CORRECTNESS PROOF`

`SAME RESULT != SAME EXECUTION PATH`

## Proof matrix

### A. Multi-run identity

Target: >= 10 executions where the bounded real fixture and runtime permit.

Required:

```text
FRESH_1 = REPLAY_1 = REPLAY_2 = FRESH_2
```

Comparison scope:

- canonical input hash
- semantic feature snapshot hash
- execution signature
- semantic trace hash
- canonical output hash
- valid-empty reason when output is empty

Final candidate equality alone is insufficient.

### B. Input mutations

| Mutation | Required result |
|---|---|
| reorder non-semantic keys | canonical identity preserved |
| add null/unknown field | explicit deny or defined canonical behavior |
| change one semantic value | evidence/output changes or explicit deny |
| truncate input | deny |
| raw-byte change | raw identity changes and/or deny |

### C. Feature mutations

- remove feature
- reorder feature structure
- change feature type
- alter one feature value

Required: semantic feature hash/trace/output changes or explicit deny.

### D. Trace mutations

- drop one trace step
- reorder trace steps
- replace semantic operation

Required: trace integrity failure and deny when the canonical trace no longer matches the execution.

### E. Trace collision attack

Two distinct semantic paths that happen to produce the same final output must not produce the same semantic execution trace hash.

### F. Hash-preserving attack

Attempt to alter semantics without changing the canonical hash domain. The result must be either canonical hash change or explicit denial. `same hash + different semantic execution` is a hard failure.

### G. Fake-empty attack

Different causes of empty output must remain distinguishable through `valid_empty_reason` and trace/evidence context.

### H. Input sensitivity / dead pipeline

Meaningful input perturbations must be consumed by the execution path. An unexplained constant output distribution is a hard finding.

### I. Partial corruption

Flip one byte in input, feature evidence, or trace material. The corruption must be detected and denied.

### J. Cross-environment replay

Compare execution signatures across environments. Either output/evidence is identical or the signature explicitly marks the executions non-comparable.

Forbidden:

```text
DIFFERENT OUTPUT + SAME EXECUTION SIGNATURE
```

### K. Filesystem branch attack

External filesystem state must not silently introduce a semantic branch. Any allowed external dependency must be explicitly represented in the execution signature/evidence.

### L. Anti-hardcode

Prove that the canonical input actually participates in the feature/evidence/output chain. A hardcoded output that passes replay tests is not proof.

## Gate result semantics

```text
PROOF_FAIL -> FINDING -> FIX -> RE-RUN
PROOF_PASS -> EVIDENCE RECORDED
```

Even complete proof success does not establish model correctness.

## Admission

N004 remains locked until this protocol's completion gate is satisfied on the actual replay path and the compact forensic receipt is persisted.
