# AI Hub FDS Case Study Summary

Run date: 2026-07-10 KST

Protocol: `PROTOCOL.md`

Thresholds: `thresholds.yaml`

Reference model: `reference_model.yaml`

## Datasets

| dataset | verdict | rows | fraud rate | confidence | strongest finding |
|---|---:|---:|---:|---|---|
| Card transactions | FAIL | 1,952,871 | 3.69% | High, but less decisive than EFT | A one-sided amount threshold reaches F1 0.718 and 1.12x the no-ID best-F1. |
| Electronic financial network | FAIL | 4,434,106 | 0.39% | Very high | `거래금액 <= 1,000,000` covers 98.97% of rows with zero positives. |

## Card Transactions

Key failures and warnings:

- `T0.1`: the published model path is recorded as concatenating supplied splits
  and performing a new random split.
- `T1.1`: amount-only ROC-AUC is `0.9519`. This is marginal against the `0.95`
  threshold; the card verdict does not depend on this gate alone.
- `T1.2`: amount-only PR-AUC is `89.37%` of the no-ID baseline PR-AUC.
- `T1.3`: `통합승인금액 >= 318000` reaches F1 `0.718`, which is `1.12x`
  the no-ID baseline's best score-threshold F1.
- `T2`: `가맹점누적매출금액_구간화=3` captures `58.18%` of fraud rows with
  `6.22x` lift.
- Single-feature table: `일시불할부구분코드=B` has `97.77%` fraud rate and
  `26.51x` lift; `승인거래코드=1` has `90.85%` fraud rate and `24.64x` lift.
- `T4.1`: ID-only PR-AUC is `67.62%` of the no-ID PR-AUC and `13.07x`
  fraud prevalence.
- `T9.2`: the top 10 `통합승인금액` values cover `86.01%` of rows.
- `T9.3`: `통합승인금액` is rounded to 1,000-unit multiples for `100.00%`
  of rows.

## Electronic Financial Network

Key failures:

- `T0.1`: the published model path is recorded as concatenating supplied splits
  and performing a new random split.
- `T1.1`: amount-only ROC-AUC is `0.9969`.
- `T1.2`: amount-only PR-AUC exceeds the no-ID baseline PR-AUC.
- `T2`: `거래금액=4000000` alone captures `30.05%` of fraud rows with `88.13x`
  lift.
- `T3`: `거래금액` class-distribution overlap is only `0.0065`.
- `T5`: `거래금액 <= 1,000,000` covers `4,388,368` rows, or `98.97%`
  of the dataset, with zero positives.
- `T6.1`: duplicate feature rows excluding label account for `1.365%` of rows.
- `T9.1`: `거래금액` has only `48` distinct values.
- `T9.2`: the top 10 `거래금액` values cover `98.05%` of rows.
- `T9.3`: `거래금액` is rounded to 1,000-unit multiples for `99.91%` of rows.

## Cross-Dataset Check

The same protocol yields a graded comparison:

- `K-Claims-Synth v0.2`: `PASS`
- ULB Credit Card Fraud: `WARN`
- BAF Base: `WARN`
- AI Hub Card: `FAIL`
- AI Hub Electronic Financial Network: `FAIL`

See `ANCHOR_COMPARISON.md`.

## Interpretation

The AI Hub FDS verdict is not a claim that amount can never be useful in real
fraud detection. The issue is the combination of shortcut-solvable labels,
template-like monetary support, weak published split handling, and missing
trivial-baseline controls.

The electronic financial network subset is the strongest public case: its label
is almost equivalent to an amount threshold and a 48-value amount template. The
card subset is also invalid as a detection benchmark, but should be presented
as corroborating evidence rather than the lead exhibit.

The dataset may still be useful for ingestion demos, imbalance handling
examples, or audit-method development. It is weak evidence for behavior-level
fraud detection model quality.
