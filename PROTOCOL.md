# Fraud Dataset Validity Protocol

This protocol audits whether a fraud-detection dataset is useful as a
benchmark. It does not ask whether a model can score well. It asks whether the
score requires learning fraud behavior.

## Verdicts

- `PASS`: suitable as a benchmark with stated caveats
- `WARN`: useful for demos or teaching, weak for model-validity claims
- `FAIL`: label or split structure is dominated by shortcuts

## Required Config Fields

- `label_col`: binary fraud label
- `positive_values`: values treated as positive labels
- `leak_cols`: label explanations or fields unavailable at decision time
- `id_cols`: account, card, user, merchant, transaction, or sequence IDs
- `date_cols`: event dates or timestamps
- `amount_cols`: monetary fields
- `numeric_cols`: amount and other continuous/count fields
- `splits`: named train, validation, or test file groups

Configs may also include `published_evaluation` metadata for `T0`.

## Implemented Tests

### T0. Evaluation Integrity

Checks whether a published model-validation path respects the stated splits and
uses appropriate holdouts.

Default fail condition:

- published model path concatenates supplied splits and performs a new random
  split

Default warning conditions:

- event-date columns exist, but no temporal holdout is recorded
- entity ID columns exist, but no entity holdout is recorded

### T1. Amount-Only Baseline

Measures whether amount alone explains the label.

Default fail conditions:

- amount-only ROC-AUC is at least `0.95`
- amount-only PR-AUC is at least `80%` of the no-ID baseline PR-AUC
- the best one-sided amount threshold has F1 at least `0.70`

### T2. Single-Feature Shortcut

Searches for a single non-leak, non-ID feature value that is highly predictive
of fraud.

Default fail condition:

- value-level positive rate is at least `50%`
- value-level lift is at least `20x`
- support is at least `100` rows

### T5. Zero-Fraud Low-Amount Region

Finds the largest low-amount prefix with zero positive labels.

Default fail condition:

- zero-fraud region covers at least `90%` of all rows

Default warning condition:

- zero-fraud region covers at least `50%` of all rows

### T9. Amount Cardinality Sanity

Checks whether a monetary field is unrealistically discrete or concentrated.

Default fail conditions:

- amount field has at most `100` distinct values
- top 10 amount values cover at least `90%` of rows

Default warning conditions:

- top 10 amount values cover at least `70%` of rows
- at least `95%` of values are multiples of 1,000

## Planned Tests

The following tests are part of the protocol design but are not yet fully
implemented in v0.1:

- `T3` class distribution overlap across important features
- `T4` ID memorization and entity cold-start evaluation
- `T6` duplicate and near-duplicate row analysis beyond exact hashes
- `T7` temporal degradation against random splits
- `T8` leak-column and post-outcome feature review
- `T10` label-noise plausibility checks

## Output

Each audit writes:

- `audit.json`: machine-readable metrics and tests
- `audit.md`: stakeholder-readable report

## Interpretation

High ROC-AUC or F1 is not proof of benchmark quality. It may mean the label can
be recovered from an exposed feature. A stronger fraud benchmark has overlap
between normal and fraud distributions, requires combinations of signals, and
holds up under temporal and entity-holdout evaluation.
