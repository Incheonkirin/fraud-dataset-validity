# K-Claims-Synth v0.2 LightGBM Sensitivity

This analysis replaces the stdlib reference denominator with a frozen LightGBM model.
It is a sensitivity check, not a tuned leaderboard model.

## Sample

- Train: 52,231 / 52,231 rows (677 positives)
- Evaluation: 15,071 / 15,071 rows (226 positives)
- Method: `deterministic_systematic`

## Results

| model/check | ROC-AUC | PR-AUC | best F1 | status |
|---|---:|---:|---:|---:|
| LightGBM no-ID | 0.5599 | 0.0250 | 0.0515 | reference |
| LightGBM amount-only | 0.5093 | 0.0154 | 0.0316 | reference |
| T1.2 amount/no-ID AP ratio |  | 0.6162 |  | PASS |
| T1.3 fixed amount rule/no-ID F1 ratio |  |  | 0.5103 | PASS |

## Robustness

- Independent full-audit FAIL gates: none
- Dataset FAIL survives T1.2/T1.3 changes: **FALSE**
