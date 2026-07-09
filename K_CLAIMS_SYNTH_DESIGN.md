# K-Claims-Synth Design Notes

`K-Claims-Synth` is a deterministic insurance-claim fraud benchmark produced by
`k_claims_synth.py`.

The benchmark is released only through the generator and audit report. Raw CSV
outputs are local artifacts and are not committed.

## Implemented Design Goals

- Normal and fraud distributions overlap on checked single features.
- No single amount, code, provider, or customer ID solves the task.
- Fraud arises from mechanisms, not direct amount thresholds.
- Random validation, temporal holdout, and entity-holdout behavior are reported.
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
- `provider_claim_rate`
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
timing, provider pattern, claim history, policy age, claim lag, and treatment
shape. The observed label then adds false negatives and false positives.

## Self-Application Gate

The generated 100,000-row v0.1 dataset passes the same protocol used on AI Hub,
ULB, and BAF.

Key audit results:

- Verdict: `PASS`
- Oracle fraud rate: `2.63%`
- Observed fraud rate: `4.09%`
- Observed/oracle label-noise rate: `2.15%`
- Amount-only ROC-AUC: `0.5119`
- Largest zero-positive low-amount region: `0.09%` of rows
- `claim_amount` distinct values: `99,191`
- Top 10 `claim_amount` share: `0.10%`

Report: `reports/k_claims_synth/audit.md`
