# Dataset Queue

## Executed Anchors

### ULB Credit Card Fraud

- Source: Kaggle dataset `mlg-ulb/creditcardfraud`
- Local preparation: `scripts/prepare_kaggle_anchors.py`
- Config: `configs/ulb_creditcard.json`
- Report: `reports/ulb_creditcard/audit.md`
- Verdict: `WARN`
- Main warning: broad amount-value shortcut under T2

### BAF Base

- Source: Kaggle dataset `sgpjesus/bank-account-fraud-dataset-neurips-2022`
- Local preparation: `scripts/prepare_kaggle_anchors.py`
- Config: `configs/baf_base.json`
- Report: `reports/baf_base/audit.md`
- Verdict: `WARN`
- Main warning: broad `housing_status=BA` shortcut under T2

## Access-Limited Targets

### IEEE-CIS Fraud Detection

- Kaggle command attempted: `kaggle competitions download -c ieee-fraud-detection`
- Result in this environment: `403`
- Status: not counted as an executed anchor

### PaySim

- Kaggle command attempted: `kaggle datasets download -d ntnu-testimon/paysim1`
- Result in this environment: `403`
- Status: not counted as an executed anchor

## Future Comparison Columns

- Dataset name
- Source / year
- Real vs synthetic
- Rows
- Fraud rate
- Main amount field distinct count
- Amount top-10 share
- Largest zero-positive low-amount region
- Strongest non-ID single-feature lift
- Amount-only PR-AUC
- No-ID full-feature PR-AUC
- Temporal holdout AP-lift ratio
- Entity-holdout AP-lift ratio
- Verdict
