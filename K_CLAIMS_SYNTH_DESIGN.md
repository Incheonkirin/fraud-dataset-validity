# K-Claims-Synth Design Notes

`K-Claims-Synth` is a deterministic insurance-claim fraud benchmark prototype
produced by `k_claims_synth.py`.

The benchmark is released through the generator and audit report. Raw CSV
outputs are local artifacts and are not committed.

## Current Status

`K-Claims-Synth v0.2` is a prototype that passes the shortcut-solvability
protocol. It is not yet claimed as a finished replacement benchmark.

## Changes From v0.1

- Removed `provider_claim_rate`, which was a quasi-leaky encoding of latent
  provider risk.
- Added prior-period provider pattern fields:
  - `provider_prior_claim_count_365d`
  - `provider_prior_high_amount_share_365d`
- Switched entity holdout from `customer_id` to `provider_id`.
- Flipped investigation-label noise toward high false negatives and low false
  positives.
- Removed oracle-after-the-fact mutation of `prior_claim_count_30d`.
- Added mild strategy drift while keeping the self-application gate passing.

## Implemented Design Goals

- Normal and fraud distributions overlap on checked single features.
- No single amount, code, provider, or customer ID solves the task.
- Fraud arises from combinations of weak behavioral signals rather than direct
  amount thresholds.
- Random validation, temporal holdout, and provider holdout behavior are
  reported.
- Training labels are noisy investigation outcomes.
- Scoring labels use a held-out oracle label.

## Schema

- `claim_id`
- `policy_id`
- `customer_id`
- `provider_id`
- `claim_date`
- `accident_date`
- `product_type`
- `diagnosis_code`
- `treatment_code`
- `hospital_days`
- `claim_amount`
- `customer_age`
- `policy_age_days`
- `prior_claim_count_30d`
- `prior_claim_count_365d`
- `provider_prior_claim_count_365d`
- `provider_prior_high_amount_share_365d`
- `region`
- `channel`
- `observed_fraud_label`
- `oracle_fraud_label`
- `fraud_type`

## Fraud Mechanisms

The generator combines overlapping weak signals:

- false hospitalization
- accident-detail manipulation
- provider collusion
- duplicate or staged claim
- disclosure-duty violation

The oracle label is sampled from a noisy risk function over combinations of
timing, prior provider patterns, claim history, policy age, claim lag, treatment
shape, and mild temporal drift. The observed label then simulates investigation
outcomes with false negatives more common than false positives.

## Self-Application Gate

The generated 100,000-row v0.2 dataset passes the same protocol used on AI Hub,
ULB, and BAF.

Key audit results:

- Verdict: `PASS`
- Oracle fraud rate: `1.75%`
- Observed fraud rate: `1.33%`
- Observed/oracle label-noise rate: `1.05%`
- Amount-only ROC-AUC: `0.5387`
- Amount-only / no-ID PR-AUC ratio: `0.5924`
- T2 single-feature shortcut: `PASS`
- T7 AP-lift temporal ratio: `1.017`
- `claim_amount` distinct values: `99,227`
- Top 10 `claim_amount` share: `0.11%`

Report: `reports/k_claims_synth/audit.md`
