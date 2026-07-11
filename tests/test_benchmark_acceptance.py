import unittest

from scripts.check_benchmark_acceptance import evaluate


def metric(roc_auc: float, average_precision: float, prevalence: float, top1_lift: float):
    return {
        "roc_auc": roc_auc,
        "average_precision": average_precision,
        "prevalence": prevalence,
        "topk": {"top_1.0%": {"lift": top1_lift}},
    }


class BenchmarkAcceptanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.thresholds = {
            "required_audit_verdict": "PASS",
            "validation": {
                "roc_auc_min": 0.70,
                "roc_auc_max": 0.90,
                "average_precision_lift_min": 4.0,
                "no_id_to_amount_ap_ratio_min": 2.0,
                "top_1pct_lift_min": 4.0,
            },
            "temporal": {
                "roc_auc_min": 0.65,
                "average_precision_lift_min": 3.0,
                "ap_lift_ratio_to_validation_min": 0.50,
            },
            "entity_holdout": {
                "roc_auc_min": 0.65,
                "average_precision_lift_min": 3.0,
                "ap_lift_ratio_to_validation_min": 0.50,
            },
        }
        self.sensitivity = {
            "sample": {"primary_eval_split": "valid"},
            "split_metrics": {
                "valid": {
                    "lightgbm_no_id": metric(0.75, 0.15, 0.03, 8.0),
                    "lightgbm_amount_only": metric(0.52, 0.04, 0.03, 1.2),
                },
                "test_temporal": {
                    "lightgbm_no_id": metric(0.72, 0.12, 0.03, 6.0),
                },
                "test_entity_holdout": {
                    "lightgbm_no_id": metric(0.70, 0.10, 0.03, 5.0),
                },
            },
        }

    def test_passes_when_validity_and_learnability_both_hold(self) -> None:
        result = evaluate(
            {"name": "candidate", "verdict": "PASS"},
            self.sensitivity,
            self.thresholds,
        )
        self.assertEqual(result["verdict"], "PASS")

    def test_fails_when_model_is_not_learnable(self) -> None:
        self.sensitivity["split_metrics"]["valid"]["lightgbm_no_id"] = metric(
            0.58, 0.04, 0.03, 1.5
        )
        result = evaluate(
            {"name": "candidate", "verdict": "PASS"},
            self.sensitivity,
            self.thresholds,
        )
        self.assertEqual(result["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
