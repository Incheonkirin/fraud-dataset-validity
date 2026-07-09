# Fraud Dataset Validity Harness

Small, dependency-free audits for fraud-detection datasets.

The harness checks whether a dataset can support model-validity claims, or
whether high scores can be explained by exposed shortcuts such as amount
buckets, single category values, ID artifacts, or weak split design.

## What v0.1 Implements

- `T0` evaluation-integrity metadata checks
- `T1` amount-only baseline checks
- `T2` single-feature shortcut checks
- `T5` zero-fraud low-amount region checks
- `T9` amount-cardinality sanity checks
- provided-split and temporal Naive Bayes baselines
- Markdown and JSON audit reports

Thresholds are stored in `thresholds.yaml`.

## Quick Start

```bash
python3 fdvh.py \
  --config configs/aihub_fds_eft.json \
  --out reports/aihub_fds_eft
```

Configs may use environment variables in file paths. For the AI Hub FDS case
study:

```bash
export AIHUB_FDS_ROOT="/path/to/3.개방데이터/1.데이터"

python3 fdvh.py \
  --config configs/aihub_fds_card.json \
  --out reports/aihub_fds_card

python3 fdvh.py \
  --config configs/aihub_fds_eft.json \
  --out reports/aihub_fds_eft
```

Each run writes:

- `audit.md`
- `audit.json`

## Current Case Study

The included reports audit the AI Hub dataset titled:

`이상 판별을 위한 금융거래 정보 및 사용자 패턴 합성데이터`

Both transaction subsets fail the v0.1 protocol:

- Card transactions fail amount-only and single-feature shortcut checks.
- Electronic financial network transactions fail amount-only, zero-fraud
  region, and amount-cardinality checks.

See `RESULT_SUMMARY.md` and the generated reports under `reports/`.

## Adding A Dataset

Create a config with:

- label column and positive label values
- leak columns that should never be used as features
- ID columns
- date columns
- amount columns
- numeric columns
- one or more named splits

Then run `fdvh.py` with the config path.

## Scope

This project does not try to build the best fraud model. It tests whether a
dataset is a credible benchmark before model comparisons begin.
