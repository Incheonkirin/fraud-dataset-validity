# K-Claims Benchmark Acceptance

Verdict: **PASS**

| check | status | value | threshold |
|---|---:|---:|---:|
| shortcut validity audit | PASS | PASS | PASS |
| validation ROC-AUC floor | PASS | 0.7463 | >= 0.7 |
| validation ROC-AUC ceiling | PASS | 0.7463 | <= 0.9 |
| validation AP lift | PASS | 5.6064 | >= 4.0 |
| no-ID AP / amount-only AP | PASS | 5.2483 | >= 2.0 |
| validation top-1% lift | PASS | 13.4669 | >= 4.0 |
| temporal ROC-AUC | PASS | 0.7440 | >= 0.65 |
| temporal AP lift | PASS | 4.3930 | >= 3.0 |
| temporal AP-lift ratio to validation | PASS | 0.7836 | >= 0.5 |
| entity_holdout ROC-AUC | PASS | 0.7509 | >= 0.65 |
| entity_holdout AP lift | PASS | 4.6294 | >= 3.0 |
| entity_holdout AP-lift ratio to validation | PASS | 0.8257 | >= 0.5 |
