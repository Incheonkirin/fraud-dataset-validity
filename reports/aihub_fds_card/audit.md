# AI Hub FDS - Card Transactions Validity Audit

Verdict: **FAIL**

## Overview

- Rows: 1,952,871
- Positives: 72,008 (3.69%)
- Duplicate full rows: 0
- Duplicate rows excluding label: 0

## Test Verdicts

| test | status | metric | threshold | details |
|---|---:|---:|---:|---|
| T0.1 Published split integrity | FAIL |  |  | Published model path concatenates supplied splits and performs a new random split. |
| T0.2 Temporal validation | WARN |  |  | Event-date columns exist, but the published evaluation metadata does not record a temporal holdout. |
| T0.3 Entity holdout | WARN |  |  | Entity ID columns exist, but the published evaluation metadata does not record an entity holdout. |
| T0.4 Type-classification scope | INFO |  |  | Type classification is recorded as a fraud-only task, so it is not evidence of detection validity. |
| T1.1 Amount-only ROC-AUC | FAIL | 0.9519 | >= 0.95 | Amount-only baseline is evaluated on the provided split. |
| T1.2 Amount-only share of no-ID PR-AUC | FAIL | 0.8937 | >= 0.8 | Compares amount-only average precision to the no-ID baseline. |
| T1.3 Best one-sided amount threshold | FAIL | 0.718 | >= 0.7 | Best threshold rule: 통합승인금액: amount >= 318000. |
| T5 Zero-fraud low-amount region | PASS |  |  | No zero-positive low-amount region was found. |
| T9.1 Amount distinct-value count | PASS | 1931 | <= 100 | 통합승인금액 has 1,931 distinct amount values. |
| T9.2 Amount top-10 concentration | WARN | 0.8601 | >= 0.7 | Top 10 통합승인금액 values cover 86.01% of rows. |
| T9.3 Round-amount concentration | WARN | 1 | >= 0.95 | 통합승인금액 values are multiples of 1,000 for 100.00% of rows. |

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
- 통합승인금액: distinct 1,931, p50 9,000, p95 105,000, p99 1,688,000, max 2,943,000, top10 share 86.01%, round(1000) share 100.00%
- 전월_매출금액: distinct 339,865, p50 1,871,000, p95 3,815,204,000, p99 51,811,979,000, max 93,263,339,000, top10 share 0.78%, round(1000) share 100.00%
- 경과일수_최종이용일자: distinct 33, p50 32, p95 35, p99 39, max 62, top10 share 99.16%, round(1000) share 0.00%

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

- provided_split_no_id_nb: ROC-AUC 0.9751, PR-AUC 0.7126, Top 1% P=95.12%, R=25.80%
- provided_split_amount_only_nb: ROC-AUC 0.9519, PR-AUC 0.6369, Top 1% P=79.31%, R=21.51%
- temporal_holdout_no_id_nb: ROC-AUC 0.9741, PR-AUC 0.7009, Top 1% P=94.36%, R=27.05%
- temporal_holdout_amount_only_nb: ROC-AUC 0.9558, PR-AUC 0.6495, Top 1% P=81.63%, R=23.40%

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
- [FAIL][T1.2] Compares amount-only average precision to the no-ID baseline.
- [FAIL][T1.3] Best threshold rule: 통합승인금액: amount >= 318000.
- [WARN][T9.2] Top 10 통합승인금액 values cover 86.01% of rows.
- [WARN][T9.3] 통합승인금액 values are multiples of 1,000 for 100.00% of rows.
- [FAIL][T2] 일시불할부구분코드=B has positive_rate 97.8%, lift 26.5x (n=24,440).
- [FAIL][T2] 승인거래코드=1 has positive_rate 90.8%, lift 24.6x (n=18,239).
- [FAIL][T2] 통합승인금액=1546000 has positive_rate 84.6%, lift 22.9x (n=104).
- [FAIL][T2] 통합승인금액=1478000 has positive_rate 79.0%, lift 21.4x (n=100).
