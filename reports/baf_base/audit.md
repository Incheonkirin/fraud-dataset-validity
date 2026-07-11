# BAF Base Validity Audit

Verdict: **WARN**

## Overview

- Rows: 1,000,000
- Positives: 11,029 (1.10%)
- Duplicate full rows: 0
- Duplicate rows excluding label and IDs: 0
- Label-conflict rows excluding label and IDs: 0

## Reference Model

- Type: `evidence_naive_bayes`
- Alpha: 1
- Weight clip: 4
- Ratio gates screening-only: true

## Test Verdicts

| test | status | metric | threshold | details |
|---|---:|---:|---:|---|
| T0 Evaluation integrity | INFO |  |  | No published evaluation metadata was provided in the config. |
| T1.1 Amount-only ROC-AUC | PASS | 0.5939 | >= 0.95 | Amount-only baseline is evaluated on the provided split. |
| T1.2 Amount-only share of no-ID PR-AUC | PASS | 0.1299 | >= 0.8 | Compares amount-only average precision to the no-ID baseline. This dependency-free ratio is screening-only; confirm it with the optional LightGBM sensitivity model. |
| T1.3 Best one-sided amount threshold | PASS | {'f1': 0.03247794707297514, 'f1_ratio': 0.15541062595172234} | F1 >= 0.7 and ratio >= 0.8 | Training-selected threshold rule: intended_balcon_amount: amount <= 0.0538092; evaluated unchanged on the provided validation split. The ratio compares against the no-ID baseline's best score-threshold F1. This dependency-free ratio is screening-only; confirm it with the optional LightGBM sensitivity model. |
| T2 Single-feature shortcut | WARN | {'column': 'housing_status', 'value': 'BA', 'count': 169675, 'positive_rate': 0.0374657433328422, 'recall': 0.5763895185420256, 'lift': 3.3970208842907064} | recall >= 0.2 and lift >= 3.0 | Broad shortcut warning: housing_status=BA has positive_rate 3.7%, lift 3.4x, recall 57.6% (n=169,675). |
| T3 Class distribution overlap | PASS | 0.7454 | > 0.2 | Lowest checked overlap is 0.7454 on credit_risk_score. |
| T4.1 ID-only baseline | PASS | {'ap_ratio': 0.10351735008531332, 'ap_lift': 1.0} | ratio/lift below warning pair | Compares ID-only AP to no-ID AP and fraud prevalence. |
| T4.2 Entity-holdout degradation | INFO |  |  | No entity-holdout baseline was available. |
| T5 Zero-fraud low-amount region | PASS | 0.000221 | < 0.5 | intended_balcon_amount <= -8.252 covers 221 rows with zero positives. |
| T6.1 Duplicate feature rows | PASS | 0 | < 0.01 | Duplicate rows excluding labels and configured IDs: 0. |
| T6.2 Label conflicts for identical features | PASS | 0 | = 0.0 | Rows in identical non-ID feature groups with mixed labels: 0. |
| T7 Temporal split degradation | PASS | {'ap_lift_ratio': 1.2143004827611519, 'raw_ap_ratio': 1.2754766575488765, 'provided_prevalence': 0.014038271117159567, 'temporal_prevalence': 0.014745515938167962} | > 0.75 | Compares prevalence-normalized AP-lift on temporal holdout against the provided split. |
| T8.1 Configured leak-column exclusion | PASS |  |  | Configured label/leak columns are excluded from features. |
| T8.2 Suspicious feature names | PASS |  |  | No suspicious label/post-outcome feature names were found. |
| T8.3 Entity aggregate feature names | PASS |  |  | No entity-level aggregate rate/risk/score feature names were found. |
| T9.1 Amount distinct-value count | PASS | 994971 | <= 100 | intended_balcon_amount has 994,971 distinct amount values. |
| T9.2 Amount top-10 concentration | PASS | 3e-05 | < 0.7 | Top 10 intended_balcon_amount values cover 0.00% of rows. |
| T9.3 Round-amount concentration | PASS | 0 | >= 0.95 | intended_balcon_amount values are multiples of 1,000 for 0.00% of rows. |
| T10 Label-noise plausibility | INFO |  |  | No separate oracle label is configured; label-noise plausibility cannot be measured directly. |

## Time Coverage

| year | rows | prevalence |
|---|---:|---:|
| 2022 | 1,000,000 | 1.10% |

## Amount Profiles

- date_of_birth_distinct_emails_4w: distinct 40, p50 9, p95 19, p99 23, max 39, top10 share 70.09%, round(1000) share 0.13%
- session_length_in_minutes: distinct 994,887, p50 5.114, p95 21.7, p99 44.55, max 85.9, top10 share 0.20%, round(1000) share 0.00%
- proposed_credit_limit: distinct 12, p50 200, p95 1,500, p99 1,500, max 2,100, top10 share 99.98%, round(1000) share 8.80%
- keep_alive_session: distinct 2, p50 1, p95 1, p99 1, max 1, top10 share 100.00%, round(1000) share 42.31%
- velocity_6h: distinct 998,687, p50 5,320, p95 11,235, p99 13,932, max 16,716, top10 share 0.00%, round(1000) share 0.00%
- days_since_request: distinct 989,330, p50 0.01518, p95 6.682, p99 22, max 78.46, top10 share 0.00%, round(1000) share 0.00%
- email_is_free: distinct 2, p50 1, p95 1, p99 1, max 1, top10 share 100.00%, round(1000) share 47.01%
- current_address_months_count: distinct 423, p50 52, p95 277, p99 370, max 428, top10 share 15.11%, round(1000) share 0.96%
- credit_risk_score: distinct 551, p50 122, p95 255, p99 305, max 389, top10 share 6.71%, round(1000) share 0.05%
- bank_months_count: distinct 33, p50 5, p95 30, p99 31, max 32, top10 share 82.21%, round(1000) share 0.00%
- income: distinct 9, p50 0.6, p95 0.9, p99 0.9, max 0.9, top10 share 100.00%, round(1000) share 0.00%
- customer_age: distinct 9, p50 30, p95 50, p99 60, max 90, top10 share 100.00%, round(1000) share 0.00%
- velocity_24h: distinct 998,940, p50 4,750, p95 7,349, p99 8,597, max 9,507, top10 share 0.00%, round(1000) share 0.00%
- device_distinct_emails_8w: distinct 4, p50 1, p95 1, p99 2, max 2, top10 share 100.00%, round(1000) share 0.63%
- zip_count_4w: distinct 6,306, p50 1,263, p95 3,677, p99 4,970, max 6,700, top10 share 0.77%, round(1000) share 0.11%
- prev_address_months_count: distinct 374, p50 -1, p95 98, p99 231, max 383, top10 share 80.05%, round(1000) share 0.00%
- intended_balcon_amount: distinct 994,971, p50 -0.8305, p95 50.39, p99 100.8, max 113, top10 share 0.00%, round(1000) share 0.00%
- velocity_4w: distinct 998,318, p50 4,913, p95 6,458, p99 6,779, max 6,995, top10 share 0.00%, round(1000) share 0.00%
- month: distinct 8, p50 3, p95 7, p99 7, max 7, top10 share 100.00%, round(1000) share 13.24%
- has_other_cards: distinct 2, p50 0, p95 1, p99 1, max 1, top10 share 100.00%, round(1000) share 77.70%
- foreign_request: distinct 2, p50 0, p95 0, p99 1, max 1, top10 share 100.00%, round(1000) share 97.48%
- phone_home_valid: distinct 2, p50 0, p95 1, p99 1, max 1, top10 share 100.00%, round(1000) share 58.29%
- bank_branch_count_8w: distinct 2,326, p50 9, p95 1,463, p99 1,974, max 2,385, top10 share 55.37%, round(1000) share 14.45%
- name_email_similarity: distinct 998,861, p50 0.4922, p95 0.9181, p99 0.9975, max 1, top10 share 0.00%, round(1000) share 0.00%
- phone_mobile_valid: distinct 2, p50 1, p95 1, p99 1, max 1, top10 share 100.00%, round(1000) share 11.03%

## Single-Feature Shortcuts

| column | value | n | pos rate | lift | recall |
|---|---|---:|---:|---:|---:|
| proposed_credit_limit | 1900 | 390 | 20.51% | 18.6x | 0.73% |
| proposed_credit_limit | 2000 | 6,114 | 12.97% | 11.76x | 7.19% |
| credit_risk_score | 344 | 111 | 12.61% | 11.44x | 0.13% |
| credit_risk_score | 338 | 136 | 11.76% | 10.67x | 0.15% |
| credit_risk_score | 339 | 116 | 9.48% | 8.598x | 0.10% |
| credit_risk_score | 325 | 264 | 9.47% | 8.586x | 0.23% |
| credit_risk_score | 320 | 246 | 8.94% | 8.109x | 0.20% |
| credit_risk_score | 340 | 129 | 8.53% | 7.732x | 0.10% |
| credit_risk_score | 310 | 349 | 8.31% | 7.534x | 0.26% |
| credit_risk_score | 326 | 213 | 7.98% | 7.237x | 0.15% |
| credit_risk_score | 333 | 164 | 7.93% | 7.187x | 0.12% |
| credit_risk_score | 341 | 103 | 7.77% | 7.042x | 0.07% |

## Amount Threshold Rules

- intended_balcon_amount: zero-positive low region `intended_balcon_amount <= -8.252` covers 221 rows (0.02%).
- intended_balcon_amount best_high_threshold: `amount >= -1.57406`, P=1.11%, R=95.37%, F1=0.02198
- intended_balcon_amount best_low_threshold: `amount <= 0.0538092`, P=1.31%, R=88.53%, F1=0.02589

## Baselines

- provided_split_no_id_nb: ROC-AUC 0.8458, PR-AUC 0.1356, Best F1 0.209, Top 1% P=23.37%, R=16.64%
- provided_split_id_only_nb: ROC-AUC 0.5, PR-AUC 0.01404, Best F1 0.02769, Top 1% P=1.32%, R=0.94%
- provided_split_with_id_nb: ROC-AUC 0.8458, PR-AUC 0.1356, Best F1 0.209, Top 1% P=23.37%, R=16.64%
- provided_split_amount_only_nb: ROC-AUC 0.5939, PR-AUC 0.01761, Best F1 0.03595, Top 1% P=2.24%, R=1.60%
- provided_split_amount_threshold: `intended_balcon_amount` amount <= 0.0538092, train F1 0.02412, validation F1 0.03248
- temporal_holdout_no_id_nb: ROC-AUC 0.8679, PR-AUC 0.173, Best F1 0.2475, Top 1% P=28.82%, R=19.54%
- temporal_holdout_amount_only_nb: ROC-AUC 0.573, PR-AUC 0.01741, Best F1 0.03538, Top 1% P=1.24%, R=0.84%

## Split Drift

| column | JS divergence | id? |
|---|---:|---:|
| event_date | 1.00000 | false |
| month | 1.00000 | false |
| application_id | 1.00000 | true |
| velocity_24h | 0.99938 | false |
| velocity_4w | 0.99932 | false |
| velocity_6h | 0.99928 | false |
| name_email_similarity | 0.99922 | false |
| intended_balcon_amount | 0.99627 | false |
| session_length_in_minutes | 0.99568 | false |
| days_since_request | 0.99198 | false |

## Red Flags

- [WARN][T2] Broad shortcut warning: housing_status=BA has positive_rate 3.7%, lift 3.4x, recall 57.6% (n=169,675).
