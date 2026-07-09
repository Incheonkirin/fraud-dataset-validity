from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
from pathlib import Path


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def prepare_ulb(raw_path: Path, out_dir: Path) -> None:
    with raw_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = ["transaction_id", "event_date"] + list(reader.fieldnames or [])
        rows = []
        start = date(2013, 9, 1)
        for idx, row in enumerate(reader):
            seconds = int(float(row["Time"]))
            row = {"transaction_id": str(idx), "event_date": (start + timedelta(seconds=seconds)).isoformat(), **row}
            rows.append(row)
    rows.sort(key=lambda item: (float(item["Time"]), int(item["transaction_id"])))
    split = int(len(rows) * 0.70)
    write_rows(out_dir / "train.csv", fieldnames, rows[:split])
    write_rows(out_dir / "valid.csv", fieldnames, rows[split:])


def prepare_baf(raw_path: Path, out_dir: Path) -> None:
    with raw_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = ["application_id", "event_date"] + list(reader.fieldnames or [])
        train = []
        valid = []
        for idx, row in enumerate(reader):
            month = int(float(row["month"]))
            event_date = date(2022 + month // 12, month % 12 + 1, 1).isoformat()
            row = {"application_id": str(idx), "event_date": event_date, **row}
            if month <= 5:
                train.append(row)
            else:
                valid.append(row)
    write_rows(out_dir / "train.csv", fieldnames, train)
    write_rows(out_dir / "valid.csv", fieldnames, valid)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare local Kaggle anchor splits")
    parser.add_argument("--root", type=Path, default=Path("data_external/kaggle"))
    parser.add_argument("--out", type=Path, default=Path("data_generated/anchors"))
    args = parser.parse_args()

    ulb_raw = args.root / "ulb_creditcard" / "creditcard.csv"
    if ulb_raw.exists():
        prepare_ulb(ulb_raw, args.out / "ulb_creditcard")
        print("prepared ulb_creditcard")
    else:
        print(f"missing {ulb_raw}")

    baf_raw = args.root / "baf" / "Base.csv"
    if baf_raw.exists():
        prepare_baf(baf_raw, args.out / "baf_base")
        print("prepared baf_base")
    else:
        print(f"missing {baf_raw}")


if __name__ == "__main__":
    main()
