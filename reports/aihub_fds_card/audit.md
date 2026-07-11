# AI Hub FDS - Card Transactions Validity Audit

Verdict: **FAIL**

## Overview

- Rows: 1,952,871
- Positives: 72,008 (3.69%)
- Duplicate full rows: 0
- Duplicate rows excluding label and IDs: 44
- Label-conflict rows excluding label and IDs: 0

## Reference Model

- Type: `evidence_naive_bayes`
- Alpha: 1
- Weight clip: 4
- Ratio gates screening-only: true

## Test Verdicts

| test | status | metric | threshold | details |
|---|---:|---:|---:|---|
| T0.1 Published split integrity | FAIL |  |  | Published model path concatenates supplied splits and performs a new random split. |
| T0.2 Temporal validation | WARN |  |  | Event-date columns exist, but the published evaluation metadata does not record a temporal holdout. |
| T0.3 Entity holdout | WARN |  |  | Entity ID columns exist, but the published evaluation metadata does not record an entity holdout. |
| T0.4 Type-classification scope | INFO |  |  | Type classification is recorded as a fraud-only task, so it is not evidence of detection validity. |
| T1.1 Amount-only ROC-AUC | FAIL | 0.9519 | >= 0.95 | Amount-only baseline is evaluated on the provided split. |
| T1.2 Amount-only share of no-ID PR-AUC | WARN | 0.8713 | >= 0.8 | Compares amount-only average precision to the no-ID baseline. This dependency-free ratio is screening-only; confirm it with the optional LightGBM sensitivity model. |
| T1.3 Best one-sided amount threshold | WARN | {'f1': 0.7204085858237284, 'f1_ratio': 1.1282727396956076} | F1 >= 0.7 and ratio >= 0.8 | Training-selected threshold rule: 통합승인금액: amount >= 318000; evaluated unchanged on the provided validation split. The ratio compares against the no-ID baseline's best score-threshold F1. This dependency-free ratio is screening-only; confirm it with the optional LightGBM sensitivity model. |
| T2 Single-feature shortcut | FAIL | {'column': '가맹점누적매출금액_구간화', 'value': '3', 'count': 182758, 'positive_rate': 0.22922115584543495, 'recall': 0.5817686923675147, 'lift': 6.2165224396876795} | recall >= 0.1 and lift >= 5.0 | Recall-weighted shortcut: 가맹점누적매출금액_구간화=3 has positive_rate 22.9%, lift 6.2x, recall 58.2% (n=182,758). |
| T3 Class distribution overlap | PASS | 0.2104 | > 0.2 | Lowest checked overlap is 0.2104 on 통합승인금액. |
| T4.1 ID-only baseline | WARN | {'ap_ratio': 0.6761809060995843, 'ap_lift': 13.067468202175169} | ratio >= 0.5 and lift >= 1.5 | Compares ID-only AP to no-ID AP and fraud prevalence. |
| T4.2 Entity-holdout degradation | PASS | {'ap_lift_ratio': 1.03094196450983, 'raw_ap_ratio': 0.9691543289458119, 'provided_prevalence': 0.03687334666752694, 'holdout_prevalence': 0.03466340955724343} | > 0.75 | Compares prevalence-normalized AP-lift on entity holdout against the provided split. |
| T5 Zero-fraud low-amount region | PASS |  |  | No zero-positive low-amount region was found. |
| T6.1 Duplicate feature rows | PASS | 2.253e-05 | < 0.01 | Duplicate rows excluding labels and configured IDs: 44. |
| T6.2 Label conflicts for identical features | PASS | 0 | = 0.0 | Rows in identical non-ID feature groups with mixed labels: 0. |
| T7 Temporal split degradation | PASS | {'ap_lift_ratio': 1.0396206814661069, 'raw_ap_ratio': 0.9836486296705499, 'provided_prevalence': 0.03687334666752694, 'temporal_prevalence': 0.034888125609169575} | > 0.75 | Compares prevalence-normalized AP-lift on temporal holdout against the provided split. |
| T8.1 Configured leak-column exclusion | PASS |  |  | Configured label/leak columns are excluded from features. |
| T8.2 Suspicious feature names | PASS |  |  | No suspicious label/post-outcome feature names were found. |
| T8.3 Entity aggregate feature names | WARN | 1 | 0 suspicious aggregate names | Feature names look like entity-level aggregates, rates, or scores: 가맹점누적매출금액_구간화. Verify they are computed from prior-period data only. |
| T9.1 Amount distinct-value count | PASS | 1931 | <= 100 | 통합승인금액 has 1,931 distinct amount values. |
| T9.2 Amount top-10 concentration | WARN | 0.8601 | >= 0.7 | Top 10 통합승인금액 values cover 86.01% of rows. |
| T9.3 Round-amount concentration | WARN | 1 | >= 0.95 | 통합승인금액 values are multiples of 1,000 for 100.00% of rows. |
| T10 Label-noise plausibility | INFO |  |  | No separate oracle label is configured; label-noise plausibility cannot be measured directly. |

## Time Coverage

| year | rows | prevalence |
|---|---:|---:|
| 2021 | 506,873 | 3.69% |
| 2022 | 492,726 | 4.12% |
| 2023 | 483,370 | 3.44% |
| 2024 | 469,902 | 3.49% |

## Amount Profiles

- 전월_매출건수: distinct 123,657, p50 338, p95 143,031, p99 1,597,241, max 1,853,135, top10 share 14.26%, round(1000) share 0.53%
- 카드이용한도금액: distinct 4, p50 5,000,000, p95 10,000,000, p99 10,000,000, max 10,000,000, top10 share 100.00%, round(1000) share 100.00%
- 경과일수_최종이용일자: distinct 33, p50 32, p95 35, p99 39, max 62, top10 share 99.16%, round(1000) share 0.00%
- 통합승인금액: distinct 1,931, p50 9,000, p95 105,000, p99 1,688,000, max 2,943,000, top10 share 86.01%, round(1000) share 100.00%
- 전월_매출금액: distinct 339,865, p50 1,871,000, p95 3,815,204,000, p99 51,811,979,000, max 93,263,339,000, top10 share 0.78%, round(1000) share 100.00%

## Single-Feature Shortcuts

| column | value | n | pos rate | lift | recall |
|---|---|---:|---:|---:|---:|
| 일시불할부구분코드 | B | 24,440 | 97.77% | 26.51x | 33.18% |
| 승인거래코드 | 1 | 18,239 | 90.85% | 24.64x | 23.01% |
| 통합승인금액 | 1546000 | 104 | 84.62% | 22.95x | 0.12% |
| 통합승인금액 | 1478000 | 100 | 79.00% | 21.42x | 0.11% |
| 통합승인금액 | 1573000 | 106 | 72.64% | 19.7x | 0.11% |
| 통합승인금액 | 1616000 | 102 | 72.55% | 19.68x | 0.10% |
| 가맹점승인업종코드 | 9103 | 5,476 | 70.05% | 19x | 5.33% |
| 통합승인금액 | 1511000 | 110 | 70.00% | 18.98x | 0.11% |
| 가맹점승인업종코드 | 9201 | 8,148 | 68.00% | 18.44x | 7.69% |
| 가맹점승인업종코드 | 9205 | 11,628 | 60.52% | 16.41x | 9.77% |
| 가맹점승인업종코드 | 9204 | 4,208 | 55.58% | 15.07x | 3.25% |
| 가맹점승인업종코드 | 6706 | 112 | 50.89% | 13.8x | 0.08% |

## Amount Threshold Rules

- 통합승인금액 best_high_threshold: `amount >= 318000`, P=80.34%, R=64.91%, F1=0.718
- 통합승인금액 best_low_threshold: `amount <= 2.943e+06`, P=3.69%, R=100.00%, F1=0.07112

## Baselines

- provided_split_no_id_nb: ROC-AUC 0.9751, PR-AUC 0.7126, Best F1 0.6385, Top 1% P=95.12%, R=25.80%
- provided_split_id_only_nb: ROC-AUC 0.9077, PR-AUC 0.4818, Best F1 0.499, Top 1% P=77.00%, R=20.88%
- provided_split_with_id_nb: ROC-AUC 0.9733, PR-AUC 0.6987, Best F1 0.6254, Top 1% P=94.24%, R=25.56%
- provided_split_amount_only_nb: ROC-AUC 0.9519, PR-AUC 0.6209, Best F1 0.7203, Top 1% P=79.31%, R=21.51%
- provided_split_amount_threshold: `통합승인금액` amount >= 318000, train F1 0.7177, validation F1 0.7204
- temporal_holdout_no_id_nb: ROC-AUC 0.9741, PR-AUC 0.7009, Best F1 0.6286, Top 1% P=94.36%, R=27.05%
- temporal_holdout_amount_only_nb: ROC-AUC 0.9558, PR-AUC 0.6277, Best F1 0.7198, Top 1% P=81.63%, R=23.40%
- entity_holdout_no_id_nb: ROC-AUC 0.9731, PR-AUC 0.6906, Best F1 0.6247, Top 1% P=93.88%, R=27.08%
- entity_holdout_id_only_nb: ROC-AUC 0.8752, PR-AUC 0.3843, Best F1 0.4283, Top 1% P=67.13%, R=19.37%

## Split Drift

| column | JS divergence | id? |
|---|---:|---:|
| 전월_매출금액 | 0.20486 | false |
| 전월_매출건수 | 0.08101 | false |
| 가맹점KEY | 0.00944 | true |
| 카드KEY | 0.00264 | true |
| 통합승인금액 | 0.00189 | false |
| 승인일자 | 0.00140 | false |
| 가맹점승인업종코드 | 0.00051 | false |
| 승인SEQ | 0.00033 | true |
| 경과일수_최종이용일자 | 0.00004 | false |
| 기준년월 | 0.00004 | false |

## Red Flags

- [FAIL][T0.1] Published model path concatenates supplied splits and performs a new random split.
- [WARN][T0.2] Event-date columns exist, but the published evaluation metadata does not record a temporal holdout.
- [WARN][T0.3] Entity ID columns exist, but the published evaluation metadata does not record an entity holdout.
- [FAIL][T1.1] Amount-only baseline is evaluated on the provided split.
- [WARN][T1.2] Compares amount-only average precision to the no-ID baseline. This dependency-free ratio is screening-only; confirm it with the optional LightGBM sensitivity model.
- [WARN][T1.3] Training-selected threshold rule: 통합승인금액: amount >= 318000; evaluated unchanged on the provided validation split. The ratio compares against the no-ID baseline's best score-threshold F1. This dependency-free ratio is screening-only; confirm it with the optional LightGBM sensitivity model.
- [FAIL][T2] Recall-weighted shortcut: 가맹점누적매출금액_구간화=3 has positive_rate 22.9%, lift 6.2x, recall 58.2% (n=182,758).
- [WARN][T4.1] Compares ID-only AP to no-ID AP and fraud prevalence.
- [WARN][T9.2] Top 10 통합승인금액 values cover 86.01% of rows.
- [WARN][T9.3] 통합승인금액 values are multiples of 1,000 for 100.00% of rows.
- [WARN][T8.3] Feature names look like entity-level aggregates, rates, or scores: 가맹점누적매출금액_구간화. Verify they are computed from prior-period data only.
