# Implementation Status

This file maps the Fable design requirements to current repository evidence.

| requirement | status | evidence |
|---|---:|---|
| Problem statement explaining why AI Hub FDS is not reliable | Done | `RESULT_SUMMARY.md`, `MODEL_PACKAGE_AUDIT.md` |
| Versioned thresholds rather than informal judgments | Done | `thresholds.yaml` |
| T0 evaluation-integrity audit | Done | `fdvh.py`, AI Hub reports |
| T1 amount-only baseline | Done | `fdvh.py`, all reports |
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
| Minimal implementation plan and folder structure | Done | `PROJECT_PLAN.md`, `README.md` |
| Explanation of why this beats training another model on flawed data | Done | `RESULT_SUMMARY.md`, `MODEL_PACKAGE_AUDIT.md` |

## Not Counted As Done

IEEE-CIS and PaySim are not counted as executed anchors because Kaggle API
returned `403` for those downloads in this environment. The completed external
anchors are ULB Credit Card Fraud and BAF Base.
