# When a Fraud Benchmark Can Be Solved by Its Amount Template

## Executive Finding

I audited the released training and validation portions of AI Hub dataset 71925,
`이상 판별을 위한 금융거래 정보 및 사용자 패턴 합성데이터`. AI Hub
describes the dataset as high-quality synthetic financial transactions for
training and validating anomaly-detection models.

The electronic financial network subset is not a credible benchmark for
behavior-level anomaly detection in its current form. Its released labels are
dominated by a discrete amount template:

- 4,388,368 rows, 98.97% of the audited subset, have amount at or below
  KRW 1,000,000 and contain zero positive labels.
- The 4,434,106 audited rows use only 48 distinct transaction amounts.
- The 10 most common amounts cover 98.05% of rows.
- Amount-only ROC-AUC is 0.9969 on the supplied train/validation split.
- The positive and negative amount distributions have overlap 0.0065.

These findings do not show that amount is irrelevant to real fraud. They show
that this released synthetic subset can be solved largely by recovering its
amount template, without demonstrating generalization to evolving customer or
account behavior.

## Scope

The audit covers the released training and validation files available in the
local download:

| subset | audited rows | positives | positive rate |
|---|---:|---:|---:|
| Electronic financial network | 4,434,106 | 17,175 | 0.39% |
| Card | 1,952,871 | 72,008 | 3.69% |

AI Hub reports 7,096,642 labeled rows across all published splits. The 6,386,977
rows audited here are approximately 90% of that total. This case study does not
claim to have audited an unavailable or unconfigured test portion.

## Why a Published Model Does Not Resolve the Problem

The distributed detection source does not preserve the supplied evaluation
split. Both card and electronic financial network scripts load train,
validation, and test datasets, concatenate them, preprocess the combined data,
and perform a new random stratified split.

Package-relative file names, exact line ranges, and SHA-256 values are recorded
in `AIHUB_MODEL_SOURCE_EVIDENCE.md`. The source package itself is not
redistributed here.

A model can therefore achieve a strong score by learning stable synthetic
shortcuts shared across the reconsolidated rows. The existence of a trained
model is evidence that the dataset is learnable; it is not evidence that the
learned decision rule represents deployable fraud behavior.

## Model Sensitivity: The Criticism That Was Valid

The first harness version used a dependency-free evidence Naive Bayes model as
the no-ID reference. That denominator was too weak for ratio-based conclusions.
A frozen LightGBM sensitivity run changed both AI Hub T1.2 results:

| subset | LightGBM no-ID PR-AUC | amount-only PR-AUC | amount/no-ID ratio | T1.2 |
|---|---:|---:|---:|---:|
| Card | 0.9935 | 0.6640 | 0.6683 | PASS |
| Electronic financial network | 0.6161 | 0.4600 | 0.7466 | PASS |

The amount-rule-to-model F1 ratio also passes under LightGBM for both subsets.
Those two ratio gates must not be used as the public basis for failure.

The electronic financial network verdict still has seven independent FAIL
gates: published split integrity, amount-only ROC-AUC, recall-weighted
single-value shortcut, distribution overlap, zero-positive low-amount region,
amount cardinality, and top-10 amount concentration.

The card verdict is weaker. It retains published split-integrity failure, a
marginal amount-only ROC-AUC failure at 0.9519, and a single-value shortcut:
`가맹점누적매출금액_구간화=3` captures 58.18% of positive rows at 6.22x lift.
Card should be treated as corroborating evidence, not the lead case.

## Comparison Datasets

The same protocol produces a graded result rather than failing every dataset:

| dataset | protocol verdict | LightGBM amount/no-ID AP ratio |
|---|---:|---:|
| K-Claims-Synth v0.3 | PASS | 0.1905 |
| ULB Credit Card Fraud | WARN | 0.0033 |
| BAF Base | WARN | 0.1001 |
| AI Hub Card | FAIL | 0.6683 |
| AI Hub Electronic Financial Network | FAIL | 0.7466 |

ULB and BAF warn because of broad single-feature subgroups, not because of
amount templates. K-Claims-Synth v0.3 separately passes a learnability gate:
validation ROC-AUC 0.7463, temporal ROC-AUC 0.7440, and unseen-provider ROC-AUC
0.7509. It remains a synthetic benchmark candidate, not a claim of calibration
to any insurer's private production distribution.

## What the AI Hub Data Can Still Be Used For

The dataset can still support ingestion tests, schema demonstrations, class
imbalance exercises, and examples of why trivial baselines matter. It should
not be used to claim that one behavior-level FDS model is better than another
without first removing or redesigning the shortcut-generating structure.

## Reproduction

Run the dependency-free audit:

```bash
python3 fdvh.py \
  --config configs/aihub_fds_eft.json \
  --out reports/aihub_fds_eft
```

Run the optional frozen LightGBM sensitivity check:

```bash
python3 -m pip install -r requirements-sensitivity.txt

python3 scripts/lightgbm_sensitivity.py \
  --config configs/aihub_fds_eft.json \
  --audit-json reports/aihub_fds_eft/audit.json \
  --out reports/aihub_fds_eft
```

The LightGBM settings and deterministic sample limits are versioned in
`lightgbm_sensitivity.json`.

## Limitations

- The audit covers released training and validation files, not every row stated
  on the AI Hub page.
- The generator implementation is not available, so the audit identifies
  released-data structure rather than assigning a cause inside the generator.
- LightGBM sensitivity uses a deterministic 300,000-row training sample and
  150,000-row evaluation sample for the large subsets; it is a robustness check,
  not hyperparameter tuning.
- Protocol thresholds are versioned design parameters and should be challenged
  and revised with additional datasets.
- A benchmark-validity failure is not a claim about the quality of the source
  institutions' private production data.

## Conclusion

The defensible conclusion is narrow and consequential: the audited electronic
financial network release is unsuitable for comparing behavior-level fraud
detection models because its labels are overwhelmingly recoverable from a
48-value amount template. High model scores on that release require a shortcut
audit before they can be interpreted as fraud-model quality.

[Official AI Hub dataset page](https://www.aihub.or.kr/aihubdata/data/view.do?aihubDataSe=data&currMenu=115&dataSetSn=71925&topMenu=100)
