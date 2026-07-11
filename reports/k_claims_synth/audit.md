# K-Claims-Synth v0.3 Validity Audit

Verdict: **PASS**

## Overview

- Rows: 100,000
- Positives: 3,274 (3.27%)
- Duplicate full rows: 0
- Duplicate rows excluding label and IDs: 0
- Label-conflict rows excluding label and IDs: 0

## Reference Model

- Type: `evidence_naive_bayes`
- Alpha: 1
- Weight clip: 4
- Ratio gates screening-only: true

## Label Alignment

- Observed label: `observed_fraud_label`
- Oracle label: `oracle_fraud_label`
- Noise rate: 1.49%
- Observed positives: 2,220 (2.22%)
- Oracle positives: 3,274 (3.27%)

## Test Verdicts

| test | status | metric | threshold | details |
|---|---:|---:|---:|---|
| T0 Evaluation integrity | INFO |  |  | No published evaluation metadata was provided in the config. |
| T1.1 Amount-only ROC-AUC | PASS | 0.494 | >= 0.95 | Amount-only baseline is evaluated on the provided split. |
| T1.2 Amount-only share of no-ID PR-AUC | PASS | 0.1654 | >= 0.8 | Compares amount-only average precision to the no-ID baseline. This dependency-free ratio is screening-only; confirm it with the optional LightGBM sensitivity model. |
| T1.3 Best one-sided amount threshold | PASS | {'f1': 0.059271455031899574, 'f1_ratio': 0.22626642754241028} | F1 >= 0.7 and ratio >= 0.8 | Training-selected threshold rule: claim_amount: amount >= 42000.8; evaluated unchanged on the provided validation split. The ratio compares against the no-ID baseline's best score-threshold F1. This dependency-free ratio is screening-only; confirm it with the optional LightGBM sensitivity model. |
| T2 Single-feature shortcut | PASS | {'column': 'hospital_days', 'value': '12', 'count': 131, 'positive_rate': 0.15267175572519084, 'recall': 0.006108735491753207, 'lift': 4.663156863933747} | below warning gates | Strongest checked non-ID value: hospital_days=12 has positive_rate 15.3%, lift 4.7x, recall 0.6% (n=131). |
| T3 Class distribution overlap | PASS | 0.7335 | > 0.2 | Lowest checked overlap is 0.7335 on hospital_days. |
| T4.1 ID-only baseline | PASS | {'ap_ratio': 0.1618590230034241, 'ap_lift': 0.9775195603279712} | ratio/lift below warning pair | Compares ID-only AP to no-ID AP and fraud prevalence. |
| T4.2 Entity-holdout degradation | PASS | {'ap_lift_ratio': 0.87263782733809, 'raw_ap_ratio': 0.8981002902811064, 'provided_prevalence': 0.0311876579332358, 'holdout_prevalence': 0.03209767416164853} | > 0.75 | Compares prevalence-normalized AP-lift on entity holdout against the provided split. |
| T5 Zero-fraud low-amount region | PASS |  |  | No zero-positive low-amount region was found. |
| T6.1 Duplicate feature rows | PASS | 0 | < 0.01 | Duplicate rows excluding labels and configured IDs: 0. |
| T6.2 Label conflicts for identical features | PASS | 0 | = 0.0 | Rows in identical non-ID feature groups with mixed labels: 0. |
| T7 Temporal split degradation | PASS | {'ap_lift_ratio': 1.3612890814266554, 'raw_ap_ratio': 1.8573756028212174, 'provided_prevalence': 0.0311876579332358, 'temporal_prevalence': 0.0425531914893617} | > 0.75 | Compares prevalence-normalized AP-lift on temporal holdout against the provided split. |
| T8.1 Configured leak-column exclusion | PASS |  |  | Configured label/leak columns are excluded from features. |
| T8.2 Suspicious feature names | PASS |  |  | No suspicious label/post-outcome feature names were found. |
| T8.3 Entity aggregate feature names | PASS |  |  | No entity-level aggregate rate/risk/score feature names were found. |
| T9.1 Amount distinct-value count | PASS | 99236 | <= 100 | claim_amount has 99,236 distinct amount values. |
| T9.2 Amount top-10 concentration | PASS | 0.00112 | < 0.7 | Top 10 claim_amount values cover 0.11% of rows. |
| T9.3 Round-amount concentration | PASS | 0 | >= 0.95 | claim_amount values are multiples of 1,000 for 0.00% of rows. |
| T10 Label-noise plausibility | PASS | 0.01486 | 0.01..0.3 | Compares observed investigation labels against oracle labels. |

## Time Coverage

| year | rows | prevalence |
|---|---:|---:|
| 2024 | 49,997 | 2.75% |
| 2025 | 50,003 | 3.80% |

## Amount Profiles

- policy_age_days: distinct 3,262, p50 427, p95 1,852, p99 2,845, max 3,650, top10 share 2.02%, round(1000) share 0.03%
- prior_claim_count_30d: distinct 8, p50 1, p95 2, p99 3, max 7, top10 share 100.00%, round(1000) share 48.01%
- claim_amount: distinct 99,236, p50 25,213, p95 124,335, p99 241,568, max 1,591,568, top10 share 0.11%, round(1000) share 0.00%
- customer_prior_same_provider_count_365d: distinct 3, p50 0, p95 0, p99 0, max 2, top10 share 100.00%, round(1000) share 99.02%
- customer_age: distinct 71, p50 45, p95 70, p99 80, max 88, top10 share 28.64%, round(1000) share 0.00%
- provider_prior_same_pair_count_365d: distinct 23, p50 0, p95 0, p99 1, max 23, top10 share 99.81%, round(1000) share 97.85%
- claim_lag_days: distinct 61, p50 5, p95 23, p99 36, max 60, top10 share 71.36%, round(1000) share 11.80%
- prior_claim_count_365d: distinct 19, p50 7, p95 13, p99 16, max 18, top10 share 81.05%, round(1000) share 2.35%
- provider_prior_high_amount_share_365d: distinct 759, p50 0.1216, p95 0.1935, p99 0.2258, max 0.3061, top10 share 11.92%, round(1000) share 0.00%
- hospital_days: distinct 27, p50 1, p95 5, p99 9, max 26, top10 share 99.16%, round(1000) share 42.33%
- provider_prior_claim_count_365d: distinct 73, p50 70, p95 84, p99 91, max 108, top10 share 43.13%, round(1000) share 0.00%

## Single-Feature Shortcuts

| column | value | n | pos rate | lift | recall |
|---|---|---:|---:|---:|---:|
| hospital_days | 12 | 131 | 15.27% | 4.663x | 0.61% |
| provider_prior_same_pair_count_365d | 1 | 1,416 | 13.70% | 4.185x | 5.93% |
| hospital_days | 10 | 287 | 13.59% | 4.151x | 1.19% |
| policy_age_days | 293 | 100 | 13.00% | 3.971x | 0.40% |
| policy_age_days | 277 | 110 | 11.82% | 3.61x | 0.40% |
| hospital_days | 8 | 717 | 11.44% | 3.493x | 2.50% |
| hospital_days | 6 | 1,811 | 10.77% | 3.289x | 5.96% |
| hospital_days | 9 | 424 | 10.61% | 3.242x | 1.37% |
| accident_date | 2025-09-08 | 132 | 10.61% | 3.239x | 0.43% |
| policy_age_days | 203 | 123 | 10.57% | 3.228x | 0.40% |
| policy_age_days | 229 | 110 | 10.00% | 3.054x | 0.34% |
| hospital_days | 7 | 1,112 | 9.98% | 3.049x | 3.39% |

## Amount Threshold Rules

- claim_amount best_high_threshold: `amount >= 17012.1`, P=3.34%, R=67.38%, F1=0.06372
- claim_amount best_low_threshold: `amount <= 338377`, P=3.28%, R=99.69%, F1=0.06344

## Baselines

- provided_split_no_id_nb: ROC-AUC 0.7859, PR-AUC 0.1884, Best F1 0.262, Top 1% P=35.33%, R=11.30%
- provided_split_id_only_nb: ROC-AUC 0.4818, PR-AUC 0.03049, Best F1 0.06055, Top 1% P=0.67%, R=0.21%
- provided_split_with_id_nb: ROC-AUC 0.7631, PR-AUC 0.1415, Best F1 0.2296, Top 1% P=28.67%, R=9.17%
- provided_split_amount_only_nb: ROC-AUC 0.494, PR-AUC 0.03116, Best F1 0.06049, Top 1% P=1.33%, R=0.43%
- provided_split_amount_threshold: `claim_amount` amount >= 42000.8, train F1 0.04343, validation F1 0.05927
- temporal_holdout_no_id_nb: ROC-AUC 0.8506, PR-AUC 0.3498, Best F1 0.3636, Top 1% P=100.00%, R=16.67%
- temporal_holdout_amount_only_nb: ROC-AUC 0.5562, PR-AUC 0.05162, Best F1 0.1111, Top 1% P=0.00%, R=0.00%
- entity_holdout_no_id_nb: ROC-AUC 0.8022, PR-AUC 0.1692, Best F1 0.256, Top 1% P=30.94%, R=9.64%
- entity_holdout_id_only_nb: ROC-AUC 0.5284, PR-AUC 0.03538, Best F1 0.06968, Top 1% P=3.87%, R=1.20%

## Split Drift

| column | JS divergence | id? |
|---|---:|---:|
| claim_id | 1.00000 | true |
| provider_id | 1.00000 | true |
| claim_amount | 0.99563 | false |
| policy_id | 0.21488 | true |
| customer_id | 0.09689 | true |
| policy_age_days | 0.05258 | false |
| provider_prior_high_amount_share_365d | 0.02579 | false |
| accident_date | 0.00896 | false |
| claim_date | 0.00829 | false |
| provider_prior_claim_count_365d | 0.00392 | false |

## Red Flags

- None.
