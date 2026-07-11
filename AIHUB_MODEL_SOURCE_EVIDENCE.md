# AI Hub Model Source Evidence

Evidence review date: 2026-07-11 KST

Source artifact: `(21-26) AI 모델.zip`, distributed with the AI Hub dataset
`이상 판별을 위한 금융거래 정보 및 사용자 패턴 합성데이터`.

The source package is not redistributed in this repository. Paths below are
relative to the extracted package. SHA-256 values identify the reviewed files.

## Detection Evaluation Path

### Card detection

File:
`1.모델소스코드/카드_이상_거래_탐지_모델/anomaly_detection.py`

SHA-256:
`6548277b095e5e1942d6711b67b3c3c309049eaa8babd40fdac38bb30b3e6530`

- Lines 134-137 load the supplied train, validation, and test datasets and
  concatenate them into one dataframe.
- Lines 194-204 preprocess the concatenated dataframe and then call `split_df`.

File: `1.모델소스코드/카드_이상_거래_탐지_모델/utils.py`

SHA-256:
`7ad3f491e1a1c29d0e63f7de316c1e566546e44862b9582a74e284cdad77487d`

- Lines 75-78 define `split_df` as a stratified `train_test_split` with
  `random_state=42`.
- Lines 109-145 factorize account and object values on the dataframe supplied
  before the new split.

### Electronic financial network detection

File:
`1.모델소스코드/전자금융공동망_이상_거래_탐지_모델/anomaly_detection.py`

SHA-256:
`7fa38fa2d6c65368fc3308559e900e11bcae8c2bc6b11e0a2908ce30733c8113`

- Lines 129-132 load the supplied train, validation, and test datasets and
  concatenate them into one dataframe.
- Lines 172-183 preprocess the concatenated dataframe and then call `split_df`.
- The repeated `args.train_dataset` checks on lines 125-127 appear to be a code
  defect, but do not change the concat-then-resplit finding when all paths exist.

File:
`1.모델소스코드/전자금융공동망_이상_거래_탐지_모델/utils.py`

SHA-256:
`e609b2cde1b8bd5e351904b767fb47e96a7042acd0201faf2f7216308934d521`

- Lines 81-84 define `split_df` as a stratified `train_test_split` with
  `random_state=42`.
- Lines 115-151 factorize account and object values on the dataframe supplied
  before the new split.

## Published Feature Sets

Card detection file:
`1.모델소스코드/카드_이상_거래_탐지_모델/meta.py`

SHA-256:
`dd0474cfee843e8d7f6a7f8deb6b8430ea0608f231f4e8e24d42de9c509ca468`

- Lines 5-35 define card and merchant IDs plus fields including
  `통합승인금액`, `승인거래코드`, `가맹점승인업종코드`, and
  `일시불할부구분코드`.

Electronic financial network detection file:
`1.모델소스코드/전자금융공동망_이상_거래_탐지_모델/meta.py`

SHA-256:
`6ff03bbc2d5dad029b2eacf3d50b89ef6bf5e6481c9ab66aaeb8439d43753009`

- Lines 5-17 define source and target account IDs plus `거래금액`, `자금구분`,
  `매체구분`, and financial-institution IDs.

## Type Classification Scope

- Card classification
  `1.모델소스코드/카드_이상_거래_유형_분류_모델/classification.py`, line 148,
  filters to four anomaly-type codes before fitting or evaluation.
- Electronic financial network classification
  `1.모델소스코드/전자금융공동망_이상_거래_유형_분류_모델/classification.py`,
  lines 141-142, normalizes and filters to six anomaly-type codes.

These classification scores answer which anomaly type a selected anomaly row
belongs to. They are not normal-versus-anomaly detection results.

## Interpretation Boundary

The source evidence establishes the evaluation path used by the distributed
scripts. It does not establish how the original data-generation process was
implemented. Claims about label-generation structure therefore rely on the
released data distributions, not on undocumented generator internals.
