# ULB Credit Card Fraud LightGBM Sensitivity

This analysis replaces the stdlib reference denominator with a frozen LightGBM model.
It is a sensitivity check, not a tuned leaderboard model.

## Sample

- Train: 199,364 / 199,364 rows (384 positives)
- Evaluation: 85,443 / 85,443 rows (108 positives)
- Method: `deterministic_systematic`

## Results

| model/check | ROC-AUC | PR-AUC | best F1 | status |
|---|---:|---:|---:|---:|
| LightGBM no-ID | 0.8680 | 0.5028 | 0.6854 | reference |
| LightGBM amount-only | 0.5615 | 0.0016 | 0.0039 | reference |
| T1.2 amount/no-ID AP ratio |  | 0.0031 |  | PASS |
| T1.3 fixed amount rule/no-ID F1 ratio |  |  | 0.0474 | PASS |

## Split Robustness

| split | rows | prevalence | no-ID ROC-AUC | no-ID PR-AUC | AP lift |
|---|---:|---:|---:|---:|---:|
| valid | 85,443 | 0.0013 | 0.8680 | 0.5028 | 397.7633 |

## Robustness

- Independent full-audit FAIL gates: none
- Dataset FAIL survives T1.2/T1.3 changes: **FALSE**
