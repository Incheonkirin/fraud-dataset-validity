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
    "claim_lag_days",
    "product_type",
    "diagnosis_code",
    "treatment_code",
    "hospital_days",
    "claim_amount",
    "customer_age",
    "policy_age_days",
    "prior_claim_count_30d",
    "prior_claim_count_365d",
    "provider_prior_claim_count_365d",
    "provider_prior_high_amount_share_365d",
    "provider_prior_same_pair_count_365d",
    "customer_prior_same_provider_count_365d",
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
    provider_ids = [f"provider_{idx:05d}" for idx in range(n_providers)]
    customer_ids = [f"customer_{idx:06d}" for idx in range(n_customers)]
    provider_risk = {
        provider_id: rng.betavariate(2.0, 8.0)
        for provider_id in provider_ids
    }
    ring_providers = set(rng.sample(provider_ids, max(6, n_providers // 28)))
    ring_pairs = {
        provider_id: (rng.choice(DIAGNOSIS_CODES), rng.choice(TREATMENT_CODES))
        for provider_id in ring_providers
    }
    customer_base = {
        customer_id: {
            "age": clamp(int(rng.gauss(46, 15)), 18, 88),
            "region": rng.choice(REGIONS),
            "claim_tendency": rng.betavariate(2.0, 8.0),
        }
        for customer_id in customer_ids
    }

    start = date(2024, 1, 1)
    end = date(2025, 12, 31)
    span = (end - start).days
    rows: list[dict[str, object]] = []
    customer_recent: dict[str, list[tuple[date, str, float]]] = {
        customer: [] for customer in customer_base
    }
    provider_recent: dict[str, list[tuple[date, float, int, str, str]]] = {
        provider_id: [] for provider_id in provider_ids
    }

    # Seed one year of unlabeled history so rolling features do not begin at an
    # artificial zero on the first benchmark date.
    for provider_id in provider_ids:
        history_count = clamp(int(rng.gauss(70, 10)), 35, 105)
        for _ in range(history_count):
            history_date = start - timedelta(days=rng.randint(1, 365))
            diagnosis_code = rng.choice(DIAGNOSIS_CODES)
            treatment_code = rng.choice(TREATMENT_CODES)
            if provider_id in ring_pairs and rng.random() < 0.20:
                diagnosis_code, treatment_code = ring_pairs[provider_id]
            amount = max(1200, round(rng.lognormvariate(10.05, 0.95), 2))
            hospital_days = clamp(int(rng.expovariate(1 / 1.5)), 0, 30)
            provider_recent[provider_id].append(
                (
                    history_date,
                    amount,
                    hospital_days,
                    diagnosis_code,
                    treatment_code,
                )
            )

    for idx in range(n_rows):
        customer_id = rng.choice(customer_ids)
        customer = customer_base[customer_id]
        day_offset = int((span * idx) / max(1, n_rows - 1))
        day_offset = min(span, day_offset + rng.randrange(0, 3))
        claim_date = start + timedelta(days=day_offset)
        is_late_period = claim_date >= date(2025, 7, 1)
        if is_late_period and rng.random() < 0.01:
            provider_id = rng.choice(list(ring_providers))
        else:
            provider_id = rng.choice(provider_ids)
        provider_score = provider_risk[provider_id]
        lag = clamp(int(rng.expovariate(1 / 8)), 0, 60)
        accident_date = claim_date - timedelta(days=lag)
        product_type = rng.choices(PRODUCTS, weights=[0.58, 0.24, 0.10, 0.08])[0]
        channel = rng.choice(CHANNELS)
        diagnosis_code = rng.choice(DIAGNOSIS_CODES)
        treatment_code = rng.choice(TREATMENT_CODES)
        is_ring_pattern = False
        ring_probability = 0.21 if is_late_period else 0.20
        if provider_id in ring_pairs and rng.random() < ring_probability:
            diagnosis_code, treatment_code = ring_pairs[provider_id]
            is_ring_pattern = True
        policy_age_days = clamp(int(rng.expovariate(1 / 620)), 1, 3650)
        prior_365 = min(18, int(rng.expovariate(1 / 1.8)))
        recent_claims = [
            item
            for item in customer_recent[customer_id]
            if (claim_date - item[0]).days <= 365
        ]
        recent_dates = [item[0] for item in recent_claims]
        prior_365 = min(18, max(prior_365, len(recent_dates)))
        prior_30 = sum(1 for d in recent_dates if (claim_date - d).days <= 30)
        customer_prior_same_provider_count_365d = sum(
            1 for _, prior_provider, _ in recent_claims if prior_provider == provider_id
        )
        provider_history = [
            item for item in provider_recent[provider_id] if (claim_date - item[0]).days <= 365
        ]
        provider_prior_claim_count_365d = len(provider_history)
        provider_prior_high_amount_share_365d = (
            sum(1 for _, amount, _, _, _ in provider_history if amount >= 75_000)
            / len(provider_history)
            if provider_history
            else 0.0
        )
        provider_prior_same_pair_count_365d = sum(
            1
            for _, _, _, prior_diagnosis, prior_treatment in provider_history
            if prior_diagnosis == diagnosis_code and prior_treatment == treatment_code
        )

        hospital_lambda = 0.8 + 0.12 * prior_365 + (0.5 if product_type == "medical" else 0.0)
        hospital_days = clamp(int(rng.expovariate(1 / hospital_lambda)), 0, 30)
        base_amount = rng.lognormvariate(10.05, 0.95)
        if product_type == "auto":
            base_amount *= rng.uniform(1.05, 1.75)
        if hospital_days >= 8:
            base_amount *= rng.uniform(1.05, 1.55)
        claim_amount = max(1200, round(base_amount + rng.uniform(-350, 350), 2))

        false_hospitalization = (
            product_type == "medical"
            and hospital_days >= 4
            and provider_prior_claim_count_365d >= 35
        )
        accident_detail_manipulation = (
            product_type in {"auto", "travel"}
            and lag >= 12
            and policy_age_days < 540
        )
        provider_collusion = (
            provider_prior_same_pair_count_365d >= 1
            and provider_prior_high_amount_share_365d >= 0.10
            and provider_prior_claim_count_365d >= 20
        )
        duplicate_or_staged_claim = (
            prior_30 >= 2
            and prior_365 >= 5
            and (
                channel in {"mobile", "web"}
                or customer_prior_same_provider_count_365d >= 1
            )
        )
        disclosure_duty_violation = (
            policy_age_days < 365
            and customer["age"] >= 58
            and prior_365 >= 2
        )
        mechanism_scores = {
            "false_hospitalization": 1.80 * false_hospitalization,
            "accident_detail_manipulation": 2.00 * accident_detail_manipulation,
            "provider_collusion": 2.20 * provider_collusion,
            "duplicate_or_staged_claim": 1.80 * duplicate_or_staged_claim,
            "disclosure_duty_violation": 1.70 * disclosure_duty_violation,
        }
        fraud_type = max(mechanism_scores, key=mechanism_scores.get)
        active_mechanisms = sum(score > 0 for score in mechanism_scores.values())
        interaction_risk = sum(mechanism_scores.values())
        risk = (
            -5.20
            + interaction_risk
            + 0.70 * (active_mechanisms >= 2)
            + 0.18 * (policy_age_days < 365)
            + 0.16 * (prior_365 >= 5)
            + 0.16 * (lag >= 18)
            + 0.16 * (hospital_days >= 6)
            + 0.28 * provider_score
            + 0.14 * (provider_prior_high_amount_share_365d >= 0.12)
            + 0.14 * customer["claim_tendency"]
            + 0.15
            * (
                is_late_period
                and channel == "mobile"
                and product_type in {"auto", "travel"}
                and lag >= 12
            )
            + rng.gauss(0, 0.24)
        )
        oracle = int(rng.random() < sigmoid(risk))

        if oracle and active_mechanisms == 0:
            fraud_type = "other"
        elif not oracle:
            fraud_type = "none"

        false_negative = oracle and rng.random() < 0.40
        false_positive = not oracle and rng.random() < 0.002
        observed = int((oracle and not false_negative) or false_positive)

        customer_recent[customer_id].append((claim_date, provider_id, claim_amount))
        provider_recent[provider_id].append(
            (
                claim_date,
                claim_amount,
                hospital_days,
                diagnosis_code,
                treatment_code,
            )
        )
        rows.append(
            {
                "claim_id": f"claim_{idx:08d}",
                "policy_id": f"policy_{rng.randrange(n_customers * 2):07d}",
                "customer_id": customer_id,
                "provider_id": provider_id,
                "claim_date": claim_date.isoformat(),
                "accident_date": accident_date.isoformat(),
                "claim_lag_days": lag,
                "product_type": product_type,
                "diagnosis_code": diagnosis_code,
                "treatment_code": treatment_code,
                "hospital_days": hospital_days,
                "claim_amount": claim_amount,
                "customer_age": customer["age"],
                "policy_age_days": policy_age_days,
                "prior_claim_count_30d": prior_30,
                "prior_claim_count_365d": prior_365,
                "provider_prior_claim_count_365d": provider_prior_claim_count_365d,
                "provider_prior_high_amount_share_365d": round(
                    provider_prior_high_amount_share_365d, 5
                ),
                "provider_prior_same_pair_count_365d": provider_prior_same_pair_count_365d,
                "customer_prior_same_provider_count_365d": customer_prior_same_provider_count_365d,
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
        entity_num = int(str(row["provider_id"]).rsplit("_", 1)[1])
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
    parser = argparse.ArgumentParser(description="Generate K-Claims-Synth v0.3")
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
                "K-Claims-Synth v0.3",
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
