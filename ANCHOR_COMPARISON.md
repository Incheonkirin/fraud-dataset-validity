# Anchor Comparison

Run date: 2026-07-11 KST

Thresholds: `thresholds.yaml`

Reference model: `reference_model.yaml`

Sensitivity model: `lightgbm_sensitivity.json`

| dataset | source | verdict | rows | fraud rate | amount ROC-AUC | LGBM amount/no-ID AP ratio | T2 | zero-fraud low region | amount distinct | top-10 share |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AI Hub FDS Card | AI Hub | FAIL | 1,952,871 | 3.69% | 0.9519 | 0.6683 | FAIL | none | 1,931 | 86.01% |
| AI Hub FDS Electronic Financial Network | AI Hub | FAIL | 4,434,106 | 0.39% | 0.9969 | 0.7466 | FAIL | 98.97% | 48 | 98.05% |
| ULB Credit Card Fraud | Kaggle / ULB | WARN | 284,807 | 0.17% | 0.7196 | 0.0033 | WARN | none | 32,767 | 16.29% |
| BAF Base | Kaggle / BAF | WARN | 1,000,000 | 1.10% | 0.5939 | 0.1001 | WARN | 0.02% | 994,971 | 0.00% |
| K-Claims-Synth v0.3 | local synthetic generator | PASS | 100,000 | 3.27% | 0.4940 | 0.1905 | PASS | none | 99,212 | 0.11% |

## Interpretation

The protocol now shows a graded spectrum rather than a binary curated pattern:

- `K-Claims-Synth v0.3` passes both shortcut validity and a separate learnability
  gate after adding observable multi-feature interactions and mature prior-only
  rolling histories.
- ULB and BAF warn on broad single-feature shortcuts, but do not fail the amount,
  overlap, temporal, duplicate, leakage, or cardinality gates.
- AI Hub Card retains split-integrity, marginal amount ROC-AUC, and
  recall-weighted shortcut failures after the LightGBM ratio gates pass.
- AI Hub Electronic Financial Network retains split-integrity, amount ROC-AUC,
  recall-weighted shortcut, class-overlap, zero-fraud region, and amount-template
  failures after the LightGBM ratio gates pass.

## Access Notes

- ULB and BAF were downloaded through Kaggle CLI with local credentials.
- IEEE-CIS and PaySim downloads returned Kaggle API `403` in this environment,
  so they are not counted as executed anchors in this comparison.
