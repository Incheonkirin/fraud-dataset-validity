# K-Claims-Synth v0.1 Validity Audit

Verdict: **PASS**

## Overview

- Rows: 100,000
- Positives: 2,628 (2.63%)
- Duplicate full rows: 0
- Duplicate rows excluding label: 0
- Label-conflict rows excluding label: 0

## Label Alignment

- Observed label: `observed_fraud_label`
- Oracle label: `oracle_fraud_label`
- Noise rate: 2.15%
- Observed positives: 4,090 (4.09%)
- Oracle positives: 2,628 (2.63%)

## Test Verdicts

| test | status | metric | threshold | details |
|---|---:|---:|---:|---|
| T0 Evaluation integrity | INFO |  |  | No published evaluation metadata was provided in the config. |
| T1.1 Amount-only ROC-AUC | PASS | 0.5119 | >= 0.95 | Amount-only baseline is evaluated on the provided split. |
| T1.2 Amount-only share of no-ID PR-AUC | PASS | 0.7156 | >= 0.8 | Compares amount-only average precision to the no-ID baseline. |
| T1.3 Best one-sided amount threshold | PASS | 0.05441 | >= 0.7 | Best threshold rule: claim_amount: amount >= 31156.6. |
| T3 Class distribution overlap | PASS | 0.8133 | > 0.2 | Lowest checked overlap is 0.8133 on prior_claim_count_30d. |
| T4.1 ID-only baseline | PASS | {'ap_ratio': 0.6383374540291692, 'ap_lift': 0.9628640295308004} | ratio/lift below warning pair | Compares ID-only AP to no-ID AP and fraud prevalence. |
| T4.2 Entity-holdout degradation | PASS | 1.055 | > 0.75 | Compares entity-holdout no-ID average precision to provided-split no-ID average precision. |
| T5 Zero-fraud low-amount region | PASS | 0.00094 | < 0.5 | claim_amount <= 1,257 covers 94 rows with zero positives. |
| T6.1 Duplicate feature rows | PASS | 0 | < 0.01 | Duplicate rows excluding the label: 0. |
| T6.2 Label conflicts for identical features | PASS | 0 | = 0.0 | Rows in duplicate feature groups with mixed labels: 0. |
| T7 Temporal split degradation | PASS | 1.031 | > 0.75 | Compares temporal no-ID average precision to provided-split no-ID average precision. |
| T8.1 Configured leak-column exclusion | PASS |  |  | Configured label/leak columns are excluded from features. |
| T8.2 Suspicious feature names | PASS |  |  | No suspicious label/post-outcome feature names were found. |
| T9.1 Amount distinct-value count | PASS | 99191 | <= 100 | claim_amount has 99,191 distinct amount values. |
| T9.2 Amount top-10 concentration | PASS | 0.00101 | < 0.7 | Top 10 claim_amount values cover 0.10% of rows. |
| T9.3 Round-amount concentration | PASS | 0 | >= 0.95 | claim_amount values are multiples of 1,000 for 0.00% of rows. |
| T10 Label-noise plausibility | PASS | 0.02152 | 0.01..0.3 | Compares observed investigation labels against oracle labels. |

## Time Coverage

| year | rows | prevalence |
|---|---:|---:|
| 2024 | 50,030 | 2.84% |
| 2025 | 49,970 | 2.42% |

## Amount Profiles

- provider_claim_rate: distinct 10,521, p50 0.05171, p95 0.093, p99 0.1163, max 0.144, top10 share 0.33%, round(1000) share 0.00%
- claim_amount: distinct 99,191, p50 25,182, p95 124,108, p99 237,324, max 1,047,166, top10 share 0.10%, round(1000) share 0.00%
- hospital_days: distinct 30, p50 1, p95 6, p99 10, max 30, top10 share 98.65%, round(1000) share 41.00%
- customer_age: distinct 71, p50 46, p95 70, p99 81, max 88, top10 share 27.90%, round(1000) share 0.00%
- prior_claim_count_365d: distinct 19, p50 7, p95 18, p99 18, max 18, top10 share 66.93%, round(1000) share 2.88%
- prior_claim_count_30d: distinct 31, p50 4, p95 14, p99 19, max 31, top10 share 83.51%, round(1000) share 15.85%
- policy_age_days: distinct 3,237, p50 432, p95 1,848, p99 2,799, max 3,650, top10 share 1.96%, round(1000) share 0.04%

## Single-Feature Shortcuts

| column | value | n | pos rate | lift | recall |
|---|---|---:|---:|---:|---:|
| hospital_days | 13 | 138 | 14.49% | 5.515x | 0.76% |
| hospital_days | 12 | 223 | 10.76% | 4.095x | 0.91% |
| hospital_days | 11 | 264 | 9.85% | 3.748x | 0.99% |
| accident_date | 2024-04-11 | 111 | 9.01% | 3.428x | 0.38% |
| policy_age_days | 54 | 142 | 7.75% | 2.948x | 0.42% |
| claim_date | 2024-08-21 | 143 | 7.69% | 2.927x | 0.42% |
| policy_age_days | 218 | 119 | 7.56% | 2.878x | 0.34% |
| claim_date | 2024-11-17 | 135 | 7.41% | 2.819x | 0.38% |
| policy_age_days | 57 | 149 | 7.38% | 2.809x | 0.42% |
| claim_date | 2025-01-07 | 139 | 7.19% | 2.738x | 0.38% |
| policy_age_days | 93 | 153 | 7.19% | 2.736x | 0.42% |
| policy_age_days | 52 | 169 | 7.10% | 2.702x | 0.46% |

## Amount Threshold Rules

- claim_amount: zero-positive low region `claim_amount <= 1,257` covers 94 rows (0.09%).
- claim_amount best_high_threshold: `amount >= 31156.6`, P=2.89%, R=45.47%, F1=0.05441
- claim_amount best_low_threshold: `amount <= 409270`, P=2.63%, R=99.85%, F1=0.05123

## Baselines

- provided_split_no_id_nb: ROC-AUC 0.5986, PR-AUC 0.03851, Top 1% P=8.05%, R=3.16%
- provided_split_id_only_nb: ROC-AUC 0.4797, PR-AUC 0.02458, Top 1% P=1.34%, R=0.53%
- provided_split_with_id_nb: ROC-AUC 0.5513, PR-AUC 0.0317, Top 1% P=3.36%, R=1.32%
- provided_split_amount_only_nb: ROC-AUC 0.5119, PR-AUC 0.02756, Top 1% P=2.68%, R=1.05%
- temporal_holdout_no_id_nb: ROC-AUC 0.6459, PR-AUC 0.03972, Top 1% P=6.40%, R=2.65%
- temporal_holdout_amount_only_nb: ROC-AUC 0.5096, PR-AUC 0.02458, Top 1% P=2.80%, R=1.16%
- entity_holdout_no_id_nb: ROC-AUC 0.6296, PR-AUC 0.04063, Top 1% P=5.50%, R=2.05%
- entity_holdout_id_only_nb: ROC-AUC 0.5226, PR-AUC 0.02875, Top 1% P=2.50%, R=0.93%

## Split Drift

| column | JS divergence | id? |
|---|---:|---:|
| claim_id | 1.00000 | true |
| customer_id | 1.00000 | true |
| claim_amount | 0.99567 | false |
| policy_id | 0.21824 | true |
| provider_claim_rate | 0.18494 | false |
| policy_age_days | 0.05380 | false |
| customer_age | 0.01740 | false |
| provider_id | 0.01079 | true |
| claim_date | 0.00957 | false |
| accident_date | 0.00948 | false |

## Red Flags

- None.
