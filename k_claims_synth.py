from __future__ import annotations

import argparse
import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path


FIELDNAMES = [
    "claim_id",
    "policy_id",
    "customer_id",
    "provider_id",
    "claim_date",
    "accident_date",
    "product_type",
    "diagnosis_code",
    "treatment_code",
    "hospital_days",
    "claim_amount",
    "customer_age",
    "policy_age_days",
    "prior_claim_count_30d",
    "prior_claim_count_365d",
    "provider_claim_rate",
    "region",
    "channel",
    "observed_fraud_label",
    "oracle_fraud_label",
    "fraud_type",
]


PRODUCTS = ["medical", "auto", "life", "travel"]
REGIONS = ["metro", "central", "south", "east", "west"]
CHANNELS = ["agent", "mobile", "web", "branch"]
DIAGNOSIS_CODES = [f"D{i:03d}" for i in range(1, 61)]
TREATMENT_CODES = [f"T{i:03d}" for i in range(1, 81)]


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def month_start(index: int) -> date:
    year = 2024 + index // 12
    month = index % 12 + 1
    return date(year, month, 1)


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def build_rows(n_rows: int, seed: int) -> list[dict[str, object]]:
    rng = random.Random(seed)
    n_customers = max(1000, n_rows // 18)
    n_providers = max(300, n_rows // 140)
    provider_risk = {
        f"provider_{idx:05d}": rng.betavariate(2.0, 8.0)
        for idx in range(n_providers)
    }
    customer_base = {
        f"customer_{idx:06d}": {
            "age": clamp(int(rng.gauss(46, 15)), 18, 88),
            "region": rng.choice(REGIONS),
            "claim_tendency": rng.betavariate(2.0, 8.0),
        }
        for idx in range(n_customers)
    }

    rows: list[dict[str, object]] = []
    customer_recent: dict[str, list[date]] = {customer: [] for customer in customer_base}
    start = date(2024, 1, 1)
    end = date(2025, 12, 31)
    span = (end - start).days

    for idx in range(n_rows):
        customer_id = rng.choice(list(customer_base))
        customer = customer_base[customer_id]
        provider_id = rng.choice(list(provider_risk))
        provider_score = provider_risk[provider_id]
        claim_date = start + timedelta(days=rng.randrange(span + 1))
        lag = clamp(int(rng.expovariate(1 / 8)), 0, 60)
        accident_date = claim_date - timedelta(days=lag)
        product_type = rng.choices(PRODUCTS, weights=[0.58, 0.24, 0.10, 0.08])[0]
        channel = rng.choice(CHANNELS)
        diagnosis_code = rng.choice(DIAGNOSIS_CODES)
        treatment_code = rng.choice(TREATMENT_CODES)
        policy_age_days = clamp(int(rng.expovariate(1 / 620)), 1, 3650)
        prior_365 = min(18, rng.poisson(1.2) if hasattr(rng, "poisson") else int(rng.expovariate(1 / 1.8)))
        recent_dates = [d for d in customer_recent[customer_id] if (claim_date - d).days <= 365]
        prior_365 = min(18, max(prior_365, len(recent_dates)))
        prior_30 = sum(1 for d in recent_dates if (claim_date - d).days <= 30)

        hospital_lambda = 0.8 + 0.12 * prior_365 + (0.5 if product_type == "medical" else 0.0)
        hospital_days = clamp(int(rng.expovariate(1 / hospital_lambda)), 0, 30)
        base_amount = rng.lognormvariate(10.05, 0.95)
        if product_type == "auto":
            base_amount *= rng.uniform(1.05, 1.75)
        if hospital_days >= 8:
            base_amount *= rng.uniform(1.05, 1.55)
        claim_amount = max(1200, round(base_amount + rng.uniform(-350, 350), 2))

        mechanism_scores = {
            "false_hospitalization": 0.9 * (hospital_days >= 9)
            + 0.4 * (product_type == "medical")
            + 0.5 * provider_score,
            "accident_detail_manipulation": 0.8 * (lag >= 24)
            + 0.25 * (product_type in {"auto", "travel"})
            + 0.25 * (policy_age_days < 180),
            "provider_collusion": 1.0 * (provider_score > 0.55)
            + 0.4 * (prior_30 >= 2)
            + 0.2 * (channel in {"agent", "branch"}),
            "duplicate_or_staged_claim": 0.7 * (prior_30 >= 2)
            + 0.5 * (prior_365 >= 5)
            + 0.2 * customer["claim_tendency"],
            "disclosure_duty_violation": 0.8 * (policy_age_days < 120)
            + 0.35 * (customer["age"] >= 65)
            + 0.2 * (prior_365 >= 3),
        }
        fraud_type = max(mechanism_scores, key=mechanism_scores.get)
        risk = (
            -4.85
            + 0.55 * (policy_age_days < 120)
            + 0.55 * (prior_30 >= 2)
            + 0.32 * (prior_365 >= 5)
            + 0.48 * (lag >= 24)
            + 0.50 * (hospital_days >= 9)
            + 0.90 * provider_score
            + 0.20 * (product_type == "medical")
            + 0.18 * customer["claim_tendency"]
            + rng.gauss(0, 0.42)
        )
        oracle = int(rng.random() < sigmoid(risk))

        if oracle:
            if fraud_type == "false_hospitalization":
                hospital_days = max(hospital_days, rng.randint(7, 18))
            elif fraud_type == "accident_detail_manipulation":
                lag = max(lag, rng.randint(18, 50))
                accident_date = claim_date - timedelta(days=lag)
            elif fraud_type == "duplicate_or_staged_claim":
                prior_30 = max(prior_30, rng.randint(1, 4))
            claim_amount = round(claim_amount * rng.uniform(0.92, 1.35), 2)
        else:
            fraud_type = "none"

        false_negative = oracle and rng.random() < 0.12
        false_positive = not oracle and rng.random() < 0.018
        observed = int((oracle and not false_negative) or false_positive)

        customer_recent[customer_id].append(claim_date)
        rows.append(
            {
                "claim_id": f"claim_{idx:08d}",
                "policy_id": f"policy_{rng.randrange(n_customers * 2):07d}",
                "customer_id": customer_id,
                "provider_id": provider_id,
                "claim_date": claim_date.isoformat(),
                "accident_date": accident_date.isoformat(),
                "product_type": product_type,
                "diagnosis_code": diagnosis_code,
                "treatment_code": treatment_code,
                "hospital_days": hospital_days,
                "claim_amount": claim_amount,
                "customer_age": customer["age"],
                "policy_age_days": policy_age_days,
                "prior_claim_count_30d": prior_30,
                "prior_claim_count_365d": prior_365,
                "provider_claim_rate": round(0.02 + provider_score * 0.18 + rng.uniform(-0.01, 0.01), 5),
                "region": customer["region"],
                "channel": channel,
                "observed_fraud_label": observed,
                "oracle_fraud_label": oracle,
                "fraud_type": fraud_type,
            }
        )
    return rows


def split_rows(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    train: list[dict[str, object]] = []
    valid: list[dict[str, object]] = []
    temporal: list[dict[str, object]] = []
    entity: list[dict[str, object]] = []
    for row in rows:
        claim_date = date.fromisoformat(str(row["claim_date"]))
        entity_num = int(str(row["customer_id"]).rsplit("_", 1)[1])
        if entity_num % 10 == 0:
            entity.append(row)
        elif claim_date >= date(2025, 7, 1):
            temporal.append(row)
        elif entity_num % 10 in {1, 2}:
            valid.append(row)
        else:
            train.append(row)
    return {
        "train": train,
        "valid": valid,
        "test_temporal": temporal,
        "test_entity_holdout": entity,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate K-Claims-Synth v0.1")
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=20260709)
    parser.add_argument("--out", type=Path, default=Path("data_generated/k_claims_synth"))
    args = parser.parse_args()

    rows = build_rows(args.rows, args.seed)
    splits = split_rows(rows)
    for name, split in splits.items():
        write_rows(args.out / f"{name}.csv", split)

    metadata = args.out / "README.txt"
    metadata.write_text(
        "\n".join(
            [
                "K-Claims-Synth v0.1",
                f"rows={len(rows)}",
                f"seed={args.seed}",
                "labels=observed_fraud_label, oracle_fraud_label",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for name, split in splits.items():
        positives = sum(int(row["oracle_fraud_label"]) for row in split)
        print(f"{name}: rows={len(split)} oracle_positives={positives}")


if __name__ == "__main__":
    main()
