# ULB Credit Card Fraud Validity Audit

Verdict: **PASS**

## Overview

- Rows: 284,807
- Positives: 492 (0.17%)
- Duplicate full rows: 0
- Duplicate rows excluding label: 0
- Label-conflict rows excluding label: 0

## Test Verdicts

| test | status | metric | threshold | details |
|---|---:|---:|---:|---|
| T0 Evaluation integrity | INFO |  |  | No published evaluation metadata was provided in the config. |
| T1.1 Amount-only ROC-AUC | PASS | 0.7196 | >= 0.95 | Amount-only baseline is evaluated on the provided split. |
| T1.2 Amount-only share of no-ID PR-AUC | PASS | 0.01447 | >= 0.8 | Compares amount-only average precision to the no-ID baseline. |
| T1.3 Best one-sided amount threshold | PASS | 0.02331 | >= 0.7 | Best threshold rule: Amount: amount <= 0. |
| T3 Class distribution overlap | PASS | 0.5945 | > 0.2 | Lowest checked overlap is 0.5945 on Amount. |
| T4.1 ID-only baseline | PASS | {'ap_ratio': 0.004796509816603542, 'ap_lift': 1.0323024773390896} | ratio/lift below warning pair | Compares ID-only AP to no-ID AP and fraud prevalence. |
| T4.2 Entity-holdout degradation | PASS | 2.015 | > 0.75 | Compares entity-holdout no-ID average precision to provided-split no-ID average precision. |
| T5 Zero-fraud low-amount region | PASS |  |  | No zero-positive low-amount region was found. |
| T6.1 Duplicate feature rows | PASS | 0 | < 0.01 | Duplicate rows excluding the label: 0. |
| T6.2 Label conflicts for identical features | PASS | 0 | = 0.0 | Rows in duplicate feature groups with mixed labels: 0. |
| T7 Temporal split degradation | PASS | 1.635 | > 0.75 | Compares temporal no-ID average precision to provided-split no-ID average precision. |
| T8.1 Configured leak-column exclusion | PASS |  |  | Configured label/leak columns are excluded from features. |
| T8.2 Suspicious feature names | PASS |  |  | No suspicious label/post-outcome feature names were found. |
| T9.1 Amount distinct-value count | PASS | 32767 | <= 100 | Amount has 32,767 distinct amount values. |
| T9.2 Amount top-10 concentration | PASS | 0.1629 | < 0.7 | Top 10 Amount values cover 16.29% of rows. |
| T9.3 Round-amount concentration | PASS | 0.006949 | >= 0.95 | Amount values are multiples of 1,000 for 0.69% of rows. |
| T10 Label-noise plausibility | INFO |  |  | No separate oracle label is configured; label-noise plausibility cannot be measured directly. |

## Time Coverage

| year | rows | prevalence |
|---|---:|---:|
| 2013 | 284,807 | 0.17% |

## Amount Profiles

- V28: distinct 275,663, p50 0.01124, p95 0.2561, p99 0.5411, max 33.85, top10 share 0.19%, round(1000) share 0.00%
- V22: distinct 275,663, p50 0.006782, p95 1.129, p99 1.53, max 10.5, top10 share 0.19%, round(1000) share 0.00%
- V2: distinct 275,663, p50 0.06549, p95 1.809, p99 3.802, max 22.06, top10 share 0.19%, round(1000) share 0.00%
- V19: distinct 275,663, p50 0.003735, p95 1.286, p99 2.263, max 5.592, top10 share 0.19%, round(1000) share 0.00%
- V24: distinct 275,663, p50 0.04098, p95 0.8664, p99 1.064, max 4.585, top10 share 0.19%, round(1000) share 0.00%
- V4: distinct 275,663, p50 -0.01985, p95 2.567, p99 4.248, max 16.88, top10 share 0.19%, round(1000) share 0.00%
- V14: distinct 275,663, p50 0.0506, p95 1.394, p99 2.15, max 10.53, top10 share 0.19%, round(1000) share 0.00%
- V18: distinct 275,663, p50 -0.003636, p95 1.394, p99 2.069, max 5.041, top10 share 0.19%, round(1000) share 0.00%
- V12: distinct 275,663, p50 0.14, p95 1.243, p99 1.699, max 7.848, top10 share 0.19%, round(1000) share 0.00%
- V17: distinct 275,663, p50 -0.06568, p95 1.275, p99 2.29, max 9.254, top10 share 0.19%, round(1000) share 0.00%
- V1: distinct 275,663, p50 0.01811, p95 2.081, p99 2.237, max 2.455, top10 share 0.19%, round(1000) share 0.00%
- V16: distinct 275,663, p50 0.06641, p95 1.325, p99 1.875, max 17.32, top10 share 0.19%, round(1000) share 0.00%
- V3: distinct 275,663, p50 0.1798, p95 2.063, p99 2.728, max 9.383, top10 share 0.19%, round(1000) share 0.00%
- V25: distinct 275,663, p50 0.01659, p95 0.7607, p99 1.204, max 7.52, top10 share 0.19%, round(1000) share 0.00%
- V21: distinct 275,663, p50 -0.02945, p95 0.5379, p99 1.932, max 27.2, top10 share 0.19%, round(1000) share 0.00%
- V11: distinct 275,663, p50 -0.03276, p95 1.614, p99 2.291, max 12.02, top10 share 0.19%, round(1000) share 0.00%
- V20: distinct 275,663, p50 -0.06248, p95 0.8362, p99 2.412, max 39.42, top10 share 0.19%, round(1000) share 0.00%
- Amount: distinct 32,767, p50 22, p95 365, p99 1,018, max 25,691, top10 share 16.29%, round(1000) share 0.69%
- V6: distinct 275,663, p50 -0.2742, p95 3.16, p99 4.2, max 73.3, top10 share 0.19%, round(1000) share 0.00%
- V26: distinct 275,663, p50 -0.05214, p95 0.9209, p99 1.159, max 3.517, top10 share 0.19%, round(1000) share 0.00%
- V23: distinct 275,663, p50 -0.01119, p95 0.488, p99 1.509, max 22.53, top10 share 0.19%, round(1000) share 0.00%
- V7: distinct 275,663, p50 0.0401, p95 1.408, p99 2.696, max 120.6, top10 share 0.19%, round(1000) share 0.00%
- V13: distinct 275,663, p50 -0.01357, p95 1.608, p99 2.514, max 7.127, top10 share 0.19%, round(1000) share 0.00%
- V10: distinct 275,663, p50 -0.09292, p95 1.549, p99 3.254, max 23.75, top10 share 0.19%, round(1000) share 0.00%
- Time: distinct 124,592, p50 84,692, p95 164,144, p99 170,561, max 172,792, top10 share 0.08%, round(1000) share 0.09%
- V5: distinct 275,663, p50 -0.05434, p95 2.099, p99 3.425, max 34.8, top10 share 0.19%, round(1000) share 0.00%
- V9: distinct 275,663, p50 -0.05143, p95 1.781, p99 2.987, max 15.59, top10 share 0.19%, round(1000) share 0.00%
- V8: distinct 275,663, p50 0.02236, p95 1.05, p99 2.076, max 20.01, top10 share 0.19%, round(1000) share 0.00%
- V27: distinct 275,663, p50 0.001342, p95 0.3877, p99 0.9314, max 31.61, top10 share 0.19%, round(1000) share 0.00%
- V15: distinct 275,663, p50 0.04807, p95 1.373, p99 1.926, max 8.878, top10 share 0.19%, round(1000) share 0.00%

## Single-Feature Shortcuts

| column | value | n | pos rate | lift | recall |
|---|---|---:|---:|---:|---:|
| Amount | 99.99 | 330 | 8.18% | 47.36x | 5.49% |
| Amount | 3.79 | 191 | 2.09% | 12.12x | 0.81% |
| Amount | 18.96 | 114 | 1.75% | 10.16x | 0.41% |
| Amount | 7.59 | 115 | 1.74% | 10.07x | 0.41% |
| Amount | 0 | 1,825 | 1.48% | 8.564x | 5.49% |
| Amount | 78 | 147 | 1.36% | 7.876x | 0.41% |
| Amount | 3.76 | 104 | 0.96% | 5.566x | 0.20% |
| Amount | 1.52 | 213 | 0.94% | 5.435x | 0.41% |
| Amount | 4.56 | 112 | 0.89% | 5.169x | 0.20% |
| Amount | 4.9 | 115 | 0.87% | 5.034x | 0.20% |
| Amount | 1.18 | 362 | 0.83% | 4.797x | 0.61% |
| Amount | 1 | 13,688 | 0.83% | 4.779x | 22.97% |

## Amount Threshold Rules

- Amount best_high_threshold: `amount >= 717.15`, P=0.43%, R=4.67%, F1=0.007883
- Amount best_low_threshold: `amount <= 0`, P=1.48%, R=5.49%, F1=0.02331

## Baselines

- provided_split_no_id_nb: ROC-AUC 0.9656, PR-AUC 0.272, Top 1% P=10.07%, R=79.63%
- provided_split_id_only_nb: ROC-AUC 0.5, PR-AUC 0.001305, Top 1% P=0.12%, R=0.93%
- provided_split_with_id_nb: ROC-AUC 0.9656, PR-AUC 0.272, Top 1% P=10.07%, R=79.63%
- provided_split_amount_only_nb: ROC-AUC 0.7196, PR-AUC 0.003938, Top 1% P=1.17%, R=9.26%
- temporal_holdout_no_id_nb: ROC-AUC 0.9715, PR-AUC 0.4447, Top 1% P=12.36%, R=81.99%
- temporal_holdout_amount_only_nb: ROC-AUC 0.6728, PR-AUC 0.00413, Top 1% P=0.86%, R=5.69%
- entity_holdout_no_id_nb: ROC-AUC 0.9696, PR-AUC 0.5482, Top 1% P=12.87%, R=79.35%
- entity_holdout_id_only_nb: ROC-AUC 0.5, PR-AUC 0.002265, Top 1% P=0.00%, R=0.00%

## Split Drift

| column | JS divergence | id? |
|---|---:|---:|
| Time | 1.00000 | false |
| transaction_id | 1.00000 | true |
| V20 | 0.99009 | false |
| V21 | 0.99009 | false |
| V3 | 0.99009 | false |
| V10 | 0.99009 | false |
| V8 | 0.99009 | false |
| V19 | 0.99009 | false |
| V15 | 0.99009 | false |
| V13 | 0.99009 | false |

## Red Flags

- None.
