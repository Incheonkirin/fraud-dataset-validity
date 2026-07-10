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


if __name__ == "__main__":
    unittest.main()
