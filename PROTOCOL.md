# Fraud Dataset Validity Protocol

This protocol audits whether a fraud-detection dataset can support benchmark
claims. It does not ask whether a model can score well. It asks whether the
score requires learning fraud behavior rather than exposed shortcuts.

## Verdicts

- `PASS`: no fail or warning gates fired
- `WARN`: no fail gates fired, but at least one warning gate fired
- `FAIL`: at least one fail gate fired

`INFO` tests are recorded for transparency and do not affect the verdict.

## Required Config Fields

- `label_col`: observed training label
- `oracle_label_col`: optional scoring label used when available
- `positive_values`: values treated as positive labels
- `leak_cols`: label explanations or fields unavailable at decision time
- `id_cols`: account, card, user, merchant, transaction, or sequence IDs
- `entity_holdout_col`: optional, explicitly selected repeated entity used for
  deterministic cold-start holdout; row or transaction identifiers are invalid
- `date_cols`: event dates or timestamps
- `amount_cols`: monetary fields for amount-specific checks
- `overlap_cols`: optional important columns for distribution-overlap checks
- `numeric_cols`: amount and other continuous/count fields
- `splits`: named train, validation, or test file groups

## Implemented Tests

### T0. Evaluation Integrity

Audits published validation metadata when supplied in the config.

Default fail:

- published model path concatenates supplied splits and performs a new random
  split

Default warnings:

- date columns exist but no temporal holdout is recorded
- entity ID columns exist but no entity holdout is recorded

### T1. Amount-Only Baseline

Measures whether amount alone explains the label.

Default fails:

- amount-only ROC-AUC >= `0.95`
- amount-only PR-AUC is at least `80%` of no-ID PR-AUC
- a one-sided amount threshold selected on the training split reaches F1 >=
  `0.70` on the unchanged validation split and at least `80%` of the no-ID
  baseline's best validation score-threshold F1

The training-only threshold selection prevents validation leakage. The optional
LightGBM sensitivity analysis should be consulted before a ratio-based T1.2 or
T1.3 result is used publicly.

With the default dependency-free evidence Naive Bayes reference, triggered T1.2
and T1.3 ratio gates are `WARN` screening results rather than final `FAIL`
evidence. A stronger frozen reference model is required to confirm them.

### T2. Single-Feature Shortcut

Searches for a single non-leak, non-ID value that is highly predictive.

Default fail:

- support >= `100` rows
- positive rate >= `50%`
- lift >= `20x`
- or recall >= `10%` and lift >= `5x`

Default warning:

- recall >= `20%` and lift >= `3x`

### T3. Class Distribution Overlap

Computes overlap between positive and negative distributions on configured
important columns. Numeric columns are binned before overlap is measured.

Default fail:

- lowest checked overlap <= `0.05`

Default warning:

- lowest checked overlap <= `0.20`

### T4. ID Memorization

Compares ID-only performance to no-ID performance and evaluates deterministic
entity holdout only when an explicit repeated entity column exists. Unique row
identifiers do not produce an entity-holdout result. Entity-holdout degradation
uses AP-lift, defined as average precision divided by fraud prevalence, before
ratio-ing across test sets.

Default fail:

- ID-only PR-AUC ratio >= `0.80` and ID-only lift over prevalence >= `3.0`
- entity-holdout AP-lift ratio <= `0.50`

Default warning:

- ID-only PR-AUC ratio >= `0.50` and ID-only lift over prevalence >= `1.5`
- entity-holdout AP-lift ratio <= `0.75`

### T5. Zero-Fraud Low-Amount Region

Finds the largest low-amount prefix with zero positive labels on configured
amount columns. This v0.1 test is intentionally narrower than a full numeric
quantile-region scan.

Default fail:

- zero-fraud region covers at least `90%` of rows

Default warning:

- zero-fraud region covers at least `50%` of rows

### T6. Duplicate Rows

Checks exact duplicate feature rows and duplicate feature groups with mixed
labels.

Default fail:

- duplicate feature rows >= `5%`
- label-conflict rows >= `0.1%`

Default warning:

- duplicate feature rows >= `1%`
- any label-conflict rows

### T7. Temporal Degradation

Compares temporal-holdout no-ID AP-lift to provided-split no-ID AP-lift when a
temporal holdout can be inferred. AP-lift normalization avoids comparing raw
average precision across splits with different fraud prevalence.

Default fail:

- temporal/provided AP-lift ratio <= `0.50`

Default warning:

- temporal/provided AP-lift ratio <= `0.75`

### T8. Leakage Review

Checks configured leak-column exclusion and suspicious label/post-outcome feature
names. It also warns on feature names that look like entity-level aggregate
rates, risks, or scores because those often represent target-encoded leakage
unless computed from prior-period data only.

Default fail:

- a configured leak column remains in features
- a feature name matches the suspicious leakage-name pattern

Default warning:

- a feature name matches the entity aggregate rate/risk/score pattern

### T9. Amount Cardinality Sanity

Checks whether monetary fields are unrealistically discrete or concentrated.

Default fails:

- amount field has at most `100` distinct values
- top 10 amount values cover at least `90%` of rows

Default warnings:

- top 10 amount values cover at least `70%` of rows
- at least `95%` of values are multiples of 1,000

### T10. Label-Noise Plausibility

When both observed and oracle labels exist, measures their mismatch rate.

Default fail:

- noise rate <= `0%`
- noise rate >= `50%`

Default warning:

- noise rate < `1%`
- noise rate > `30%`

Datasets without a separate oracle label receive `INFO`.

## Output

Each audit writes:

- `audit.json`: machine-readable metrics, thresholds, tests, and red flags
- `audit.md`: stakeholder-readable report

## Interpretation

High ROC-AUC or F1 is not proof of benchmark quality. It may mean the label can
be recovered from an exposed feature. A stronger fraud benchmark has overlap
between normal and fraud distributions, requires combinations of signals, and
holds up under temporal and entity-holdout evaluation.
