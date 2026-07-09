# AI Hub FDS Model Package Audit

Audit date: 2026-07-09 KST

Dataset: `이상 판별을 위한 금융거래 정보 및 사용자 패턴 합성데이터`

Verdict: the reference models do not change the dataset verdict.

## What Was Reviewed

- Public data description and usage-guide documents
- Reference model manual
- Extracted reference model source files
- The generated data reports in `reports/`

## Documentation Claims

The public documents describe the dataset as high-quality synthetic financial
transaction data for anomaly-detection model training and validation. The model
manual describes a Graph Feature Preprocessor, SMOTE, and LightGBM pipeline.

The reported validation metrics include:

| task | reported metric |
|---|---:|
| Electronic financial network detection | Minority F1 48.6% |
| Electronic financial network type classification | F1 30.4% |
| Card detection | Minority F1 72.3% |
| Card type classification | F1 86.4% |

## Source-Level Findings

### Detection models use shortcut-prone fields

The card detection model uses fields including:

- `카드KEY`
- `가맹점KEY`
- `승인거래코드`
- `통합승인금액`
- `일시불할부구분코드`
- `가맹점승인업종코드`

The electronic financial network detection model uses fields including:

- `출금계좌일련번호`
- `입금계좌일련번호`
- `거래금액`
- `자금구분`
- `매체구분`

This is not simple inclusion of the label or label-description columns. The
problem is shortcut leakage: ordinary-looking decision-time fields recover much
of the label.

### The published split path is weak

The reference detection scripts load supplied train, validation, and test
folders, concatenate them, and then perform a fresh random stratified split.
That is not a future-period validation and does not test entity cold start.

### Global preprocessing sees the full entity/category universe

Before splitting, the model path factorizes source/target IDs and object
columns across the full concatenated data. This is transductive preprocessing.
It does not directly encode the label, but it weakens the claim that the
validation simulates future transactions.

### Type classification is not detection

The type-classification scripts filter to anomaly-type rows. Those models answer
"given a fraudulent row, which type is it?" They do not validate whether the
dataset supports normal-versus-fraud detection.

## Data-Level Cross-Check

The harness reports the same failure mode numerically:

- Card: a one-sided amount threshold, `통합승인금액 >= 318000`, reaches F1 `0.718`.
  This is close to the official card detection Minority F1 claim of `0.723`.
- Electronic financial network: amount-only PR-AUC exceeds the no-ID baseline
  PR-AUC on the provided split.
- Electronic financial network: `거래금액 <= 1,000,000` covers `98.97%` of rows
  with zero positive labels.
- Electronic financial network: `거래금액` has only `48` distinct values.

## Bottom Line

The existence of reference models is not evidence that the dataset is a credible
fraud-detection benchmark. The model path uses shortcut-bearing fields, relies
on random split validation, and does not report trivial baselines or shortcut
ablation checks.
