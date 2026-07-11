# Fraud Dataset Validity Harness

Dependency-free audits for fraud-detection datasets.

The harness checks whether a dataset can support model-validity claims, or
whether high scores can be explained by exposed shortcuts such as amount
buckets, single category values, ID artifacts, duplicate rows, label leakage, or
weak split design.

## What Is Implemented

- `T0` evaluation-integrity metadata checks
- `T1` amount-only baseline checks
- `T2` single-feature shortcut checks
- `T3` class distribution overlap checks
- `T4` ID memorization and entity-holdout checks
- `T5` zero-fraud low-amount region checks
- `T6` duplicate and label-conflict checks
- `T7` temporal degradation checks
- `T8` leak-column, post-outcome feature, and entity-aggregate review
- `T9` amount-cardinality sanity checks
- `T10` observed/oracle label-noise plausibility checks
- Markdown and JSON audit reports
- deterministic `K-Claims-Synth` test fixture with observed and oracle labels
- optional frozen LightGBM sensitivity analysis for ratio-based gates
- explicit K-Claims fixture learnability gate

Thresholds are stored in `thresholds.yaml`.
The stdlib reference model is described in `reference_model.yaml`.
The optional LightGBM settings are described in `lightgbm_sensitivity.json`.

## Quick Start

```bash
python3 fdvh.py \
  --config configs/aihub_fds_eft.json \
  --out reports/aihub_fds_eft
```

Configs may use environment variables in file paths. For local AI Hub data:

```bash
export AIHUB_FDS_ROOT="/absolute/path/to/3.개방데이터/1.데이터"

python3 fdvh.py \
  --config configs/aihub_fds_card.json \
  --out reports/aihub_fds_card
```

Each run writes:

- `audit.md`
- `audit.json`

## LightGBM Sensitivity

The default audit remains dependency-free. Before publishing a ratio-based T1
finding, run the stronger optional denominator:

```bash
python3 -m pip install -r requirements-sensitivity.txt

python3 scripts/lightgbm_sensitivity.py \
  --config configs/aihub_fds_eft.json \
  --audit-json reports/aihub_fds_eft/audit.json \
  --out reports/aihub_fds_eft
```

This writes `lightgbm_sensitivity.md` and `lightgbm_sensitivity.json` without
changing the dependency-free default verdict report.

## K-Claims-Synth

Generate the synthetic insurance-claim test fixture:

```bash
python3 k_claims_synth.py \
  --rows 100000 \
  --out data_generated/k_claims_synth

export K_CLAIMS_SYNTH_ROOT="$PWD/data_generated/k_claims_synth"

python3 fdvh.py \
  --config configs/k_claims_synth.json \
  --out reports/k_claims_synth
```

Run the learnability and holdout acceptance gate after the validity audit:

```bash
python3 scripts/lightgbm_sensitivity.py \
  --config configs/k_claims_synth.json \
  --audit-json reports/k_claims_synth/audit.json \
  --out reports/k_claims_synth

python3 scripts/check_fixture_acceptance.py \
  --audit-json reports/k_claims_synth/audit.json \
  --sensitivity-json reports/k_claims_synth/lightgbm_sensitivity.json \
  --out reports/k_claims_synth
```

The included reports show that `K-Claims-Synth v0.3` is useful for exercising
both shortcut and learnability checks. Its authored labels and uncalibrated
distributions are not evidence of insurance benchmark realism or model quality.

## External Anchors

Kaggle credentials are required for BAF and ULB downloads.

```bash
kaggle datasets download -d mlg-ulb/creditcardfraud \
  -p data_external/kaggle/ulb_creditcard --unzip

kaggle datasets download -d sgpjesus/bank-account-fraud-dataset-neurips-2022 \
  -p data_external/kaggle/baf --unzip

python3 scripts/prepare_kaggle_anchors.py

export FDVH_ANCHOR_ROOT="$PWD/data_generated/anchors"

python3 fdvh.py --config configs/ulb_creditcard.json --out reports/ulb_creditcard
python3 fdvh.py --config configs/baf_base.json --out reports/baf_base
```

The included reports show ULB Credit Card Fraud and BAF Base receiving `WARN`
verdicts, while the local test fixture passes and the AI Hub FDS datasets fail.
This graded spectrum is summarized in `ANCHOR_COMPARISON.md`.

## Current Results

Start with `CASE_STUDY.md`. Supporting results are in `ANCHOR_COMPARISON.md`,
`RESULT_SUMMARY.md`, and `AIHUB_MODEL_SOURCE_EVIDENCE.md`.

## Scope

This project does not try to build the best fraud model. It provides shortcut
linting and holdout stress tests before model comparisons begin. Passing these
checks is necessary but does not establish external realism.
