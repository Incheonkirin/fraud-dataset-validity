# AI Hub FDS Case Study Summary

Run date: 2026-07-09 KST

Protocol: `PROTOCOL.md`

Thresholds: `thresholds.yaml`

## Datasets

| dataset | verdict | rows | fraud rate | strongest finding |
|---|---:|---:|---:|---|
| Card transactions | FAIL | 1,952,871 | 3.69% | One amount threshold reaches F1 0.718, close to the official detection F1 claim. |
| Electronic financial network | FAIL | 4,434,106 | 0.39% | `거래금액 <= 1,000,000` covers 98.97% of rows with zero positives. |

## Card Transactions

Key failures:

- `T0.1`: the published model path is recorded as concatenating supplied splits
  and performing a new random split.
- `T1.1`: amount-only ROC-AUC is `0.9519`.
- `T1.2`: amount-only PR-AUC is `89.37%` of the no-ID baseline PR-AUC.
- `T1.3`: `통합승인금액 >= 318000` reaches F1 `0.718`.
- `T2`: `일시불할부구분코드=B` has `97.77%` fraud rate and `26.51x` lift.
- `T2`: `승인거래코드=1` has `90.85%` fraud rate and `24.64x` lift.
- `T9.2`: the top 10 `통합승인금액` values cover `86.01%` of rows.

## Electronic Financial Network

Key failures:

- `T0.1`: the published model path is recorded as concatenating supplied splits
  and performing a new random split.
- `T1.1`: amount-only ROC-AUC is `0.9969`.
- `T1.2`: amount-only PR-AUC exceeds the no-ID baseline PR-AUC.
- `T5`: `거래금액 <= 1,000,000` covers `4,388,368` rows, or `98.97%`
  of the dataset, with zero positives.
- `T9.1`: `거래금액` has only `48` distinct values.
- `T9.2`: the top 10 `거래금액` values cover `98.05%` of rows.
- `T2`: high-amount values show extreme lift, for example
  `거래금액=500000000` has `69.31%` fraud rate and `178.9x` lift.

## Interpretation

The reference model scores do not rehabilitate the dataset. The same outcome can
be largely explained by exposed amount and code shortcuts, weak split handling,
and unrealistically discrete monetary fields.

The dataset may still be useful for ingestion demos, imbalance handling examples,
or audit-method development. It is weak evidence for behavior-level fraud
detection model quality.
