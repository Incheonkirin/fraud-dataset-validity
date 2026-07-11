# AI Hub FDS - Electronic Financial Network LightGBM Sensitivity

This analysis replaces the stdlib reference denominator with a frozen LightGBM model.
It is a sensitivity check, not a tuned leaderboard model.

## Sample

- Train: 300,000 / 3,941,428 rows (1,167 positives)
- Evaluation: 150,000 / 492,678 rows (584 positives)
- Method: `deterministic_systematic`

## Results

| model/check | ROC-AUC | PR-AUC | best F1 | status |
|---|---:|---:|---:|---:|
| LightGBM no-ID | 0.9982 | 0.6161 | 0.6147 | reference |
| LightGBM amount-only | 0.9972 | 0.4600 | 0.5540 | reference |
| T1.2 amount/no-ID AP ratio |  | 0.7466 |  | PASS |
| T1.3 fixed amount rule/no-ID F1 ratio |  |  | 0.9095 | PASS |

## Robustness

- Independent full-audit FAIL gates: T0.1, T1.1, T2, T3, T5, T9.1, T9.2
- Dataset FAIL survives T1.2/T1.3 changes: **TRUE**
