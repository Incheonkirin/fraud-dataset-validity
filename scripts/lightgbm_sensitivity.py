from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import fdvh


def should_select(index: int, total: int, target: int) -> bool:
    if target >= total:
        return True
    return ((index + 1) * target) // total != (index * target) // total


def count_rows(paths: list[Path]) -> int:
    return sum(1 for _ in fdvh.iter_rows(paths))


def sample_columns(
    config: dict[str, object],
    paths: list[Path],
    feature_cols: list[str],
    purpose: str,
    max_rows: int,
) -> tuple[dict[str, list[str]], list[int], int]:
    total = count_rows(paths)
    target = min(total, max_rows)
    columns = {col: [] for col in feature_cols}
    labels: list[int] = []
    for index, row in enumerate(fdvh.iter_rows(paths)):
        if not should_select(index, total, target):
            continue
        for col in feature_cols:
            columns[col].append(fdvh.normalize(row.get(col, "")))
        labels.append(fdvh.positive_label(config, row, purpose))
    return columns, labels, total


def prepare_train_frame(
    train_data: dict[str, list[str]],
    feature_cols: list[str],
    numeric_cols: set[str],
    date_cols: set[str],
):
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit(
            "Sensitivity dependencies are missing. Install requirements-sensitivity.txt."
        ) from exc

    train = pd.DataFrame(train_data, columns=feature_cols)
    category_levels = {}
    for col in feature_cols:
        if col in date_cols:
            train[col] = pd.to_numeric(
                train[col].str.replace(r"\D", "", regex=True), errors="coerce"
            )
        elif col in numeric_cols:
            train[col] = pd.to_numeric(train[col], errors="coerce")
        else:
            train_values = train[col].fillna(fdvh.NA).astype(str)
            categories = pd.Index(train_values.unique())
            category_levels[col] = categories
            train[col] = pd.Categorical(train_values, categories=categories)
    return train, category_levels


def prepare_eval_frame(
    eval_data: dict[str, list[str]],
    feature_cols: list[str],
    numeric_cols: set[str],
    date_cols: set[str],
    category_levels,
):
    import pandas as pd

    evaluation = pd.DataFrame(eval_data, columns=feature_cols)
    for col in feature_cols:
        if col in date_cols:
            evaluation[col] = pd.to_numeric(
                evaluation[col].str.replace(r"\D", "", regex=True), errors="coerce"
            )
        elif col in numeric_cols:
            evaluation[col] = pd.to_numeric(evaluation[col], errors="coerce")
        else:
            evaluation[col] = pd.Categorical(
                evaluation[col].fillna(fdvh.NA).astype(str),
                categories=category_levels[col],
            )
    return evaluation


def fit_model(train, y_train: list[int], params: dict[str, object]):
    try:
        import lightgbm as lgb
    except ImportError as exc:
        raise SystemExit(
            "Sensitivity dependencies are missing. Install requirements-sensitivity.txt."
        ) from exc

    positives = sum(y_train)
    negatives = len(y_train) - positives
    model_params = dict(params)
    model_params["objective"] = "binary"
    if positives:
        model_params["scale_pos_weight"] = negatives / positives
    model = lgb.LGBMClassifier(**model_params)
    model.fit(train, y_train, categorical_feature="auto")
    return model


def score_model(model, evaluation) -> list[float]:
    return model.predict_proba(evaluation)[:, 1].tolist()


def find_test(audit: dict[str, object], test_id: str) -> dict[str, object] | None:
    for test in audit.get("tests", []):
        if test.get("id") == test_id:
            return test
    return None


def amount_rule_f1(audit: dict[str, object]) -> float | None:
    baseline = audit.get("baselines", {}).get("provided_split_amount_threshold")
    if isinstance(baseline, dict):
        metric = baseline.get("eval_metrics")
        if isinstance(metric, dict) and isinstance(metric.get("f1"), (int, float)):
            return float(metric["f1"])
    test = find_test(audit, "T1.3")
    metric = test.get("metric") if test else None
    if isinstance(metric, dict) and isinstance(metric.get("f1"), (int, float)):
        return float(metric["f1"])
    return None


def package_versions() -> dict[str, str]:
    import lightgbm
    import pandas
    import sklearn

    return {
        "lightgbm": lightgbm.__version__,
        "pandas": pandas.__version__,
        "scikit_learn": sklearn.__version__,
    }


def run(
    config_path: Path,
    audit_path: Path,
    settings_path: Path,
) -> dict[str, object]:
    config = fdvh.load_config(config_path)
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    paths_by_split = fdvh.split_paths(config)
    split_names = list(paths_by_split)
    if len(split_names) < 2:
        raise ValueError("A provided train/evaluation split is required.")
    train_paths = paths_by_split[split_names[0]]
    header = fdvh.read_header(train_paths[0])
    excluded = {
        fdvh.label_column(config, "train"),
        fdvh.label_column(config, "eval"),
        *config.get("leak_cols", []),
        *config.get("id_cols", []),
    }
    feature_cols = [col for col in header if col not in excluded]
    amount_cols = [
        col for col in feature_cols if col in set(config.get("amount_cols", []))
    ]
    if not amount_cols:
        raise ValueError("No usable amount column is configured.")

    sampling = settings["sampling"]
    train_data, y_train, train_total = sample_columns(
        config,
        train_paths,
        feature_cols,
        "train",
        int(sampling["max_train_rows"]),
    )
    numeric_cols = set(config.get("numeric_cols", []))
    date_cols = set(config.get("date_cols", []))
    train_frame, category_levels = prepare_train_frame(
        train_data,
        feature_cols,
        numeric_cols,
        date_cols,
    )
    model_params = settings["model"]
    no_id_model = fit_model(train_frame, y_train, model_params)
    amount_model = fit_model(train_frame[amount_cols], y_train, model_params)

    split_metrics = {}
    for split_name in split_names[1:]:
        eval_data, y_eval, eval_total = sample_columns(
            config,
            paths_by_split[split_name],
            feature_cols,
            "eval",
            int(sampling["max_eval_rows"]),
        )
        eval_frame = prepare_eval_frame(
            eval_data,
            feature_cols,
            numeric_cols,
            date_cols,
            category_levels,
        )
        no_id_scores = score_model(no_id_model, eval_frame)
        amount_scores = score_model(amount_model, eval_frame[amount_cols])
        split_metrics[split_name] = {
            "sample": {
                "rows_total": eval_total,
                "rows_used": len(y_eval),
                "positives_used": sum(y_eval),
            },
            "lightgbm_no_id": fdvh.evaluate_scores(y_eval, no_id_scores),
            "lightgbm_amount_only": fdvh.evaluate_scores(y_eval, amount_scores),
        }

    primary_split = split_names[1]
    primary = split_metrics[primary_split]
    no_id = primary["lightgbm_no_id"]
    amount_only = primary["lightgbm_amount_only"]
    ap_ratio = amount_only["average_precision"] / no_id["average_precision"]
    fixed_rule_f1 = amount_rule_f1(audit)
    f1_ratio = (
        fixed_rule_f1 / no_id["best_f1"]
        if fixed_rule_f1 is not None and no_id.get("best_f1")
        else None
    )
    thresholds = audit["thresholds"]["t1_amount_only_baseline"]
    t1_2_fail = ap_ratio >= thresholds["fail_if_average_precision_ratio_gte"]
    t1_3_fail = bool(
        fixed_rule_f1 is not None
        and f1_ratio is not None
        and fixed_rule_f1 >= thresholds["fail_if_best_threshold_f1_gte"]
        and f1_ratio >= thresholds["fail_if_best_threshold_f1_ratio_gte"]
    )
    independent_fail_gates = [
        test["id"]
        for test in audit.get("tests", [])
        if test.get("status") == "FAIL" and test.get("id") not in {"T1.2", "T1.3"}
    ]
    return {
        "dataset": audit["name"],
        "title": audit["title"],
        "run_type": "lightgbm_reference_model_sensitivity",
        "settings": settings,
        "package_versions": package_versions(),
        "features": {
            "no_id_count": len(feature_cols),
            "amount_columns": amount_cols,
            "excluded_id_columns": list(config.get("id_cols", [])),
            "excluded_leak_columns": list(config.get("leak_cols", [])),
        },
        "sample": {
            "train_rows_total": train_total,
            "train_rows_used": len(y_train),
            "train_positives_used": sum(y_train),
            "primary_eval_split": primary_split,
            "eval_rows_total": primary["sample"]["rows_total"],
            "eval_rows_used": primary["sample"]["rows_used"],
            "eval_positives_used": primary["sample"]["positives_used"],
        },
        "split_metrics": split_metrics,
        "metrics": {
            "lightgbm_no_id": no_id,
            "lightgbm_amount_only": amount_only,
            "amount_only_ap_ratio": ap_ratio,
            "fixed_amount_rule_f1": fixed_rule_f1,
            "fixed_amount_rule_to_lightgbm_f1_ratio": f1_ratio,
        },
        "sensitivity_verdict": {
            "t1_2": "FAIL" if t1_2_fail else "PASS",
            "t1_3": "FAIL" if t1_3_fail else "PASS",
            "independent_fail_gates": independent_fail_gates,
            "dataset_fail_survives_ratio_gate_changes": bool(independent_fail_gates),
        },
    }


def metric(value: object) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}" if isinstance(value, float) else str(value)


def render(result: dict[str, object]) -> str:
    sample = result["sample"]
    metrics = result["metrics"]
    verdict = result["sensitivity_verdict"]
    no_id = metrics["lightgbm_no_id"]
    amount = metrics["lightgbm_amount_only"]
    lines = [
            f"# {result['title']} LightGBM Sensitivity",
            "",
            "This analysis replaces the stdlib reference denominator with a frozen LightGBM model.",
            "It is a sensitivity check, not a tuned leaderboard model.",
            "",
            "## Sample",
            "",
            f"- Train: {sample['train_rows_used']:,} / {sample['train_rows_total']:,} rows ({sample['train_positives_used']:,} positives)",
            f"- Evaluation: {sample['eval_rows_used']:,} / {sample['eval_rows_total']:,} rows ({sample['eval_positives_used']:,} positives)",
            f"- Method: `{result['settings']['sampling']['method']}`",
            "",
            "## Results",
            "",
            "| model/check | ROC-AUC | PR-AUC | best F1 | status |",
            "|---|---:|---:|---:|---:|",
            f"| LightGBM no-ID | {metric(no_id['roc_auc'])} | {metric(no_id['average_precision'])} | {metric(no_id['best_f1'])} | reference |",
            f"| LightGBM amount-only | {metric(amount['roc_auc'])} | {metric(amount['average_precision'])} | {metric(amount['best_f1'])} | reference |",
            f"| T1.2 amount/no-ID AP ratio |  | {metric(metrics['amount_only_ap_ratio'])} |  | {verdict['t1_2']} |",
            f"| T1.3 fixed amount rule/no-ID F1 ratio |  |  | {metric(metrics['fixed_amount_rule_to_lightgbm_f1_ratio'])} | {verdict['t1_3']} |",
            "",
            "## Split Robustness",
            "",
            "| split | rows | prevalence | no-ID ROC-AUC | no-ID PR-AUC | AP lift |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    for split_name, split in result["split_metrics"].items():
        split_metric = split["lightgbm_no_id"]
        split_lift = (
            split_metric["average_precision"] / split_metric["prevalence"]
            if split_metric.get("prevalence")
            else None
        )
        lines.append(
            f"| {split_name} | {split['sample']['rows_used']:,} | "
            f"{metric(split_metric['prevalence'])} | {metric(split_metric['roc_auc'])} | "
            f"{metric(split_metric['average_precision'])} | {metric(split_lift)} |"
        )
    lines.extend(
        [
            "",
            "## Robustness",
            "",
            f"- Independent full-audit FAIL gates: {', '.join(verdict['independent_fail_gates']) or 'none'}",
            f"- Dataset FAIL survives T1.2/T1.3 changes: **{str(verdict['dataset_fail_survives_ratio_gate_changes']).upper()}**",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run optional LightGBM sensitivity analysis")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--audit-json", required=True, type=Path)
    parser.add_argument(
        "--settings", type=Path, default=ROOT / "lightgbm_sensitivity.json"
    )
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = run(args.config, args.audit_json, args.settings)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "lightgbm_sensitivity.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = render(result)
    (args.out / "lightgbm_sensitivity.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
