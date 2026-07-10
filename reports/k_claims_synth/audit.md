# K-Claims-Synth v0.2 Validity Audit

Verdict: **PASS**

## Overview

- Rows: 100,000
- Positives: 1,753 (1.75%)
- Duplicate full rows: 0
- Duplicate rows excluding label: 0
- Label-conflict rows excluding label: 0

## Reference Model

- Type: `evidence_naive_bayes`
- Alpha: 1
- Weight clip: 4

## Label Alignment

- Observed label: `observed_fraud_label`
- Oracle label: `oracle_fraud_label`
- Noise rate: 1.05%
- Observed positives: 1,328 (1.33%)
- Oracle positives: 1,753 (1.75%)

## Test Verdicts

| test | status | metric | threshold | details |
|---|---:|---:|---:|---|
| T0 Evaluation integrity | INFO |  |  | No published evaluation metadata was provided in the config. |
| T1.1 Amount-only ROC-AUC | PASS | 0.5387 | >= 0.95 | Amount-only baseline is evaluated on the provided split. |
| T1.2 Amount-only share of no-ID PR-AUC | PASS | 0.5924 | >= 0.8 | Compares amount-only average precision to the no-ID baseline. |
| T1.3 Best one-sided amount threshold | PASS | {'f1': 0.03976529190763645, 'f1_ratio': 0.6102442873518056} | F1 >= 0.7 and ratio >= 0.8 | Best threshold rule: claim_amount: amount >= 53006.1; ratio compares against the no-ID baseline's best score-threshold F1. |
| T2 Single-feature shortcut | PASS | {'column': 'hospital_days', 'value': '12', 'count': 123, 'positive_rate': 0.0975609756097561, 'recall': 0.0068454078722190535, 'lift': 5.565372253836628} | below warning gates | Strongest checked non-ID value: hospital_days=12 has positive_rate 9.8%, lift 5.6x, recall 0.7% (n=123). |
| T3 Class distribution overlap | PASS | 0.8957 | > 0.2 | Lowest checked overlap is 0.8957 on policy_age_days. |
| T4.1 ID-only baseline | PASS | {'ap_ratio': 0.5407850046053172, 'ap_lift': 0.9983341014901134} | ratio/lift below warning pair | Compares ID-only AP to no-ID AP and fraud prevalence. |
| T4.2 Entity-holdout degradation | PASS | {'ap_lift_ratio': 1.160254649690694, 'raw_ap_ratio': 1.401892894081572, 'provided_prevalence': 0.014995687081149227, 'holdout_prevalence': 0.018118735543562067} | > 0.75 | Compares prevalence-normalized AP-lift on entity holdout against the provided split. |
| T5 Zero-fraud low-amount region | PASS |  |  | No zero-positive low-amount region was found. |
| T6.1 Duplicate feature rows | PASS | 0 | < 0.01 | Duplicate rows excluding the label: 0. |
| T6.2 Label conflicts for identical features | PASS | 0 | = 0.0 | Rows in duplicate feature groups with mixed labels: 0. |
| T7 Temporal split degradation | PASS | {'ap_lift_ratio': 1.0171945756782643, 'raw_ap_ratio': 0.948705950247362, 'provided_prevalence': 0.014995687081149227, 'temporal_prevalence': 0.013986013986013986} | > 0.75 | Compares prevalence-normalized AP-lift on temporal holdout against the provided split. |
| T8.1 Configured leak-column exclusion | PASS |  |  | Configured label/leak columns are excluded from features. |
| T8.2 Suspicious feature names | PASS |  |  | No suspicious label/post-outcome feature names were found. |
| T8.3 Entity aggregate feature names | PASS |  |  | No entity-level aggregate rate/risk/score feature names were found. |
| T9.1 Amount distinct-value count | PASS | 99227 | <= 100 | claim_amount has 99,227 distinct amount values. |
| T9.2 Amount top-10 concentration | PASS | 0.00114 | < 0.7 | Top 10 claim_amount values cover 0.11% of rows. |
| T9.3 Round-amount concentration | PASS | 0 | >= 0.95 | claim_amount values are multiples of 1,000 for 0.00% of rows. |
| T10 Label-noise plausibility | PASS | 0.01047 | 0.01..0.3 | Compares observed investigation labels against oracle labels. |

## Time Coverage

| year | rows | prevalence |
|---|---:|---:|
| 2024 | 49,998 | 1.69% |
| 2025 | 50,002 | 1.81% |

## Amount Profiles

- customer_age: distinct 71, p50 45, p95 70, p99 80, max 88, top10 share 28.59%, round(1000) share 0.00%
- provider_prior_claim_count_365d: distinct 111, p50 61, p95 82, p99 89, max 110, top10 share 25.75%, round(1000) share 0.71%
- prior_claim_count_365d: distinct 19, p50 7, p95 13, p99 16, max 18, top10 share 81.28%, round(1000) share 2.42%
- provider_prior_high_amount_share_365d: distinct 829, p50 0.125, p95 0.2222, p99 0.3333, max 1, top10 share 20.42%, round(1000) share 5.44%
- claim_amount: distinct 99,227, p50 25,086, p95 123,087, p99 238,912, max 1,591,568, top10 share 0.11%, round(1000) share 0.00%
- policy_age_days: distinct 3,254, p50 430, p95 1,871, p99 2,826, max 3,650, top10 share 1.99%, round(1000) share 0.03%
- hospital_days: distinct 25, p50 1, p95 6, p99 9, max 24, top10 share 99.05%, round(1000) share 42.18%
- prior_claim_count_30d: distinct 8, p50 1, p95 2, p99 3, max 7, top10 share 100.00%, round(1000) share 48.20%

## Single-Feature Shortcuts

| column | value | n | pos rate | lift | recall |
|---|---|---:|---:|---:|---:|
| hospital_days | 12 | 123 | 9.76% | 5.565x | 0.68% |
| hospital_days | 11 | 193 | 8.81% | 5.025x | 0.97% |
| policy_age_days | 7 | 153 | 6.54% | 3.728x | 0.57% |
| claim_date | 2025-11-04 | 124 | 6.45% | 3.68x | 0.46% |
| accident_date | 2024-01-06 | 126 | 6.35% | 3.622x | 0.46% |
| accident_date | 2025-04-25 | 129 | 6.20% | 3.538x | 0.46% |
| policy_age_days | 74 | 129 | 6.20% | 3.538x | 0.46% |
| accident_date | 2024-02-09 | 113 | 6.19% | 3.534x | 0.40% |
| policy_age_days | 97 | 133 | 6.02% | 3.431x | 0.46% |
| accident_date | 2025-08-21 | 150 | 6.00% | 3.423x | 0.51% |
| claim_date | 2024-11-21 | 121 | 5.79% | 3.3x | 0.40% |
| claim_date | 2025-03-29 | 125 | 5.60% | 3.195x | 0.40% |

## Amount Threshold Rules

- claim_amount best_high_threshold: `amount >= 53006.1`, P=2.15%, R=26.87%, F1=0.03977
- claim_amount best_low_threshold: `amount <= 639822`, P=1.75%, R=100.00%, F1=0.03447

## Baselines

- provided_split_no_id_nb: ROC-AUC 0.5502, PR-AUC 0.02768, Best F1 0.06516, Top 1% P=6.62%, R=4.42%
- provided_split_id_only_nb: ROC-AUC 0.4938, PR-AUC 0.01497, Best F1 0.0298, Top 1% P=1.99%, R=1.33%
- provided_split_with_id_nb: ROC-AUC 0.5386, PR-AUC 0.02523, Best F1 0.06731, Top 1% P=5.96%, R=3.98%
- provided_split_amount_only_nb: ROC-AUC 0.5387, PR-AUC 0.0164, Best F1 0.03489, Top 1% P=0.66%, R=0.44%
- temporal_holdout_no_id_nb: ROC-AUC 0.617, PR-AUC 0.02626, Best F1 0.06061, Top 1% P=0.00%, R=0.00%
- temporal_holdout_amount_only_nb: ROC-AUC 0.4574, PR-AUC 0.01965, Best F1 0.04082, Top 1% P=0.00%, R=0.00%
- entity_holdout_no_id_nb: ROC-AUC 0.5892, PR-AUC 0.03881, Best F1 0.08491, Top 1% P=9.34%, R=5.17%
- entity_holdout_id_only_nb: ROC-AUC 0.5143, PR-AUC 0.01976, Best F1 0.04082, Top 1% P=2.75%, R=1.52%

## Split Drift

| column | JS divergence | id? |
|---|---:|---:|
| provider_id | 1.00000 | true |
| claim_id | 1.00000 | true |
| claim_amount | 0.99518 | false |
| policy_id | 0.21620 | true |
| customer_id | 0.09723 | true |
| policy_age_days | 0.05365 | false |
| provider_prior_high_amount_share_365d | 0.02331 | false |
| accident_date | 0.00946 | false |
| claim_date | 0.00925 | false |
| provider_prior_claim_count_365d | 0.00141 | false |

## Red Flags

- None.
