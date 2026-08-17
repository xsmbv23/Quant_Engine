# N003-PROOF — Anti-Illusion Doctrine

## Purpose

N003-PROOF proves forensic reproducibility and execution integrity. It does **not** prove predictive/model correctness.

A pipeline can be perfectly reproducible and still be consistently wrong. This is the `CONSISTENTLY_WRONG_PIPELINE` failure class.

Therefore N003-PROOF adds a second boundary inside the proof gate:

```text
FORENSIC INTEGRITY
        !=
SEMANTIC/CAUSAL RESPONSIVENESS
        !=
MODEL CORRECTNESS
```

## Mandatory anti-illusion checks

### 1. Input sensitivity

A meaningful semantic input perturbation must either:

- change canonical evidence/output/trace, or
- be explicitly rejected by a declared policy.

A constant output under meaningful input mutation is a hard finding.

### 2. Feature information

Feature snapshots must not silently collapse to a constant vector when the accepted input contains meaningful variation.

Minimum proof signals:

- non-zero variance where the feature contract permits variation;
- more than one unique semantic state across a multi-scenario fixture, unless the contract explicitly explains why not;
- no hidden fallback that converts missing/invalid input into a fabricated constant feature vector.

This is an information-presence check, not a statistical quality claim.

### 3. Causal dependency

The proof harness must demonstrate that canonical input participates in the feature/evidence/output chain.

Required adversarial operation:

```text
input A -> execution A
input B (semantic perturbation) -> execution B
```

If A and B produce identical evidence while the perturbation is contract-relevant, the proof gate fails unless the contract explicitly denies B.

### 4. Anti-hardcode

The harness must detect suspicious many-to-one behavior where materially different accepted inputs repeatedly produce the same output/evidence.

A fixed expected output is never sufficient evidence.

### 5. Execution graph identity

A semantic trace hash is necessary but not assumed sufficient to prove execution topology. Future proof evidence should capture a compact execution graph fingerprint containing:

- ordered semantic operations;
- branch decisions;
- feature usage map;
- dependency identities.

Two distinct semantic execution paths must not silently collapse into one fingerprint.

## Important boundary

These checks may prove that the pipeline responds to its inputs. They still do not prove that its signal is economically useful, statistically valid, or predictive.

```text
N003 PASS
    = forensic integrity + causal responsiveness proof

N003 PASS
    != model correctness

N004 / higher semantic validation
    remains separately locked
```
