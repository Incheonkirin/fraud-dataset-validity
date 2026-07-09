# Project Plan

## Problem Statement

Public fraud datasets are often validated by training a model and reporting a
score. That is not enough. A dataset can produce high model scores when the
label is recoverable from amount buckets, category codes, entity IDs, or weak
split design.

This project defines a small protocol for testing those failure modes before
model comparisons begin.

## v0.1: Failed Case Study

Status: implemented.

Scope:

- implement `T0`, `T1`, `T2`, `T5`, and `T9`
- run the protocol on the AI Hub FDS card subset
- run the protocol on the AI Hub FDS electronic financial network subset
- publish Markdown and JSON reports

Primary result:

- both subsets fail as fraud-detection benchmarks

## v0.2: External Anchors

Goal:

- run the same harness on external datasets so the protocol is not tied to one
  failed case study

Targets:

- BAF / Bank Account Fraud
- PaySim
- IEEE-CIS Fraud Detection
- ULB Credit Card Fraud

Output:

- comparison table across datasets
- threshold revisions, if needed
- notes on which tests discriminate cleanly and which are too broad

## v0.3: Insurance Benchmark Design

Goal:

- build `K-Claims-Synth`, an insurance-claim fraud benchmark that passes the
  protocol before release

Key requirements:

- noisy observed investigation label
- held-out oracle label for scoring
- normal/fraud overlap on single features
- temporal and entity-holdout splits
- fraud mechanisms based on combinations of timing, behavior, provider pattern,
  and claim history

## Repository Outputs

- `fdvh.py`: audit runner
- `thresholds.yaml`: versioned thresholds
- `configs/`: dataset configs
- `reports/`: generated case-study reports
- `PROTOCOL.md`: test definitions
- `RESULT_SUMMARY.md`: case-study summary
- `MODEL_PACKAGE_AUDIT.md`: reference-model audit notes
- `K_CLAIMS_SYNTH_DESIGN.md`: synthetic insurance benchmark design
