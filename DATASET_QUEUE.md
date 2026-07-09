# Dataset Queue

The next step is to run the same protocol on public fraud datasets and build a
comparison table.

## Priority 1

### BAF / Bank Account Fraud

Reason:

- Public fraud benchmark.
- Designed around fairness and realistic tabular fraud patterns.
- Good contrast against AI Hub FDS because it should not collapse to a raw
  amount threshold.

Needed:

- Local data files.
- Config mapping label, amount, date/time, ID/leak columns.

### PaySim

Reason:

- Common synthetic mobile money fraud dataset.
- Known simulator-based structure, useful as a sanity comparison.

Needed:

- Local CSV.
- Config for `isFraud`, `amount`, transaction type, account IDs, step/time.

### IEEE-CIS Fraud Detection

Reason:

- Widely used Kaggle fraud dataset.
- Has realistic messiness: high-cardinality IDs, missingness, transaction
  amounts, engineered identity fields.

Needed:

- Kaggle data download.
- Config for `isFraud`, `TransactionAmt`, `TransactionDT`, ID/leak fields.

## Priority 2

### Other AI Hub Financial Synthetic Datasets

Reason:

- Same public-data ecosystem.
- Useful for identifying whether the FDS issue is isolated or systemic.

Needed:

- Dataset list.
- Local download.
- Label availability check.

## Comparison Table Columns

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
- Temporal holdout PR-AUC
- Verdict

