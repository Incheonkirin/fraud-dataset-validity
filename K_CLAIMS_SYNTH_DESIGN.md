# K-Claims-Synth Design Notes

`K-Claims-Synth` is the planned insurance-claim fraud benchmark for this
protocol. It should ship only after it passes the same validity harness used on
external datasets.

## Design Goals

- Normal and fraud distributions should overlap on every single feature.
- No single amount, code, provider, or customer ID should solve the task.
- Fraud should arise from mechanisms, not direct label rules.
- Random split, temporal split, and entity-holdout split should be reported
  separately.
- Training labels should be noisy investigation outcomes; scoring labels should
  use a held-out oracle label.

## Candidate Schema

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

Examples of mechanisms to implement:

- false hospitalization: long stays with weak diagnosis/treatment support and
  provider-level repetition
- accident-detail manipulation: unusual lag between accident and claim dates,
  with otherwise ordinary claim amounts
- collusive provider cluster: multiple customers, same provider, similar claim
  shape in a short window
- duplicate or staged claim: repeated claim structure across related policies
- disclosure-duty violation: fraud signal emerges from policy age, claim timing,
  and prior-claim history rather than amount alone

## Validation Gate

The dataset should not be released unless:

- `T1` amount-only tests pass
- `T2` single-feature shortcut tests pass
- `T5` zero-fraud region tests pass
- `T9` cardinality sanity tests pass
- temporal holdout does not collapse relative to random split
- entity-holdout results are reported separately

## v0.1 Target

- 50,000 to 100,000 claims
- 2% to 4% observed fraud rate
- four to five fraud mechanisms
- 24 months of claim dates
- train, validation, temporal test, and entity-holdout test splits
- generator script, schema document, and audit report
