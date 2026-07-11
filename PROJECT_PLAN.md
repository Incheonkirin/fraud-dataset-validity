# Project Plan

## Problem Statement

Public fraud datasets are often validated by training a model and reporting a
score. That is not enough. A dataset can produce high model scores when the
label is recoverable from amount buckets, category codes, entity IDs, duplicate
rows, label leaks, or weak split design.

This project defines and implements a protocol for testing those failure modes
before model comparisons begin.

## Completed Phase 1: AI Hub Failed Case Study

Implemented tests:

- `T0` evaluation integrity
- `T1` amount-only baseline
- `T2` single-feature shortcuts
- `T3` class distribution overlap
- `T4` ID memorization and entity holdout
- `T5` zero-fraud low-amount region
- `T6` duplicate rows and label conflicts
- `T7` temporal degradation
- `T8` leak-column, post-outcome feature, and entity-aggregate review
- `T9` amount cardinality sanity
- `T10` label-noise plausibility

Primary result:

- AI Hub FDS Card: `FAIL`
- AI Hub FDS Electronic Financial Network: `FAIL`

## Completed Phase 2: External Anchors

Executed anchors:

- ULB Credit Card Fraud: `WARN`
- BAF Base: `WARN`

These anchors show a middle register: the protocol does not simply fail every
public fraud dataset, but the recall-weighted T2 shortcut check can still flag
broad single-value effects.

Access-limited targets:

- IEEE-CIS Fraud Detection: Kaggle API returned `403`
- PaySim: Kaggle API returned `403`

## Completed Engineering Fixture: K-Claims-Synth

Implemented:

- deterministic generator: `k_claims_synth.py`
- observed investigation label: `observed_fraud_label`
- held-out scoring label: `oracle_fraud_label`
- train, validation, temporal, and entity-holdout split files
- self-application gate through `configs/k_claims_synth.json`
- versioned fixture learnability thresholds: `k_claims_fixture_acceptance.json`
- LightGBM checks on validation, temporal, and provider-holdout splits
- pre-observation unlabeled history for mature rolling features

Primary result:

- K-Claims-Synth v0.3 validity audit: `PASS`
- K-Claims-Synth v0.3 fixture acceptance: `PASS`

These results validate test wiring, not fidelity to Korean insurance claims.
The next workstream is the label-honest evaluation design in
`INSURANCE_FDS_PREPARATION.md`.

## Repository Outputs

- `fdvh.py`: audit runner
- `thresholds.yaml`: versioned thresholds
- `reference_model.yaml`: stdlib reference-model parameters
- `k_claims_fixture_acceptance.json`: fixture learnability and robustness thresholds
- `configs/`: dataset configs
- `reports/`: generated case-study and anchor reports
- `PROTOCOL.md`: test definitions
- `RESULT_SUMMARY.md`: AI Hub case-study summary
- `ANCHOR_COMPARISON.md`: cross-dataset result table
- `MODEL_PACKAGE_AUDIT.md`: reference-model audit notes
- `K_CLAIMS_SYNTH_DESIGN.md`: insurance test-fixture design and limits
- `INSURANCE_FDS_PREPARATION.md`: internal insurance FDS rebuild preparation
- `IMPLEMENTATION_STATUS.md`: requirement-by-requirement completion map
