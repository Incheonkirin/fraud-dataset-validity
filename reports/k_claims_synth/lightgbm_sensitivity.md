# K-Claims-Synth v0.3 LightGBM Sensitivity

This analysis replaces the stdlib reference denominator with a frozen LightGBM model.
It is a sensitivity check, not a tuned leaderboard model.

## Sample

- Train: 52,150 / 52,150 rows (1,079 positives)
- Evaluation: 15,038 / 15,038 rows (469 positives)
- Method: `deterministic_systematic`

## Results

| model/check | ROC-AUC | PR-AUC | best F1 | status |
|---|---:|---:|---:|---:|
| LightGBM no-ID | 0.7463 | 0.1748 | 0.2573 | reference |
| LightGBM amount-only | 0.5165 | 0.0334 | 0.0636 | reference |
| T1.2 amount/no-ID AP ratio |  | 0.1913 |  | PASS |
| T1.3 fixed amount rule/no-ID F1 ratio |  |  | 0.2304 | PASS |

## Split Robustness

| split | rows | prevalence | no-ID ROC-AUC | no-ID PR-AUC | AP lift |
|---|---:|---:|---:|---:|---:|
| valid | 15,038 | 0.0312 | 0.7463 | 0.1748 | 5.6064 |
| test_temporal | 22,651 | 0.0391 | 0.7440 | 0.1718 | 4.3930 |
| test_entity_holdout | 10,161 | 0.0321 | 0.7509 | 0.1485 | 4.6294 |

## Robustness

- Independent full-audit FAIL gates: none
- Dataset FAIL survives T1.2/T1.3 changes: **FALSE**
