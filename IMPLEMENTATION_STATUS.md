# Implementation Status

This file maps the project design requirements to current repository evidence.

| requirement | status | evidence |
|---|---:|---|
| Problem statement explaining why AI Hub FDS is not reliable | Done | `RESULT_SUMMARY.md`, `MODEL_PACKAGE_AUDIT.md` |
| Versioned thresholds rather than informal judgments | Done | `thresholds.yaml` |
| T0 evaluation-integrity audit | Done | `fdvh.py`, AI Hub reports |
| T1 amount-only baseline | Done | `fdvh.py`, all reports |
| T1.3 training-only threshold selection | Done | `fdvh.py`, `tests/test_fdvh.py`, regenerated reports |
| T2 single-feature shortcut test | Done | `fdvh.py`, all reports |
| T3 class distribution overlap | Done | `fdvh.py`, all reports |
| T4 ID memorization and entity holdout | Done | `fdvh.py`, all reports |
| T5 zero-fraud region test | Done | `fdvh.py`, all reports |
| T6 duplicate and label-conflict checks | Done | `fdvh.py`, all reports |
| T7 temporal degradation check | Done | `fdvh.py`; reports show PASS or INFO when no temporal baseline is inferable |
| T8 leak-column/post-outcome review | Done | `fdvh.py`, all reports |
| T9 cardinality sanity | Done | `fdvh.py`, all reports |
| T10 label-noise plausibility | Done | `fdvh.py`, `reports/k_claims_synth/audit.md` |
| External anchors proving the protocol does not fail everything | Done | `reports/ulb_creditcard`, `reports/baf_base`, `ANCHOR_COMPARISON.md` |
| K-Claims-Synth with observed and oracle labels | Done | `k_claims_synth.py`, `configs/k_claims_synth.json` |
| K-Claims-Synth self-application gate | Done | `reports/k_claims_synth/audit.md` verdict `PASS` |
| K-Claims learnability and holdout gate | Done | `k_claims_acceptance.json`, `scripts/check_benchmark_acceptance.py`, `reports/k_claims_synth/benchmark_acceptance.md` |
| K-Claims pre-observation history warmup | Done | `k_claims_synth.py` |
| T2 promoted into verdict table | Done | `fdvh.py`, all regenerated reports |
| AP-lift normalization for cross-prevalence split ratios | Done | `T4.2`, `T7` in all regenerated reports |
| Reference model parameters externalized | Done | `reference_model.yaml`, report `Reference Model` section |
| Frozen LightGBM sensitivity analysis | Done | `scripts/lightgbm_sensitivity.py`, `lightgbm_sensitivity.json`, all report directories |
| Exact official model source citations and hashes | Done | `AIHUB_MODEL_SOURCE_EVIDENCE.md`, `MODEL_PACKAGE_AUDIT.md` |
| Deterministic default entity selection | Done | `fdvh.py`, `tests/test_fdvh.py` |
| EFT-led public case study | Done | `CASE_STUDY.md` |
| Dependency-free CI checks | Done | `.github/workflows/tests.yml` |
| K-Claims provider-rate quasi-leak removed | Done | `k_claims_synth.py`, `K_CLAIMS_SYNTH_DESIGN.md` |
| K-Claims provider holdout and label-noise direction fixed | Done | `configs/k_claims_synth.json`, `reports/k_claims_synth/audit.md` |
| Minimal implementation plan and folder structure | Done | `PROJECT_PLAN.md`, `README.md` |
| Explanation of why this beats training another model on flawed data | Done | `RESULT_SUMMARY.md`, `MODEL_PACKAGE_AUDIT.md` |

## Not Counted As Done

IEEE-CIS and PaySim are not counted as executed anchors because Kaggle API
returned `403` for those downloads in this environment. The completed external
anchors are ULB Credit Card Fraud and BAF Base; both currently produce `WARN`
verdicts under the recall-weighted T2 shortcut criterion.

The default audit remains dependency-free; LightGBM is intentionally isolated
behind `requirements-sensitivity.txt`.
