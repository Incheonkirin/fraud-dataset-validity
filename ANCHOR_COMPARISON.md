# Anchor Comparison

Run date: 2026-07-10 KST

Thresholds: `thresholds.yaml`

Reference model: `reference_model.yaml`

| dataset | source | verdict | rows | fraud rate | amount-only ROC-AUC | T2 shortcut status | zero-fraud low-amount region | amount distinct count | top-10 amount share | oracle label? |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AI Hub FDS Card | AI Hub | FAIL | 1,952,871 | 3.69% | 0.9519 | FAIL | none | 1,931 | 86.01% | no |
| AI Hub FDS Electronic Financial Network | AI Hub | FAIL | 4,434,106 | 0.39% | 0.9969 | FAIL | 98.97% | 48 | 98.05% | no |
| ULB Credit Card Fraud | Kaggle / ULB | WARN | 284,807 | 0.17% | 0.7196 | WARN | none | 32,767 | 16.29% | no |
| BAF Base | Kaggle / BAF | WARN | 1,000,000 | 1.10% | 0.5939 | WARN | 0.02% | 994,971 | 0.00% | no |
| K-Claims-Synth v0.2 | local synthetic generator | PASS | 100,000 | 1.75% | 0.5387 | PASS | none | 99,227 | 0.11% | yes |

## Interpretation

The protocol now shows a graded spectrum rather than a binary curated pattern:

- `K-Claims-Synth v0.2` passes after removing the provider-rate quasi-leak,
  switching the entity holdout to providers, and flipping label noise toward
  high false negatives with low false positives.
- ULB and BAF warn on broad single-feature shortcuts, but do not fail the amount,
  overlap, temporal, duplicate, leakage, or cardinality gates.
- AI Hub Card fails on split integrity, amount-only baselines, amount threshold
  F1, recall-weighted single-feature shortcuts, and amount concentration.
- AI Hub Electronic Financial Network fails on split integrity, amount-only
  baselines, recall-weighted single-feature shortcuts, class-overlap collapse,
  zero-fraud low-amount coverage, duplicate rows, and amount cardinality.

## Access Notes

- ULB and BAF were downloaded through Kaggle CLI with local credentials.
- IEEE-CIS and PaySim downloads returned Kaggle API `403` in this environment,
  so they are not counted as executed anchors in this comparison.
