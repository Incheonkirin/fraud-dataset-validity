# AI Hub FDS - Electronic Financial Network Validity Audit

Verdict: **FAIL**

## Overview

- Rows: 4,434,106
- Positives: 17,175 (0.39%)
- Duplicate full rows: 60,538
- Duplicate rows excluding label: 60,538

## Test Verdicts

| test | status | metric | threshold | details |
|---|---:|---:|---:|---|
| T0.1 Published split integrity | FAIL |  |  | Published model path concatenates supplied splits and performs a new random split. |
| T0.2 Temporal validation | WARN |  |  | Event-date columns exist, but the published evaluation metadata does not record a temporal holdout. |
| T0.3 Entity holdout | WARN |  |  | Entity ID columns exist, but the published evaluation metadata does not record an entity holdout. |
| T0.4 Type-classification scope | INFO |  |  | Type classification is recorded as a fraud-only task, so it is not evidence of detection validity. |
| T1.1 Amount-only ROC-AUC | FAIL | 0.9969 | >= 0.95 | Amount-only baseline is evaluated on the provided split. |
| T1.2 Amount-only share of no-ID PR-AUC | FAIL | 1.119 | >= 0.8 | Compares amount-only average precision to the no-ID baseline. |
| T1.3 Best one-sided amount threshold | PASS | 0.5588 | >= 0.7 | Best threshold rule: 거래금액: amount >= 4e+06. |
| T5 Zero-fraud low-amount region | FAIL | 0.9897 | >= 0.9 | 거래금액 <= 1,000,000 covers 4,388,368 rows with zero positives. |
| T9.1 Amount distinct-value count | FAIL | 48 | <= 100 | 거래금액 has 48 distinct amount values. |
| T9.2 Amount top-10 concentration | FAIL | 0.9805 | >= 0.9 | Top 10 거래금액 values cover 98.05% of rows. |
| T9.3 Round-amount concentration | WARN | 0.9991 | >= 0.95 | 거래금액 values are multiples of 1,000 for 99.91% of rows. |

## Time Coverage

| year | rows | prevalence |
|---|---:|---:|
| 2021 | 400,340 | 0.17% |
| 2022 | 1,295,280 | 0.36% |
| 2023 | 1,306,786 | 0.39% |
| 2024 | 1,431,700 | 0.46% |

## Amount Profiles

- 거래금액: distinct 48, p50 30,000, p95 300,000, p99 2,000,000, max 500,000,000, top10 share 98.05%, round(1000) share 99.91%

## Single-Feature Shortcuts

| column | value | n | pos rate | lift | recall |
|---|---|---:|---:|---:|---:|
| 거래금액 | 500000000 | 378 | 69.31% | 178.9x | 1.53% |
| 거래금액 | 400000000 | 462 | 61.26% | 158.1x | 1.65% |
| 거래금액 | 300000000 | 739 | 52.64% | 135.9x | 2.26% |
| 거래금액 | 90000000 | 1,070 | 51.50% | 132.9x | 3.21% |
| 거래금액 | 70000000 | 1,588 | 49.31% | 127.3x | 4.56% |
| 거래금액 | 20000000 | 172 | 48.84% | 126.1x | 0.49% |
| 거래금액 | 80000000 | 1,246 | 48.64% | 125.6x | 3.53% |
| 거래금액 | 60000000 | 1,998 | 47.75% | 123.3x | 5.55% |
| 거래금액 | 50000000 | 2,166 | 47.37% | 122.3x | 5.97% |
| 거래금액 | 200000000 | 1,676 | 44.81% | 115.7x | 4.37% |
| 거래금액 | 10000000 | 136 | 44.12% | 113.9x | 0.35% |
| 거래금액 | 40000000 | 1,299 | 42.65% | 110.1x | 3.23% |

## Amount Threshold Rules

- 거래금액: zero-positive low region `거래금액 <= 1,000,000` covers 4,388,368 rows (98.97%).
- 거래금액 best_high_threshold: `amount >= 4e+06`, P=38.91%, R=99.12%, F1=0.5588
- 거래금액 best_low_threshold: `amount <= 5e+08`, P=0.39%, R=100.00%, F1=0.007717

## Baselines

- provided_split_no_id_nb: ROC-AUC 0.9966, PR-AUC 0.3526, Top 1% P=37.37%, R=96.49%
- provided_split_amount_only_nb: ROC-AUC 0.9969, PR-AUC 0.3947, Top 1% P=38.50%, R=99.42%
- temporal_holdout_no_id_nb: ROC-AUC 0.9962, PR-AUC 0.362, Top 1% P=39.18%, R=84.54%
- temporal_holdout_amount_only_nb: ROC-AUC 0.9965, PR-AUC 0.3939, Top 1% P=40.28%, R=86.90%

## Split Drift

| column | JS divergence | id? |
|---|---:|---:|
| 입금계좌일련번호 | 0.13266 | true |
| 출금계좌일련번호 | 0.01374 | true |
| 거래일자 | 0.00052 | false |
| 출금금융회사일련번호 | 0.00002 | false |
| 입금금융회사일련번호 | 0.00002 | false |
| 거래금액 | 0.00002 | false |
| 매체구분 | 0.00000 | false |
| 거래시간대 | 0.00000 | false |
| 자금구분 | 0.00000 | false |

## Red Flags

- [FAIL][T0.1] Published model path concatenates supplied splits and performs a new random split.
- [WARN][T0.2] Event-date columns exist, but the published evaluation metadata does not record a temporal holdout.
- [WARN][T0.3] Entity ID columns exist, but the published evaluation metadata does not record an entity holdout.
- [FAIL][T1.1] Amount-only baseline is evaluated on the provided split.
- [FAIL][T1.2] Compares amount-only average precision to the no-ID baseline.
- [FAIL][T5] 거래금액 <= 1,000,000 covers 4,388,368 rows with zero positives.
- [FAIL][T9.1] 거래금액 has 48 distinct amount values.
- [FAIL][T9.2] Top 10 거래금액 values cover 98.05% of rows.
- [WARN][T9.3] 거래금액 values are multiples of 1,000 for 99.91% of rows.
- [FAIL][T2] 거래금액=500000000 has positive_rate 69.3%, lift 178.9x (n=378).
- [FAIL][T2] 거래금액=400000000 has positive_rate 61.3%, lift 158.1x (n=462).
- [FAIL][T2] 거래금액=300000000 has positive_rate 52.6%, lift 135.9x (n=739).
- [FAIL][T2] 거래금액=90000000 has positive_rate 51.5%, lift 132.9x (n=1,070).
- [WARN][G0] Duplicate rows excluding label: 60,538 (1.4%).
- [WARN][G4] Train/validation non-ID distributions are nearly identical.
