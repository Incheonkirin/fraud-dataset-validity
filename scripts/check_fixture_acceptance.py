from __future__ import annotations

import argparse
import json
from pathlib import Path


def ap_lift(metric: dict[str, object]) -> float:
    return float(metric["average_precision"]) / float(metric["prevalence"])


def add_check(
    checks: list[dict[str, object]],
    name: str,
    value: object,
    passed: bool,
    threshold: str,
) -> None:
    checks.append(
        {
            "name": name,
            "value": value,
            "status": "PASS" if passed else "FAIL",
            "threshold": threshold,
        }
    )


def evaluate(
    audit: dict[str, object],
    sensitivity: dict[str, object],
    thresholds: dict[str, object],
) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    required_verdict = str(thresholds["required_audit_verdict"])
    add_check(
        checks,
        "shortcut validity audit",
        audit["verdict"],
        audit["verdict"] == required_verdict,
        required_verdict,
    )

    split_metrics = sensitivity["split_metrics"]
    primary_name = sensitivity["sample"]["primary_eval_split"]
    validation = split_metrics[primary_name]
    valid_model = validation["lightgbm_no_id"]
    valid_amount = validation["lightgbm_amount_only"]
    valid_thresholds = thresholds["validation"]
    valid_roc = float(valid_model["roc_auc"])
    valid_lift = ap_lift(valid_model)
    model_to_amount = float(valid_model["average_precision"]) / float(
        valid_amount["average_precision"]
    )
    top1_lift = float(valid_model["topk"]["top_1.0%"]["lift"])
    add_check(
        checks,
        "validation ROC-AUC floor",
        valid_roc,
        valid_roc >= valid_thresholds["roc_auc_min"],
        f">= {valid_thresholds['roc_auc_min']}",
    )
    add_check(
        checks,
        "validation ROC-AUC ceiling",
        valid_roc,
        valid_roc <= valid_thresholds["roc_auc_max"],
        f"<= {valid_thresholds['roc_auc_max']}",
    )
    add_check(
        checks,
        "validation AP lift",
        valid_lift,
        valid_lift >= valid_thresholds["average_precision_lift_min"],
        f">= {valid_thresholds['average_precision_lift_min']}",
    )
    add_check(
        checks,
        "no-ID AP / amount-only AP",
        model_to_amount,
        model_to_amount >= valid_thresholds["no_id_to_amount_ap_ratio_min"],
        f">= {valid_thresholds['no_id_to_amount_ap_ratio_min']}",
    )
    add_check(
        checks,
        "validation top-1% lift",
        top1_lift,
        top1_lift >= valid_thresholds["top_1pct_lift_min"],
        f">= {valid_thresholds['top_1pct_lift_min']}",
    )

    for split_name, gate_name in (
        ("test_temporal", "temporal"),
        ("test_entity_holdout", "entity_holdout"),
    ):
        split_thresholds = thresholds[gate_name]
        metric = split_metrics.get(split_name, {}).get("lightgbm_no_id")
        if not isinstance(metric, dict):
            add_check(checks, f"{gate_name} split exists", None, False, "required")
            continue
        split_roc = float(metric["roc_auc"])
        split_lift = ap_lift(metric)
        lift_ratio = split_lift / valid_lift
        add_check(
            checks,
            f"{gate_name} ROC-AUC",
            split_roc,
            split_roc >= split_thresholds["roc_auc_min"],
            f">= {split_thresholds['roc_auc_min']}",
        )
        add_check(
            checks,
            f"{gate_name} AP lift",
            split_lift,
            split_lift >= split_thresholds["average_precision_lift_min"],
            f">= {split_thresholds['average_precision_lift_min']}",
        )
        add_check(
            checks,
            f"{gate_name} AP-lift ratio to validation",
            lift_ratio,
            lift_ratio >= split_thresholds["ap_lift_ratio_to_validation_min"],
            f">= {split_thresholds['ap_lift_ratio_to_validation_min']}",
        )

    return {
        "dataset": audit["name"],
        "verdict": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
        "checks": checks,
        "thresholds": thresholds,
    }


def render(result: dict[str, object]) -> str:
    lines = [
        "# K-Claims Test-Fixture Acceptance",
        "",
        f"Verdict: **{result['verdict']}**",
        "",
        "| check | status | value | threshold |",
        "|---|---:|---:|---:|",
    ]
    for check in result["checks"]:
        value = check["value"]
        value_text = f"{value:.4f}" if isinstance(value, float) else str(value)
        lines.append(
            f"| {check['name']} | {check['status']} | {value_text} | {check['threshold']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check K-Claims test-fixture acceptance")
    parser.add_argument("--audit-json", required=True, type=Path)
    parser.add_argument("--sensitivity-json", required=True, type=Path)
    parser.add_argument(
        "--thresholds", type=Path, default=Path("k_claims_fixture_acceptance.json")
    )
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    audit = json.loads(args.audit_json.read_text(encoding="utf-8"))
    sensitivity = json.loads(args.sensitivity_json.read_text(encoding="utf-8"))
    thresholds = json.loads(args.thresholds.read_text(encoding="utf-8"))
    result = evaluate(audit, sensitivity, thresholds)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "fixture_acceptance.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = render(result)
    (args.out / "fixture_acceptance.md").write_text(report, encoding="utf-8")
    print(report)
    raise SystemExit(0 if result["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
