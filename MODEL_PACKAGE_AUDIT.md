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

Evidence status: source-cited. Package-relative paths, line numbers, and SHA-256
values are recorded in `AIHUB_MODEL_SOURCE_EVIDENCE.md`. The distributed source
package is not redistributed in this repository.

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

Both reference detection scripts load supplied train, validation, and test
folders, concatenate them, and then perform a fresh random stratified split.
For card detection this occurs at `anomaly_detection.py:134-137` followed by
`utils.py:75-78`; for electronic financial network detection it occurs at
`anomaly_detection.py:129-132` followed by `utils.py:81-84`. That is not a
future-period validation and does not test entity cold start.

### Global preprocessing sees the full entity/category universe

Before splitting, the model path factorizes source/target IDs and object
columns across the full concatenated data. The relevant ranges are card
`utils.py:109-145` and electronic financial network `utils.py:115-151`. This is
transductive preprocessing.
It does not directly encode the label, but it weakens the claim that the
validation simulates future transactions.

### Type classification is not detection

The type-classification scripts filter to anomaly-type rows at card
`classification.py:148` and electronic financial network
`classification.py:141-142`. Those models answer
"given a fraudulent row, which type is it?" They do not validate whether the
dataset supports normal-versus-fraud detection.

## Data-Level Cross-Check

The harness reports the same failure mode numerically:

- Card: a threshold selected on training, `통합승인금액 >= 318000`, reaches
  validation F1 `0.7204`.
  This is close to the official card detection Minority F1 claim of `0.723`.
- Electronic financial network: amount-only PR-AUC exceeds the stdlib no-ID
  baseline PR-AUC, but not the stronger LightGBM denominator.
- Electronic financial network: `거래금액 <= 1,000,000` covers `98.97%` of rows
  with zero positive labels.
- Electronic financial network: `거래금액` has only `48` distinct values.

## LightGBM Sensitivity

A frozen LightGBM sensitivity analysis materially improves the no-ID reference
denominator:

| dataset | LightGBM no-ID PR-AUC | amount-only PR-AUC | amount/no-ID ratio |
|---|---:|---:|---:|
| Card | 0.9935 | 0.6640 | 0.6683 |
| Electronic financial network | 0.6161 | 0.4600 | 0.7466 |

The stdlib T1.2 screening threshold is crossed, but T1.2 passes under LightGBM
for both datasets. This confirms that `T1.2` and `T1.3` should not carry the
public verdict. The electronic financial network FAIL remains supported
independently by T0.1, T1.1, T2, T3, T5, T9.1, and T9.2. The card FAIL remains
supported by T0.1, the marginal T1.1 result, and T2.

See each report directory's `lightgbm_sensitivity.md`.

## Bottom Line

The existence of reference models is not evidence that the dataset is a credible
fraud-detection benchmark. The model path uses shortcut-bearing fields, relies
on random split validation, and does not report trivial baselines or shortcut
ablation checks.

The strongest public claim is not that every official score is invalid. It is
that the distributed evaluation path does not preserve the supplied splits and
that the electronic financial network labels are dominated by a highly
discrete amount structure. The card finding is corroborating and less decisive.
