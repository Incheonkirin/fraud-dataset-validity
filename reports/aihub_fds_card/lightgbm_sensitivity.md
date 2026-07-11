# AI Hub FDS - Card Transactions LightGBM Sensitivity

This analysis replaces the stdlib reference denominator with a frozen LightGBM model.
It is a sensitivity check, not a tuned leaderboard model.

## Sample

- Train: 300,000 / 1,735,885 rows (10,992 positives)
- Evaluation: 150,000 / 216,986 rows (5,445 positives)
- Method: `deterministic_systematic`

## Results

| model/check | ROC-AUC | PR-AUC | best F1 | status |
|---|---:|---:|---:|---:|
| LightGBM no-ID | 0.9998 | 0.9935 | 0.9608 | reference |
| LightGBM amount-only | 0.9563 | 0.6640 | 0.7148 | reference |
| T1.2 amount/no-ID AP ratio |  | 0.6683 |  | PASS |
| T1.3 fixed amount rule/no-ID F1 ratio |  |  | 0.7498 | PASS |

## Robustness

- Independent full-audit FAIL gates: T0.1, T1.1, T2
- Dataset FAIL survives T1.2/T1.3 changes: **TRUE**
