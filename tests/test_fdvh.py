import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import fdvh


class FraudDatasetValidityHarnessTest(unittest.TestCase):
    def write_csv(self, path: Path, rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_amount_rules_find_zero_positive_low_region(self) -> None:
        totals = {1000.0: 90, 2000.0: 5, 100000.0: 5}
        positives = {100000.0: 5}
        rules = fdvh.best_amount_rules(
            Counter(totals),
            Counter(positives),
        )
        region = rules["zero_positive_low_region"]
        self.assertEqual(region["threshold_lte"], 2000.0)
        self.assertEqual(region["rows"], 95)
        self.assertAlmostEqual(region["share"], 0.95)

    def test_small_dataset_triggers_t5_and_t9(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            train = tmpdir / "train.csv"
            valid = tmpdir / "valid.csv"
            rows = []
            for index in range(95):
                rows.append(
                    {
                        "transaction_id": index,
                        "account_id": f"a{index % 10}",
                        "event_date": "20240101",
                        "amount": 1000 if index < 90 else 2000,
                        "code": "normal",
                        "label": 0,
                    }
                )
            for index in range(95, 100):
                rows.append(
                    {
                        "transaction_id": index,
                        "account_id": f"a{index}",
                        "event_date": "20240102",
                        "amount": 100000,
                        "code": "rare",
                        "label": 1,
                    }
                )
            self.write_csv(train, rows[:70])
            self.write_csv(valid, rows[70:])

            config = {
                "name": "toy",
                "title": "Toy",
                "label_col": "label",
                "positive_values": ["1"],
                "leak_cols": [],
                "id_cols": ["transaction_id", "account_id"],
                "date_cols": ["event_date"],
                "amount_cols": ["amount"],
                "numeric_cols": ["amount"],
                "splits": [
                    {"name": "train", "paths": [str(train)]},
                    {"name": "valid", "paths": [str(valid)]},
                ],
            }
            result = fdvh.audit(config, fdvh.load_thresholds(Path("thresholds.yaml")))
            statuses = {(test["id"], test["status"]) for test in result["tests"]}
            self.assertIn(("T5", "FAIL"), statuses)
            self.assertIn(("T9.1", "FAIL"), statuses)

    def test_t2_recall_weighted_shortcut_is_verdict_row(self) -> None:
        rules = [
            {
                "column": "amount_bucket",
                "value": "high",
                "is_id": False,
                "count": 200,
                "positive_rate": 0.25,
                "recall": 0.15,
                "lift": 6.0,
            }
        ]
        tests = fdvh.evaluate_t2(rules, fdvh.load_thresholds(Path("thresholds.yaml")), 100)
        self.assertEqual(tests[0]["id"], "T2")
        self.assertEqual(tests[0]["status"], "FAIL")
        self.assertIn("Recall-weighted shortcut", tests[0]["details"])

    def test_amount_threshold_is_selected_on_train_and_frozen_on_eval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            train = tmpdir / "train.csv"
            valid = tmpdir / "valid.csv"
            self.write_csv(
                train,
                [
                    {"amount": 10, "label": 0},
                    {"amount": 20, "label": 0},
                    {"amount": 100, "label": 1},
                    {"amount": 110, "label": 1},
                ],
            )
            self.write_csv(
                valid,
                [
                    {"amount": 10, "label": 1},
                    {"amount": 20, "label": 1},
                    {"amount": 100, "label": 0},
                    {"amount": 110, "label": 0},
                ],
            )
            config = {
                "label_col": "label",
                "positive_values": ["1"],
            }
            result = fdvh.run_amount_threshold_baseline(
                config, [train], [valid], ["amount"]
            )
            self.assertEqual(result["direction"], "high")
            self.assertEqual(result["threshold"], 100.0)
            self.assertEqual(result["train_metrics"]["f1"], 1.0)
            self.assertEqual(result["eval_metrics"]["f1"], 0.0)

    def test_systematic_sampling_selects_exact_target(self) -> None:
        from scripts.lightgbm_sensitivity import should_select

        selected = [index for index in range(101) if should_select(index, 101, 17)]
        self.assertEqual(len(selected), 17)
        self.assertEqual(selected, sorted(selected))

    def test_entity_holdout_requires_explicit_repeated_entity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            train = tmpdir / "train.csv"
            valid = tmpdir / "valid.csv"
            rows = [
                {
                    "first_id": f"first-{index % 20}",
                    "second_id": f"second-{index % 10}",
                    "amount": index + 1,
                    "label": index % 11 == 0,
                }
                for index in range(200)
            ]
            self.write_csv(train, rows[:100])
            self.write_csv(valid, rows[100:])
            config = {
                "name": "ordered-ids",
                "title": "Ordered IDs",
                "label_col": "label",
                "positive_values": ["1", "True"],
                "leak_cols": [],
                "id_cols": ["first_id", "second_id"],
                "date_cols": [],
                "amount_cols": ["amount"],
                "numeric_cols": ["amount"],
                "splits": [
                    {"name": "train", "paths": [str(train)]},
                    {"name": "valid", "paths": [str(valid)]},
                ],
            }
            result = fdvh.audit(config, fdvh.load_thresholds(Path("thresholds.yaml")))
            self.assertNotIn("entity_holdout_no_id_nb", result["baselines"])

            config["entity_holdout_col"] = "first_id"
            result = fdvh.audit(config, fdvh.load_thresholds(Path("thresholds.yaml")))
            entity = result["baselines"]["entity_holdout_no_id_nb"]
            self.assertEqual(entity["entity_col"], "first_id")
            self.assertEqual(entity["entity_count"], 20)
            self.assertEqual(entity["repeated_entity_count"], 20)

    def test_entity_holdout_rejects_unique_row_identifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.csv"
            rows = [
                {"row_id": f"row-{index}", "amount": index, "label": index % 7 == 0}
                for index in range(100)
            ]
            self.write_csv(path, rows)
            config = {"label_col": "label", "positive_values": ["1", "True"]}
            result = fdvh.run_entity_holdout_baseline(
                config,
                [path],
                "row_id",
                ["amount"],
                fdvh.DEFAULT_REFERENCE_MODEL,
            )
            self.assertIsNone(result)

    def test_duplicate_features_exclude_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.csv"
            self.write_csv(
                path,
                [
                    {"row_id": "a", "feature": "same", "label": 0},
                    {"row_id": "b", "feature": "same", "label": 1},
                ],
            )
            config = {
                "name": "duplicates",
                "title": "Duplicates",
                "label_col": "label",
                "positive_values": ["1"],
                "leak_cols": [],
                "id_cols": ["row_id"],
                "date_cols": [],
                "amount_cols": [],
                "numeric_cols": [],
                "splits": [{"name": "all", "paths": [str(path)]}],
            }
            result = fdvh.audit(config, fdvh.load_thresholds(Path("thresholds.yaml")))
            profile = result["row_profile"]
            self.assertEqual(profile["duplicate_rows_excluding_label_and_ids"], 1)
            self.assertEqual(profile["label_conflict_rows_excluding_label_and_ids"], 2)

    def test_average_precision_is_invariant_with_tied_scores(self) -> None:
        first = fdvh.average_precision([1, 0, 1, 0], [0.9, 0.9, 0.1, 0.1])
        permuted = fdvh.average_precision([0, 1, 0, 1], [0.9, 0.9, 0.1, 0.1])
        self.assertAlmostEqual(first, permuted)
        self.assertAlmostEqual(first, 0.5)

    def test_t8_flags_korean_entity_aggregate_name(self) -> None:
        tests = fdvh.evaluate_t8(
            ["가맹점누적매출금액_구간화"],
            ["가맹점누적매출금액_구간화"],
            set(),
            fdvh.load_thresholds(Path("thresholds.yaml")),
        )
        statuses = {test["id"]: test["status"] for test in tests}
        self.assertEqual(statuses["T8.3"], "WARN")

    def test_weak_reference_makes_ratio_gate_screening_only(self) -> None:
        baselines = {
            "provided_split_no_id_nb": {
                "average_precision": 0.5,
                "best_f1": 0.8,
            },
            "provided_split_amount_only_nb": {
                "roc_auc": 0.7,
                "average_precision": 0.45,
            },
            "provided_split_amount_threshold": {
                "column": "amount",
                "rule": "amount >= 100",
                "eval_metrics": {"f1": 0.75},
            },
        }
        tests = fdvh.evaluate_t1(
            baselines,
            fdvh.load_thresholds(Path("thresholds.yaml")),
            {"ratio_gates_are_screening_only": True},
        )
        statuses = {test["id"]: test["status"] for test in tests}
        self.assertEqual(statuses["T1.2"], "WARN")
        self.assertEqual(statuses["T1.3"], "WARN")


if __name__ == "__main__":
    unittest.main()
