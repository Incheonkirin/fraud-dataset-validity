# Insurance FDS Rebuild Preparation

## Objective

Prepare a reusable evaluation spine before the internal insurance FDS rebuild
begins. The target is not a particular model family. It is a system that can
tell whether a new graph, sequence, tabular, or language-model component creates
better investigation decisions under real label and capacity constraints.

The central thesis is:

> A new insurance FDS must be label-honest and evidence-first: it must account
> for selective investigation labels, delayed outcomes, fixed investigation
> capacity, temporal drift, and organized entity relationships before model
> architecture comparisons are trusted.

## Why This Comes Before Architecture

Historical investigation outcomes are not an independently labeled sample.
Cases were selected by earlier rules and investigator judgment. Uninvestigated
claims are mostly unknown rather than confirmed negative. Confirmed outcomes
also mature over months. A random split and ordinary F1 can therefore reward a
new model for reproducing the previous selection policy.

Graph, sequence, and language-model components remain candidates, but they plug
into this evaluation spine instead of defining the project.

## WS0: Label-Honest Evaluation Sandbox

### Event Schema

The sandbox must distinguish claim events from label-observation events:

- `claim_id`, `claim_time`, claimant, provider, broker, accident, and policy IDs
- decision-time structured and unstructured evidence
- legacy rule score and historical investigation policy decision
- `selected_for_investigation_at`
- investigation stages and evidence timestamps
- provisional outcome, confirmed outcome, and confirmation timestamp
- recovery or prevented-loss amount when available
- oracle label only in simulation, never assumed in production

Every feature and label is reconstructed as-of the scoring timestamp.

### Selective-Label Simulation

K-Claims may simulate an historical policy `pi_0(x)` that investigates cases
non-randomly. At minimum, include:

- legacy-rule selection concentrated on familiar fraud patterns
- investigator overrides
- a small randomized exploration bucket with recorded propensity
- capacity truncation at a fixed daily or weekly alert budget

The current independent false-negative flip is insufficient because it models
noise but not selection bias.

### Delayed-Label Simulation

Generate outcome delays by case type and severity. Training and evaluation
snapshots must exclude outcomes unavailable at the snapshot date. Report
results by label-maturity window rather than treating recent unlabeled cases as
negative.

### Required Metrics

Primary metrics reflect an investigation worklist:

- precision at fixed capacity `K`
- catch rate at `K`
- fraud amount or expected loss captured at `K`
- alerts required per confirmed case
- calibration within score bands
- performance on novel providers, claimants, and time periods
- stability and confidence intervals across monthly backtests

ROC-AUC and global F1 remain diagnostic metrics only.

### Bias-Aware Evaluation Candidates

Compare at least four estimates against the simulation oracle:

1. naive evaluation on investigated cases only
2. inverse-propensity weighting where propensities are known
3. self-normalized inverse-propensity weighting
4. a doubly robust estimator using an outcome model

Reject inference without defensible assumptions must be labeled sensitivity
analysis, not ground truth recovery.

### WS0 Acceptance Test

WS0 is complete only when:

- a biased historical policy produces a materially biased naive model ranking;
- the correction method recovers oracle precision-at-K or value-at-K within a
  predeclared tolerance and bootstrap interval across multiple seeds;
- the result survives policy, capacity, delay, and fraud-prevalence stress tests;
- failure cases are reported instead of tuned away.

Synthetic model ROC-AUC is not a WS0 success criterion.

## WS1: Harness Reliability

- require an explicitly configured repeated entity for entity holdout
- exclude IDs from duplicate-feature and label-conflict hashes
- use tie-safe average precision
- add bootstrap confidence intervals and repeated temporal backtests
- distinguish measured tests from source-derived metadata assertions
- run official model packages before making model-dependence claims

## WS2: Replaceable Model Components

Once WS0 is trustworthy, compare components on the same as-of snapshots and
worklist metrics:

- tabular baseline with prior-only aggregates
- claim and provider event sequences
- claimant-provider-broker-accident heterogeneous graph features
- language-model extraction of evidence from medical records and statements
- late fusion and investigator-facing evidence summaries

The LLM may extract or summarize evidence, but it must not invent the fraud
decision or obscure source provenance.

## WS3: Production Transition

When internal data becomes available:

1. map actual label states and timestamps before training a model;
2. reproduce the legacy selection policy and capacity constraints;
3. establish chronological and unseen-entity backtests;
4. reserve a controlled exploration stream where governance allows it;
5. compare model families using the same worklist and value metrics;
6. monitor score, entity, label-maturity, and investigator-feedback drift.

## Stop Conditions

- If investigation selection and outcome timestamps cannot be reconstructed,
  do not claim unbiased offline model superiority.
- If no exploration or defensible propensity estimate exists, report partial
  identification or sensitivity bounds rather than a corrected point estimate.
- If a component improves random-split F1 but not temporal value-at-K, reject it.
- If graph or language-model components add no stable incremental value over a
  prior-only tabular baseline, remove them.

## Current Artifact Roles

- AI Hub case study: completed transaction-data shortcut example, not insurance
  evidence
- validity harness: model-validation utility under active repair
- K-Claims-Synth: pipeline and estimator test fixture, not an insurance benchmark
- ULB and BAF: external software-behavior anchors, not Korean insurance anchors
- internal rebuild: the only setting where operational insurance performance can
  eventually be established
