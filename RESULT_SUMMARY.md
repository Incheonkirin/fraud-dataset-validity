# AI Hub FDS Case Study Summary

Run date: 2026-07-11 KST

Protocol: `PROTOCOL.md`

Thresholds: `thresholds.yaml`

Reference model: `reference_model.yaml`

Sensitivity model: `lightgbm_sensitivity.json`

## Datasets

| dataset | verdict | rows | fraud rate | confidence | strongest finding |
|---|---:|---:|---:|---|---|
| Card transactions | FAIL | 1,952,871 | 3.69% | Moderate; less decisive than EFT | One category value captures 58.18% of positives at 6.22x lift. |
| Electronic financial network | FAIL | 4,434,106 | 0.39% | Very high | `거래금액 <= 1,000,000` covers 98.97% of rows with zero positives. |

## Card Transactions

Key failures and warnings:

- `T0.1`: source-cited distributed scripts concatenate supplied splits and
  perform a new random stratified split.
- `T1.1`: amount-only ROC-AUC is `0.9519`. This is marginal against the `0.95`
  threshold; the card verdict does not depend on this gate alone.
- `T1.2` sensitivity: the stdlib screening threshold is crossed, but the
  LightGBM amount/no-ID PR-AUC ratio is `0.6631` and passes. Do not use T1.2 as
  public evidence.
- `T1.3` sensitivity: the training-selected `통합승인금액 >= 318000` rule
  reaches validation F1 `0.7204`, but only `0.7498x` the LightGBM best F1 and
  therefore passes the relative gate. Do not use T1.3 as public evidence.
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

- `T0.1`: source-cited distributed scripts concatenate supplied splits and
  perform a new random stratified split.
- `T1.1`: amount-only ROC-AUC is `0.9969`.
- `T1.2` sensitivity: the LightGBM amount/no-ID PR-AUC ratio is `0.7195` and
  passes. The stdlib ratio is not used as public evidence.
- `T2`: `거래금액=4000000` alone captures `30.05%` of fraud rows with `88.13x`
  lift.
- `T3`: `거래금액` class-distribution overlap is only `0.0065`.
- `T5`: `거래금액 <= 1,000,000` covers `4,388,368` rows, or `98.97%`
  of the dataset, with zero positives.
- `T6.1`: duplicate feature rows excluding labels and configured IDs account for
  `52.30%` of rows (`2,319,072` rows).
- `T6.2`: `1,399` rows belong to identical non-ID feature groups with mixed
  labels.
- `T9.1`: `거래금액` has only `48` distinct values.
- `T9.2`: the top 10 `거래금액` values cover `98.05%` of rows.
- `T9.3`: `거래금액` is rounded to 1,000-unit multiples for `99.91%` of rows.

## Cross-Dataset Check

The same protocol yields a graded comparison:

- `K-Claims-Synth v0.3` test fixture: wiring checks `PASS`; external realism untested
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
card subset remains concerning, but should be presented as corroborating
evidence rather than the lead exhibit.

The audit covers the released training and validation files, approximately 90%
of the total labeled rows stated on the AI Hub page. It does not claim coverage
of an unavailable or unconfigured test portion.

The dataset may still be useful for ingestion demos, imbalance handling
examples, or audit-method development. It is weak evidence for behavior-level
fraud detection model quality.
