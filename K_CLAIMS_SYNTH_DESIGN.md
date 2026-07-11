# K-Claims-Synth Design Notes

`K-Claims-Synth` is a deterministic insurance-claim fraud test fixture produced
by `k_claims_synth.py`.

The fixture is released through the generator and audit reports. Raw CSV
outputs are local artifacts and are not committed.

## Current Status

`K-Claims-Synth v0.3` passes two independent gates:

1. The T0-T10 shortcut-validity protocol must return `PASS`.
2. A frozen LightGBM model must meet versioned learnability and holdout
   thresholds in `k_claims_fixture_acceptance.json`.

This closes the v0.2 gap: v0.2 avoided trivial shortcuts but was nearly
unlearnable. V0.3 only demonstrates that the harness can exercise a nontrivial
synthetic task. Because the risk function and labels are authored here, model
performance is circular evidence and must not be presented as insurance-model
quality or benchmark realism.

## Changes From v0.2

- Added explicit learnability floors and an upper ROC-AUC ceiling.
- Added decision-time, prior-only behavioral fields:
  - `claim_lag_days`
  - `provider_prior_same_pair_count_365d`
  - `customer_prior_same_provider_count_365d`
- Strengthened fraud signal through multi-feature interactions rather than a
  single amount, code, provider, or customer identifier.
- Seeded one year of unlabeled provider history before the scored window begins so
  rolling features do not start at an artificial zero.
- Evaluated one frozen model on validation, future-period, and unseen-provider
  splits.

## Design Invariants

- Amount alone must remain uninformative.
- No single feature value may meet the recall-weighted shortcut failure gate.
- Numeric class distributions must retain substantial overlap.
- IDs are excluded from the reference model.
- Provider and customer aggregates use only events before the current claim.
- Training uses noisy investigation outcomes.
- Scoring uses the held-out oracle label.
- Future-period and unseen-provider performance must remain useful.
- Validation ROC-AUC above 0.90 fails the acceptance gate as suspiciously easy.

## Observable Fraud Mechanisms

The oracle probability is driven by combinations of weak, decision-time
signals:

- false hospitalization: medical product, longer stay, and a mature provider
  history
- accident-detail manipulation: auto or travel product, long reporting lag,
  and a relatively new policy
- provider collusion: repeated diagnosis-treatment pairs, prior high-amount
  share, and sufficient prior provider volume
- duplicate or staged claim: repeated recent claims, longer claim history, and
  digital-channel or repeated-provider behavior
- disclosure-duty violation: newer policy, older customer, and prior claims

Each component also appears in legitimate claims. Fraud probability rises when
components co-occur; no component is a direct label rule.

## Historical Warmup

The generator creates one year of unlabeled provider events before 2024. These
events are used only to initialize rolling 365-day features and are not included
in the scored fixture rows.

Without this warmup, early rows had zero provider history while late rows had
mature histories. That artifact doubled late-period prevalence and caused a
spurious temporal warning. Warmup makes the observation window stationary
without using future information.

## Labels

- `oracle_fraud_label` is sampled from the multi-mechanism risk function.
- `observed_fraud_label` simulates investigation outcomes with 40% false
  negatives and 0.2% false positives among oracle-negative claims.
- `fraud_type` is excluded from all model features.

The resulting full-dataset rates are:

- oracle positive rate: `3.27%`
- observed positive rate: `2.22%`
- observed/oracle mismatch rate: `1.49%`

## Fixture Diagnostics

The values below are regression targets for test wiring. They are not empirical
estimates of performance on Korean insurance claims.

| check | result | threshold |
|---|---:|---:|
| T0-T10 validity verdict | PASS | PASS |
| Validation ROC-AUC | 0.7463 | 0.70-0.90 |
| Validation AP lift | 5.6064 | >= 4.0 |
| No-ID AP / amount-only AP | 5.2483 | >= 2.0 |
| Validation top-1% lift | 13.4669 | >= 4.0 |
| Temporal ROC-AUC | 0.7440 | >= 0.65 |
| Temporal AP lift | 4.3930 | >= 3.0 |
| Unseen-provider ROC-AUC | 0.7509 | >= 0.65 |
| Unseen-provider AP lift | 4.6294 | >= 3.0 |

Supporting reports:

- `reports/k_claims_synth/audit.md`
- `reports/k_claims_synth/lightgbm_sensitivity.md`
- `reports/k_claims_synth/fixture_acceptance.md`

## Remaining Limits

- Feature distributions are plausible by construction, not calibrated against
  a private insurer population.
- Fraud mechanisms are stylized and do not cover investigation workflow,
  recoveries, legal outcomes, or network evidence outside the claim table.
- External practitioners have not yet reviewed the schema or thresholds.
- The fixture must not be called an insurance benchmark until its distributions,
  mechanisms, and effect sizes are calibrated against defensible external or
  private insurance evidence.
