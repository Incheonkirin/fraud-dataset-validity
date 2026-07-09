# Anchor Comparison

Run date: 2026-07-09 KST

Thresholds: `thresholds.yaml`

| dataset | source | verdict | rows | fraud rate | amount-only ROC-AUC | zero-fraud low-amount region | amount distinct count | top-10 amount share | oracle label? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AI Hub FDS Card | AI Hub | FAIL | 1,952,871 | 3.69% | 0.9519 | none | 1,931 | 86.01% | no |
| AI Hub FDS Electronic Financial Network | AI Hub | FAIL | 4,434,106 | 0.39% | 0.9969 | 98.97% | 48 | 98.05% | no |
| ULB Credit Card Fraud | Kaggle / ULB | PASS | 284,807 | 0.17% | 0.7196 | none | 32,767 | 16.29% | no |
| BAF Base | Kaggle / BAF | PASS | 1,000,000 | 1.10% | 0.5939 | 0.02% | 994,971 | 0.00% | no |
| K-Claims-Synth v0.1 | local synthetic generator | PASS | 100,000 | 2.63% | 0.5119 | 0.09% | 99,191 | 0.10% | yes |

## Interpretation

The protocol does not fail every fraud dataset. ULB Credit Card Fraud and BAF
Base pass the implemented gates, while the two AI Hub FDS subsets fail for
specific, reproducible reasons:

- AI Hub Card fails amount-only and single-feature shortcut checks.
- AI Hub Electronic Financial Network fails amount-only, overlap, zero-fraud
  region, and amount-cardinality checks.
- K-Claims-Synth passes the same gates while exposing both observed and oracle
  labels for label-noise evaluation.

## Access Notes

- ULB and BAF were downloaded through Kaggle CLI with local credentials.
- IEEE-CIS and PaySim downloads returned Kaggle API `403` in this environment,
  so they are not counted as executed anchors in this comparison.
