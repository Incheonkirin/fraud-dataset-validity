# BAF Base LightGBM Sensitivity

This analysis replaces the stdlib reference denominator with a frozen LightGBM model.
It is a sensitivity check, not a tuned leaderboard model.

## Sample

- Train: 300,000 / 794,989 rows (3,185 positives)
- Evaluation: 150,000 / 205,011 rows (2,093 positives)
- Method: `deterministic_systematic`

## Results

| model/check | ROC-AUC | PR-AUC | best F1 | status |
|---|---:|---:|---:|---:|
| LightGBM no-ID | 0.8807 | 0.1688 | 0.2503 | reference |
| LightGBM amount-only | 0.5802 | 0.0169 | 0.0341 | reference |
| T1.2 amount/no-ID AP ratio |  | 0.1001 |  | PASS |
| T1.3 fixed amount rule/no-ID F1 ratio |  |  | 0.1298 | PASS |

## Split Robustness

| split | rows | prevalence | no-ID ROC-AUC | no-ID PR-AUC | AP lift |
|---|---:|---:|---:|---:|---:|
| valid | 150,000 | 0.0140 | 0.8807 | 0.1688 | 12.0999 |

## Robustness

- Independent full-audit FAIL gates: none
- Dataset FAIL survives T1.2/T1.3 changes: **FALSE**
