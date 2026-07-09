from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import zipfile
from copy import deepcopy
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


NA = "<NA>"
INTEGER_PATTERN = re.compile(r"-?\d+(\.0+)?")
DEFAULT_THRESHOLDS = {
    "version": "0.1",
    "min_rule_support": 100,
    "t0_evaluation_integrity": {
        "fail_if_concat_then_random_resplit": True,
        "fail_if_type_classification_filters_to_positive_rows": False,
        "warn_if_no_temporal_holdout_with_dates": True,
        "warn_if_no_entity_holdout_with_ids": True,
    },
    "t1_amount_only_baseline": {
        "fail_if_roc_auc_gte": 0.95,
        "fail_if_average_precision_ratio_gte": 0.80,
        "fail_if_best_threshold_f1_gte": 0.70,
    },
    "t2_single_feature_shortcut": {
        "fail_if_positive_rate_gte": 0.50,
        "fail_if_lift_gte": 20.0,
        "warn_if_recall_gte": 0.20,
    },
    "t5_zero_fraud_region": {
        "fail_if_row_share_gte": 0.90,
        "warn_if_row_share_gte": 0.50,
    },
    "t9_cardinality_sanity": {
        "fail_if_amount_distinct_lte": 100,
        "fail_if_amount_top10_share_gte": 0.90,
        "warn_if_amount_top10_share_gte": 0.70,
        "warn_if_round_thousand_share_gte": 0.95,
    },
    "duplicates": {
        "warn_if_duplicate_feature_rows_gte": 0.01,
    },
    "split_drift": {
        "warn_if_max_non_id_js_lte": 0.01,
    },
}


def normalize(value: object) -> str:
    if value is None:
        return NA
    text = str(value).strip()
    if not text:
        return NA
    if INTEGER_PATTERN.fullmatch(text):
        return str(int(float(text)))
    return text


def parse_scalar(value: str) -> object:
    value = value.strip()
    if not value:
        return ""
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        if re.fullmatch(r"-?\d+", value):
            return int(value)
        if re.fullmatch(r"-?(\d+\.\d*|\d*\.\d+)(e-?\d+)?", value, re.I):
            return float(value)
    except ValueError:
        pass
    return value


def load_simple_yaml(path: Path) -> dict[str, object]:
    """Read the small thresholds YAML format without adding a dependency."""
    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2:
            raise ValueError(f"Invalid YAML indentation in {path}: {raw_line!r}")
        key, sep, value = line.lstrip().partition(":")
        if not sep:
            raise ValueError(f"Invalid YAML line in {path}: {raw_line!r}")
        while indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value.strip():
            parent[key] = parse_scalar(value)
        else:
            child: dict[str, object] = {}
            parent[key] = child
            stack.append((indent, child))
    return root


def deep_merge(base: dict[str, object], override: dict[str, object]) -> dict[str, object]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)  # type: ignore[arg-type]
        else:
            result[key] = value
    return result


def load_thresholds(path: Path | None) -> dict[str, object]:
    if path is None:
        default_path = Path("thresholds.yaml")
        path = default_path if default_path.exists() else None
    if path is None:
        return deepcopy(DEFAULT_THRESHOLDS)
    return deep_merge(DEFAULT_THRESHOLDS, load_simple_yaml(path))


def parse_float(value: object) -> float | None:
    text = normalize(value)
    if text == NA:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_year_month_day(value: object) -> tuple[str, str, str]:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if len(digits) >= 8:
        return digits[:4], digits[:6], digits[:8]
    if len(digits) >= 6:
        return digits[:4], digits[:6], ""
    if len(digits) >= 4:
        return digits[:4], "", ""
    return "", "", ""


def csv_infos(zip_path: Path) -> list[zipfile.ZipInfo]:
    with zipfile.ZipFile(zip_path) as zf:
        return [
            info
            for info in zf.infolist()
            if not info.is_dir() and info.filename.lower().endswith(".csv")
        ]


def open_text_stream(binary_stream) -> io.TextIOWrapper:
    # AI Hub files are UTF-8-sig. Keep this helper small and explicit so other
    # encodings can be added per dataset if needed.
    return io.TextIOWrapper(binary_stream, encoding="utf-8-sig", newline="")


def iter_rows_from_path(path: Path) -> Iterable[dict[str, str]]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            for info in csv_infos(path):
                with zf.open(info) as fh:
                    with open_text_stream(fh) as text_fh:
                        reader = csv.DictReader(text_fh)
                        for row in reader:
                            yield row
    else:
        with path.open("rb") as fh:
            with open_text_stream(fh) as text_fh:
                reader = csv.DictReader(text_fh)
                for row in reader:
                    yield row


def iter_rows(paths: list[Path]) -> Iterable[dict[str, str]]:
    for path in paths:
        yield from iter_rows_from_path(path)


def read_header(path: Path) -> list[str]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            info = csv_infos(path)[0]
            with zf.open(info) as fh:
                with open_text_stream(fh) as text_fh:
                    return next(csv.reader(text_fh))
    with path.open("rb") as fh:
        with open_text_stream(fh) as text_fh:
            return next(csv.reader(text_fh))


def load_config(path: Path) -> dict[str, object]:
    config = json.loads(path.read_text(encoding="utf-8"))
    try:
        config["config_path"] = str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        config["config_path"] = path.name
    config["_config_dir"] = str(path.resolve().parent)
    return config


def split_paths(config: dict[str, object]) -> dict[str, list[Path]]:
    result: dict[str, list[Path]] = {}
    config_dir = Path(str(config.get("_config_dir", ".")))
    for split in config["splits"]:
        result[split["name"]] = []
        for raw_path in split["paths"]:
            expanded = os.path.expandvars(os.path.expanduser(str(raw_path)))
            path = Path(expanded)
            if not path.is_absolute():
                path = config_dir / path
            result[split["name"]].append(path)
    return result


def positive_label(config: dict[str, object], row: dict[str, str]) -> int:
    value = normalize(row.get(config["label_col"], ""))
    return int(value in set(config.get("positive_values", ["1", "1.0", "Y", "true", "True"])))


def row_hash(row: dict[str, str], cols: list[str]) -> str:
    text = "\x1f".join(normalize(row.get(col, "")) for col in cols)
    return hashlib.blake2b(text.encode("utf-8"), digest_size=12).hexdigest()


def entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    value = 0.0
    for count in counter.values():
        p = count / total
        value -= p * math.log2(p)
    return value


def js_divergence(left: Counter[str], right: Counter[str]) -> float:
    left_total = sum(left.values())
    right_total = sum(right.values())
    if left_total == 0 or right_total == 0:
        return 0.0
    js = 0.0
    for key in set(left) | set(right):
        p = left[key] / left_total
        q = right[key] / right_total
        m = (p + q) / 2.0
        if p:
            js += 0.5 * p * math.log2(p / m)
        if q:
            js += 0.5 * q * math.log2(q / m)
    return js


def overlap_coefficient(pos_counts: Counter[str], neg_counts: Counter[str]) -> float | None:
    pos_total = sum(pos_counts.values())
    neg_total = sum(neg_counts.values())
    if pos_total == 0 or neg_total == 0:
        return None
    overlap = 0.0
    for key in set(pos_counts) | set(neg_counts):
        overlap += min(pos_counts[key] / pos_total, neg_counts[key] / neg_total)
    return overlap


def percentile_from_counter(counter: Counter[float], q: float) -> float | None:
    total = sum(counter.values())
    if total == 0:
        return None
    target = max(1, math.ceil(total * q))
    running = 0
    for value in sorted(counter):
        running += counter[value]
        if running >= target:
            return value
    return None


def numeric_summary(counter: Counter[float]) -> dict[str, object]:
    total = sum(counter.values())
    if not total:
        return {}
    values = sorted(counter)
    return {
        "count": total,
        "distinct": len(counter),
        "min": values[0],
        "p01": percentile_from_counter(counter, 0.01),
        "p05": percentile_from_counter(counter, 0.05),
        "p25": percentile_from_counter(counter, 0.25),
        "p50": percentile_from_counter(counter, 0.50),
        "p75": percentile_from_counter(counter, 0.75),
        "p95": percentile_from_counter(counter, 0.95),
        "p99": percentile_from_counter(counter, 0.99),
        "max": values[-1],
        "mean": sum(value * count for value, count in counter.items()) / total,
        "top_values": [
            {"value": value, "count": count, "share": count / total}
            for value, count in counter.most_common(10)
        ],
        "top1_share": counter.most_common(1)[0][1] / total,
        "top10_share": sum(count for _, count in counter.most_common(10)) / total,
        "multiple_100_share": sum(count for value, count in counter.items() if value % 100 == 0) / total,
        "multiple_1000_share": sum(count for value, count in counter.items() if value % 1000 == 0) / total,
        "zero_count": counter.get(0.0, 0),
        "negative_count": sum(count for value, count in counter.items() if value < 0),
    }


def numeric_log_bin(value: object) -> str:
    number = parse_float(value)
    if number is None:
        return NA
    sign = "neg" if number < 0 else "pos"
    bucket = int(math.floor(math.log10(abs(number) + 1.0) * 8))
    return f"{sign}_{bucket}"


def date_tokens(col: str, value: object) -> list[str]:
    text = normalize(value)
    if text == NA:
        return [f"{col}=NA"]
    _, ym, ymd = parse_year_month_day(text)
    if ymd:
        return [f"{col}_month={ym[4:6]}", f"{col}_day={ymd[6:8]}"]
    if ym:
        return [f"{col}_month={ym[4:6]}"]
    return [f"{col}={text}"]


def row_tokens(
    row: dict[str, str],
    feature_cols: list[str],
    date_cols: set[str],
    numeric_cols: set[str],
) -> list[str]:
    tokens: list[str] = []
    for col in feature_cols:
        if col in date_cols:
            tokens.extend(date_tokens(col, row.get(col, "")))
        elif col in numeric_cols:
            tokens.append(f"{col}_logbin={numeric_log_bin(row.get(col, ''))}")
        else:
            tokens.append(f"{col}={normalize(row.get(col, ''))}")
    return tokens


class EvidenceNB:
    def __init__(self, alpha: float = 1.0, weight_clip: float = 4.0) -> None:
        self.alpha = alpha
        self.weight_clip = weight_clip
        self.pos_rows = 0
        self.neg_rows = 0
        self.counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    def update(self, tokens: list[str], y: int) -> None:
        if y:
            self.pos_rows += 1
            index = 1
        else:
            self.neg_rows += 1
            index = 0
        for token in tokens:
            self.counts[token][index] += 1

    def score(self, tokens: list[str]) -> float:
        score = math.log((self.pos_rows + self.alpha) / (self.neg_rows + self.alpha))
        pos_denom = self.pos_rows + 2 * self.alpha
        neg_denom = self.neg_rows + 2 * self.alpha
        for token in tokens:
            neg_count, pos_count = self.counts.get(token, [0, 0])
            pos_rate = (pos_count + self.alpha) / pos_denom
            neg_rate = (neg_count + self.alpha) / neg_denom
            weight = math.log(pos_rate / neg_rate)
            score += max(-self.weight_clip, min(self.weight_clip, weight))
        return score


def roc_auc(y: list[int], scores: list[float]) -> float | None:
    n = len(y)
    pos = sum(y)
    neg = n - pos
    if pos == 0 or neg == 0:
        return None
    order = sorted(range(n), key=lambda index: scores[index])
    rank_sum = 0.0
    start = 0
    while start < n:
        end = start + 1
        while end < n and scores[order[end]] == scores[order[start]]:
            end += 1
        average_rank = (start + 1 + end) / 2.0
        rank_sum += average_rank * sum(y[order[i]] for i in range(start, end))
        start = end
    return (rank_sum - pos * (pos + 1) / 2.0) / (pos * neg)


def average_precision(y: list[int], scores: list[float]) -> float | None:
    pos = sum(y)
    if pos == 0:
        return None
    order = sorted(range(len(y)), key=lambda index: scores[index], reverse=True)
    hits = 0
    total_precision = 0.0
    for rank, index in enumerate(order, start=1):
        if y[index]:
            hits += 1
            total_precision += hits / rank
    return total_precision / pos


def topk(y: list[int], scores: list[float]) -> dict[str, object]:
    total = len(y)
    positives = sum(y)
    prevalence = positives / total if total else 0.0
    order = sorted(range(total), key=lambda index: scores[index], reverse=True)
    result = {}
    for rate in [0.001, 0.005, 0.01, 0.02, 0.05]:
        k = max(1, round(total * rate))
        hits = sum(y[index] for index in order[:k])
        precision = hits / k
        result[f"top_{rate:.1%}"] = {
            "k": k,
            "hits": hits,
            "precision": precision,
            "recall": hits / positives if positives else None,
            "lift": precision / prevalence if prevalence else None,
        }
    return result


def evaluate_scores(y: list[int], scores: list[float]) -> dict[str, object]:
    return {
        "rows": len(y),
        "positives": sum(y),
        "prevalence": sum(y) / len(y) if y else None,
        "roc_auc": roc_auc(y, scores),
        "average_precision": average_precision(y, scores),
        "topk": topk(y, scores),
    }


def run_nb_baseline(
    config: dict[str, object],
    train_paths: list[Path],
    test_paths: list[Path],
    feature_cols: list[str],
) -> dict[str, object]:
    date_cols = set(config.get("date_cols", []))
    numeric_cols = set(config.get("numeric_cols", []))
    model = EvidenceNB()
    train_rows = 0
    train_pos = 0
    for row in iter_rows(train_paths):
        y = positive_label(config, row)
        train_rows += 1
        train_pos += y
        model.update(row_tokens(row, feature_cols, date_cols, numeric_cols), y)

    y_values: list[int] = []
    scores: list[float] = []
    for row in iter_rows(test_paths):
        y_values.append(positive_label(config, row))
        scores.append(model.score(row_tokens(row, feature_cols, date_cols, numeric_cols)))

    metrics = evaluate_scores(y_values, scores)
    metrics["train_rows"] = train_rows
    metrics["train_positives"] = train_pos
    metrics["train_prevalence"] = train_pos / train_rows if train_rows else None
    return metrics


def run_temporal_baseline(
    config: dict[str, object],
    all_paths: list[Path],
    header: list[str],
    feature_cols: list[str],
) -> dict[str, object] | None:
    date_cols = list(config.get("date_cols", []))
    if not date_cols:
        return None
    date_col = date_cols[-1]
    years = Counter()
    for row in iter_rows(all_paths):
        year, _, _ = parse_year_month_day(row.get(date_col, ""))
        if year:
            years[year] += 1
    if len(years) < 2:
        return None
    test_year = sorted(years)[-1]

    model = EvidenceNB()
    train_rows = 0
    train_pos = 0
    date_set = set(config.get("date_cols", []))
    numeric_set = set(config.get("numeric_cols", []))
    for row in iter_rows(all_paths):
        year, _, _ = parse_year_month_day(row.get(date_col, ""))
        if not year or year >= test_year:
            continue
        y = positive_label(config, row)
        train_rows += 1
        train_pos += y
        model.update(row_tokens(row, feature_cols, date_set, numeric_set), y)

    y_values: list[int] = []
    scores: list[float] = []
    for row in iter_rows(all_paths):
        year, _, _ = parse_year_month_day(row.get(date_col, ""))
        if year != test_year:
            continue
        y_values.append(positive_label(config, row))
        scores.append(model.score(row_tokens(row, feature_cols, date_set, numeric_set)))

    if not y_values:
        return None
    metrics = evaluate_scores(y_values, scores)
    metrics["date_col"] = date_col
    metrics["test_year"] = test_year
    metrics["train_rows"] = train_rows
    metrics["train_positives"] = train_pos
    metrics["train_prevalence"] = train_pos / train_rows if train_rows else None
    return metrics


def best_amount_rules(
    total_counts: Counter[float],
    pos_counts: Counter[float],
) -> dict[str, object]:
    total = sum(total_counts.values())
    positives = sum(pos_counts.values())
    if not total or not positives:
        return {}
    values = sorted(total_counts)
    prefix_rows = 0
    prefix_pos = 0
    zero_positive_prefix = None
    best_high = None
    best_low = None
    suffix_rows = total
    suffix_pos = positives
    for value in values:
        rows_at_value = total_counts[value]
        pos_at_value = pos_counts[value]
        prefix_rows += rows_at_value
        prefix_pos += pos_at_value
        if prefix_pos == 0:
            zero_positive_prefix = {
                "threshold_lte": value,
                "rows": prefix_rows,
                "share": prefix_rows / total,
            }
        low_precision = prefix_pos / prefix_rows
        low_recall = prefix_pos / positives
        low_f1 = (
            2 * low_precision * low_recall / (low_precision + low_recall)
            if low_precision + low_recall
            else 0
        )
        if best_low is None or low_f1 > best_low["f1"]:
            best_low = {
                "rule": f"amount <= {value:g}",
                "rows": prefix_rows,
                "precision": low_precision,
                "recall": low_recall,
                "f1": low_f1,
            }
        high_precision = suffix_pos / suffix_rows if suffix_rows else 0
        high_recall = suffix_pos / positives
        high_f1 = (
            2 * high_precision * high_recall / (high_precision + high_recall)
            if high_precision + high_recall
            else 0
        )
        if best_high is None or high_f1 > best_high["f1"]:
            best_high = {
                "rule": f"amount >= {value:g}",
                "rows": suffix_rows,
                "precision": high_precision,
                "recall": high_recall,
                "f1": high_f1,
            }
        suffix_rows -= rows_at_value
        suffix_pos -= pos_at_value
    return {
        "zero_positive_low_region": zero_positive_prefix,
        "best_low_threshold": best_low,
        "best_high_threshold": best_high,
    }


def threshold_group(thresholds: dict[str, object], name: str) -> dict[str, object]:
    value = thresholds.get(name, {})
    return value if isinstance(value, dict) else {}


def add_test(
    tests: list[dict[str, object]],
    test_id: str,
    name: str,
    status: str,
    details: str,
    metric: object | None = None,
    threshold: object | None = None,
) -> None:
    tests.append(
        {
            "id": test_id,
            "name": name,
            "status": status,
            "metric": metric,
            "threshold": threshold,
            "details": details,
        }
    )


def evaluate_t0(
    config: dict[str, object],
    thresholds: dict[str, object],
) -> list[dict[str, object]]:
    tests: list[dict[str, object]] = []
    published = config.get("published_evaluation")
    if not isinstance(published, dict):
        add_test(
            tests,
            "T0",
            "Evaluation integrity",
            "INFO",
            "No published evaluation metadata was provided in the config.",
        )
        return tests

    t0 = threshold_group(thresholds, "t0_evaluation_integrity")
    if published.get("concatenates_splits_before_random_resplit"):
        status = "FAIL" if t0.get("fail_if_concat_then_random_resplit", True) else "WARN"
        add_test(
            tests,
            "T0.1",
            "Published split integrity",
            status,
            "Published model path concatenates supplied splits and performs a new random split.",
        )
    else:
        add_test(
            tests,
            "T0.1",
            "Published split integrity",
            "PASS",
            "No split reconcat/random-resplit issue is recorded in the config.",
        )

    if config.get("date_cols") and not published.get("uses_temporal_holdout", False):
        status = "WARN" if t0.get("warn_if_no_temporal_holdout_with_dates", True) else "INFO"
        add_test(
            tests,
            "T0.2",
            "Temporal validation",
            status,
            "Event-date columns exist, but the published evaluation metadata does not record a temporal holdout.",
        )

    if config.get("id_cols") and not published.get("uses_entity_holdout", False):
        status = "WARN" if t0.get("warn_if_no_entity_holdout_with_ids", True) else "INFO"
        add_test(
            tests,
            "T0.3",
            "Entity holdout",
            status,
            "Entity ID columns exist, but the published evaluation metadata does not record an entity holdout.",
        )

    if published.get("type_classification_filters_to_positive_rows"):
        status = (
            "FAIL"
            if t0.get("fail_if_type_classification_filters_to_positive_rows", False)
            else "INFO"
        )
        add_test(
            tests,
            "T0.4",
            "Type-classification scope",
            status,
            "Type classification is recorded as a fraud-only task, so it is not evidence of detection validity.",
        )
    return tests


def evaluate_t1(
    baselines: dict[str, object],
    amount_rules: dict[str, object],
    thresholds: dict[str, object],
) -> list[dict[str, object]]:
    tests: list[dict[str, object]] = []
    t1 = threshold_group(thresholds, "t1_amount_only_baseline")
    amount_metric = baselines.get("provided_split_amount_only_nb")
    no_id_metric = baselines.get("provided_split_no_id_nb")

    if isinstance(amount_metric, dict):
        roc_auc_value = amount_metric.get("roc_auc")
        roc_threshold = t1.get("fail_if_roc_auc_gte", 0.95)
        if isinstance(roc_auc_value, (int, float)):
            add_test(
                tests,
                "T1.1",
                "Amount-only ROC-AUC",
                "FAIL" if roc_auc_value >= roc_threshold else "PASS",
                "Amount-only baseline is evaluated on the provided split.",
                metric=roc_auc_value,
                threshold=f">= {roc_threshold}",
            )

        ap_value = amount_metric.get("average_precision")
        if isinstance(no_id_metric, dict):
            no_id_ap = no_id_metric.get("average_precision")
            ratio_threshold = t1.get("fail_if_average_precision_ratio_gte", 0.80)
            if isinstance(ap_value, (int, float)) and isinstance(no_id_ap, (int, float)) and no_id_ap:
                ratio = ap_value / no_id_ap
                add_test(
                    tests,
                    "T1.2",
                    "Amount-only share of no-ID PR-AUC",
                    "FAIL" if ratio >= ratio_threshold else "PASS",
                    "Compares amount-only average precision to the no-ID baseline.",
                    metric=ratio,
                    threshold=f">= {ratio_threshold}",
                )
    else:
        add_test(
            tests,
            "T1",
            "Amount-only baseline",
            "INFO",
            "No amount-only baseline was available.",
        )

    f1_threshold = t1.get("fail_if_best_threshold_f1_gte", 0.70)
    best_f1 = None
    best_rule = None
    for col, rules in amount_rules.items():
        if not isinstance(rules, dict):
            continue
        for rule_key in ["best_high_threshold", "best_low_threshold"]:
            rule = rules.get(rule_key)
            if isinstance(rule, dict) and isinstance(rule.get("f1"), (int, float)):
                if best_f1 is None or rule["f1"] > best_f1:
                    best_f1 = rule["f1"]
                    best_rule = f"{col}: {rule.get('rule')}"
    if best_f1 is not None:
        add_test(
            tests,
            "T1.3",
            "Best one-sided amount threshold",
            "FAIL" if best_f1 >= f1_threshold else "PASS",
            f"Best threshold rule: {best_rule}.",
            metric=best_f1,
            threshold=f">= {f1_threshold}",
        )
    return tests


def evaluate_t5(
    amount_rules: dict[str, object],
    thresholds: dict[str, object],
) -> list[dict[str, object]]:
    tests: list[dict[str, object]] = []
    t5 = threshold_group(thresholds, "t5_zero_fraud_region")
    fail_share = t5.get("fail_if_row_share_gte", 0.90)
    warn_share = t5.get("warn_if_row_share_gte", 0.50)
    found = False
    for col, rules in amount_rules.items():
        if not isinstance(rules, dict):
            continue
        region = rules.get("zero_positive_low_region")
        if not isinstance(region, dict):
            continue
        found = True
        share = region.get("share", 0)
        if share >= fail_share:
            status = "FAIL"
            threshold = f">= {fail_share}"
        elif share >= warn_share:
            status = "WARN"
            threshold = f">= {warn_share}"
        else:
            status = "PASS"
            threshold = f"< {warn_share}"
        add_test(
            tests,
            "T5",
            "Zero-fraud low-amount region",
            status,
            f"{col} <= {number(region.get('threshold_lte'))} covers {region.get('rows'):,} rows with zero positives.",
            metric=share,
            threshold=threshold,
        )
    if not found:
        add_test(
            tests,
            "T5",
            "Zero-fraud low-amount region",
            "PASS",
            "No zero-positive low-amount region was found.",
        )
    return tests


def evaluate_t9(
    numeric_profiles: dict[str, object],
    amount_cols: set[str],
    thresholds: dict[str, object],
) -> list[dict[str, object]]:
    tests: list[dict[str, object]] = []
    t9 = threshold_group(thresholds, "t9_cardinality_sanity")
    for col, profile_obj in numeric_profiles.items():
        if col not in amount_cols or not isinstance(profile_obj, dict):
            continue
        distinct = profile_obj.get("distinct")
        top10 = profile_obj.get("top10_share")
        round1000 = profile_obj.get("multiple_1000_share")

        if isinstance(distinct, int):
            threshold = t9.get("fail_if_amount_distinct_lte", 100)
            add_test(
                tests,
                "T9.1",
                "Amount distinct-value count",
                "FAIL" if distinct <= threshold else "PASS",
                f"{col} has {distinct:,} distinct amount values.",
                metric=distinct,
                threshold=f"<= {threshold}",
            )

        if isinstance(top10, (int, float)):
            fail_top10 = t9.get("fail_if_amount_top10_share_gte", 0.90)
            warn_top10 = t9.get("warn_if_amount_top10_share_gte", 0.70)
            if top10 >= fail_top10:
                status = "FAIL"
                threshold = f">= {fail_top10}"
            elif top10 >= warn_top10:
                status = "WARN"
                threshold = f">= {warn_top10}"
            else:
                status = "PASS"
                threshold = f"< {warn_top10}"
            add_test(
                tests,
                "T9.2",
                "Amount top-10 concentration",
                status,
                f"Top 10 {col} values cover {top10:.2%} of rows.",
                metric=top10,
                threshold=threshold,
            )

        if isinstance(round1000, (int, float)):
            threshold = t9.get("warn_if_round_thousand_share_gte", 0.95)
            add_test(
                tests,
                "T9.3",
                "Round-amount concentration",
                "WARN" if round1000 >= threshold else "PASS",
                f"{col} values are multiples of 1,000 for {round1000:.2%} of rows.",
                metric=round1000,
                threshold=f">= {threshold}",
            )
    return tests


def audit(config: dict[str, object], thresholds: dict[str, object]) -> dict[str, object]:
    paths_by_split = split_paths(config)
    split_names = list(paths_by_split)
    all_paths = [path for paths in paths_by_split.values() for path in paths]
    header = read_header(all_paths[0])
    label_col = config["label_col"]
    leak_cols = set(config.get("leak_cols", [])) | {label_col}
    id_cols = set(config.get("id_cols", []))
    feature_cols = [col for col in header if col not in leak_cols]
    no_id_feature_cols = [col for col in feature_cols if col not in id_cols]
    amount_cols = set(config.get("amount_cols", []))
    numeric_cols = set(config.get("numeric_cols", []))
    date_cols = set(config.get("date_cols", []))
    primary_date_col = list(config.get("date_cols", []))[-1] if config.get("date_cols") else None

    combined_rows = 0
    combined_pos = 0
    missing = Counter()
    value_counts: dict[str, Counter[str]] = defaultdict(Counter)
    value_pos: dict[str, Counter[str]] = defaultdict(Counter)
    numeric_counts: dict[str, Counter[float]] = defaultdict(Counter)
    numeric_pos: dict[str, Counter[float]] = defaultdict(Counter)
    date_by_month = Counter()
    date_pos_by_month = Counter()
    date_by_year = Counter()
    date_pos_by_year = Counter()
    full_hashes = Counter()
    feature_hashes = Counter()
    split_stats = {}
    split_value_counts: dict[str, dict[str, Counter[str]]] = {}

    for split_name, paths in paths_by_split.items():
        rows = 0
        positives = 0
        split_missing = Counter()
        split_year = Counter()
        split_year_pos = Counter()
        split_values: dict[str, Counter[str]] = defaultdict(Counter)
        for row in iter_rows(paths):
            rows += 1
            combined_rows += 1
            y = positive_label(config, row)
            positives += y
            combined_pos += y
            full_hashes[row_hash(row, header)] += 1
            feature_hashes[row_hash(row, [col for col in header if col != label_col])] += 1

            for col in header:
                value = normalize(row.get(col, ""))
                if value == NA:
                    missing[col] += 1
                    split_missing[col] += 1
                value_counts[col][value] += 1
                value_pos[col][value] += y
                split_values[col][value] += 1

            for col in numeric_cols:
                number = parse_float(row.get(col, ""))
                if number is not None:
                    numeric_counts[col][number] += 1
                    numeric_pos[col][number] += y

            if primary_date_col:
                year, ym, _ = parse_year_month_day(row.get(primary_date_col, ""))
                if year:
                    date_by_year[year] += 1
                    date_pos_by_year[year] += y
                    split_year[year] += 1
                    split_year_pos[year] += y
                if ym:
                    date_by_month[ym] += 1
                    date_pos_by_month[ym] += y

        split_value_counts[split_name] = split_values
        split_stats[split_name] = {
            "rows": rows,
            "positives": positives,
            "prevalence": positives / rows if rows else None,
            "missing_rate_top": [
                {"column": col, "missing_rate": count / rows}
                for col, count in split_missing.most_common(10)
                if count
            ],
            "by_year": {
                year: {
                    "rows": split_year[year],
                    "positives": split_year_pos[year],
                    "prevalence": split_year_pos[year] / split_year[year],
                }
                for year in sorted(split_year)
            },
        }

    prevalence = combined_pos / combined_rows if combined_rows else 0.0
    duplicate_full = sum(count - 1 for count in full_hashes.values() if count > 1)
    duplicate_features = sum(count - 1 for count in feature_hashes.values() if count > 1)

    columns = []
    for col in header:
        counts = value_counts[col]
        ent = entropy(counts)
        columns.append(
            {
                "column": col,
                "role": "label_or_leak"
                if col in leak_cols
                else "id"
                if col in id_cols
                else "feature",
                "missing_rate": missing[col] / combined_rows if combined_rows else None,
                "distinct": len(counts),
                "cardinality_ratio": len(counts) / combined_rows if combined_rows else None,
                "top1_share": counts.most_common(1)[0][1] / combined_rows if counts else None,
                "top5_share": sum(n for _, n in counts.most_common(5)) / combined_rows
                if counts
                else None,
                "entropy": ent,
                "effective_categories": 2**ent if ent else 0.0,
                "top_values": [
                    {
                        "value": value,
                        "count": count,
                        "share": count / combined_rows,
                        "positive_rate": value_pos[col][value] / count if count else None,
                    }
                    for value, count in counts.most_common(8)
                ],
            }
        )

    single_feature_rules = []
    overlap_by_col = []
    min_support = int(config.get("min_rule_support", thresholds.get("min_rule_support", 100)))
    for col in feature_cols:
        pos_counter = Counter()
        neg_counter = Counter()
        for value, count in value_counts[col].items():
            pos_count = value_pos[col][value]
            neg_count = count - pos_count
            if pos_count:
                pos_counter[value] = pos_count
            if neg_count:
                neg_counter[value] = neg_count
            if count < min_support:
                continue
            positive_rate = pos_count / count
            lift = positive_rate / prevalence if prevalence else None
            recall = pos_count / combined_pos if combined_pos else None
            single_feature_rules.append(
                {
                    "column": col,
                    "value": value,
                    "is_id": col in id_cols,
                    "count": count,
                    "share": count / combined_rows,
                    "positive": pos_count,
                    "positive_rate": positive_rate,
                    "recall": recall,
                    "lift": lift,
                }
            )
        overlap_by_col.append(
            {
                "column": col,
                "is_id": col in id_cols,
                "overlap": overlap_coefficient(pos_counter, neg_counter),
            }
        )

    single_feature_rules.sort(
        key=lambda item: (
            item["lift"] if item["lift"] is not None else -1,
            item["positive_rate"],
            item["count"],
        ),
        reverse=True,
    )
    overlap_by_col.sort(
        key=lambda item: item["overlap"] if item["overlap"] is not None else 2.0
    )

    numeric_profiles = {
        col: numeric_summary(counts) for col, counts in numeric_counts.items()
    }
    amount_rules = {
        col: best_amount_rules(numeric_counts[col], numeric_pos[col])
        for col in amount_cols
        if col in numeric_counts
    }

    split_drift = []
    if len(split_names) >= 2:
        left = split_names[0]
        right = split_names[1]
        for col in feature_cols:
            split_drift.append(
                {
                    "column": col,
                    "is_id": col in id_cols,
                    "js_divergence": js_divergence(
                        split_value_counts[left][col],
                        split_value_counts[right][col],
                    ),
                }
            )
        split_drift.sort(key=lambda item: item["js_divergence"], reverse=True)

    baselines = {}
    if len(split_names) >= 2:
        train_paths = paths_by_split[split_names[0]]
        test_paths = paths_by_split[split_names[1]]
        baselines["provided_split_no_id_nb"] = run_nb_baseline(
            config, train_paths, test_paths, no_id_feature_cols
        )
        amount_feature_cols = [col for col in no_id_feature_cols if col in amount_cols]
        if amount_feature_cols:
            baselines["provided_split_amount_only_nb"] = run_nb_baseline(
                config, train_paths, test_paths, amount_feature_cols
            )

    temporal = run_temporal_baseline(config, all_paths, header, no_id_feature_cols)
    if temporal:
        baselines["temporal_holdout_no_id_nb"] = temporal
    amount_temporal_cols = [col for col in no_id_feature_cols if col in amount_cols]
    if amount_temporal_cols:
        amount_temporal = run_temporal_baseline(
            config, all_paths, header, amount_temporal_cols
        )
        if amount_temporal:
            baselines["temporal_holdout_amount_only_nb"] = amount_temporal

    tests: list[dict[str, object]] = []
    tests.extend(evaluate_t0(config, thresholds))
    tests.extend(evaluate_t1(baselines, amount_rules, thresholds))
    tests.extend(evaluate_t5(amount_rules, thresholds))
    tests.extend(evaluate_t9(numeric_profiles, amount_cols, thresholds))

    red_flags = []
    for test in tests:
        if test["status"] in {"FAIL", "WARN"}:
            red_flags.append(
                {
                    "severity": str(test["status"]).lower(),
                    "gate": test["id"],
                    "message": str(test["details"]),
                }
            )

    t2 = threshold_group(thresholds, "t2_single_feature_shortcut")
    duplicate_thresholds = threshold_group(thresholds, "duplicates")
    split_thresholds = threshold_group(thresholds, "split_drift")

    for item in single_feature_rules:
        if item["is_id"]:
            continue
        if item["count"] < min_support:
            continue
        if (
            item["positive_rate"] >= t2.get("fail_if_positive_rate_gte", 0.5)
            and item["lift"]
            and item["lift"] >= t2.get("fail_if_lift_gte", 20.0)
        ):
            red_flags.append(
                {
                    "severity": "fail",
                    "gate": "T2",
                    "message": (
                        f"{item['column']}={item['value']} has positive_rate "
                        f"{item['positive_rate']:.1%}, lift {item['lift']:.1f}x "
                        f"(n={item['count']:,})."
                    ),
                }
            )
            if len([flag for flag in red_flags if flag["gate"] == "T2"]) >= 10:
                break

    duplicate_warn = duplicate_thresholds.get("warn_if_duplicate_feature_rows_gte", 0.01)
    if duplicate_features / combined_rows >= duplicate_warn:
        red_flags.append(
            {
                "severity": "warn",
                "gate": "G0",
                "message": (
                    f"Duplicate rows excluding label: {duplicate_features:,} "
                    f"({duplicate_features / combined_rows:.1%})."
                ),
            }
        )

    if split_drift:
        non_id_js = [item["js_divergence"] for item in split_drift if not item["is_id"]]
        max_js_threshold = split_thresholds.get("warn_if_max_non_id_js_lte", 0.01)
        if non_id_js and max(non_id_js) < max_js_threshold:
            red_flags.append(
                {
                    "severity": "warn",
                    "gate": "G4",
                    "message": "Train/validation non-ID distributions are nearly identical.",
                }
            )

    verdict = "PASS"
    if any(flag["severity"] == "fail" for flag in red_flags):
        verdict = "FAIL"
    elif red_flags:
        verdict = "WARN"

    return {
        "name": config["name"],
        "title": config.get("title", config["name"]),
        "config_path": config.get("config_path"),
        "verdict": verdict,
        "row_profile": {
            "rows": combined_rows,
            "positives": combined_pos,
            "prevalence": prevalence,
            "duplicate_full_rows": duplicate_full,
            "duplicate_rows_excluding_label": duplicate_features,
            "date_by_year": {
                year: {
                    "rows": date_by_year[year],
                    "positives": date_pos_by_year[year],
                    "prevalence": date_pos_by_year[year] / date_by_year[year],
                }
                for year in sorted(date_by_year)
            },
            "date_by_month": {
                ym: {
                    "rows": date_by_month[ym],
                    "positives": date_pos_by_month[ym],
                    "prevalence": date_pos_by_month[ym] / date_by_month[ym],
                }
                for ym in sorted(date_by_month)
            },
        },
        "split_stats": split_stats,
        "columns": columns,
        "numeric_profiles": numeric_profiles,
        "single_feature_rules_top": single_feature_rules[:50],
        "single_feature_rules_top_non_id": [
            item for item in single_feature_rules if not item["is_id"]
        ][:50],
        "class_overlap_lowest": overlap_by_col[:25],
        "amount_rules": amount_rules,
        "split_drift_top": split_drift[:25],
        "baselines": baselines,
        "thresholds": thresholds,
        "tests": tests,
        "red_flags": red_flags,
    }


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def number(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value:,.0f}"
        return f"{value:.4g}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def metric_line(name: str, metric: dict[str, object]) -> str:
    top1 = metric.get("topk", {}).get("top_1.0%", {})
    return (
        f"- {name}: ROC-AUC {number(metric.get('roc_auc'))}, "
        f"PR-AUC {number(metric.get('average_precision'))}, "
        f"Top 1% P={pct(top1.get('precision'))}, R={pct(top1.get('recall'))}"
    )


def render_markdown(result: dict[str, object]) -> str:
    profile = result["row_profile"]
    lines = [
        f"# {result['title']} Validity Audit",
        "",
        f"Verdict: **{result['verdict']}**",
        "",
        "## Overview",
        "",
        f"- Rows: {profile['rows']:,}",
        f"- Positives: {profile['positives']:,} ({pct(profile['prevalence'])})",
        f"- Duplicate full rows: {profile['duplicate_full_rows']:,}",
        f"- Duplicate rows excluding label: {profile['duplicate_rows_excluding_label']:,}",
        "",
    ]
    if result.get("tests"):
        lines.extend(
            [
                "## Test Verdicts",
                "",
                "| test | status | metric | threshold | details |",
                "|---|---:|---:|---:|---|",
            ]
        )
        for test in result["tests"]:
            metric = test.get("metric")
            if isinstance(metric, float):
                metric_text = f"{metric:.4g}"
            elif metric is None:
                metric_text = ""
            else:
                metric_text = str(metric)
            lines.append(
                f"| {test['id']} {test['name']} | {test['status']} | "
                f"{metric_text} | {test.get('threshold') or ''} | {test['details']} |"
            )
        lines.append("")

    if profile["date_by_year"]:
        lines.extend(["## Time Coverage", "", "| year | rows | prevalence |", "|---|---:|---:|"])
        for year, item in profile["date_by_year"].items():
            lines.append(f"| {year} | {item['rows']:,} | {pct(item['prevalence'])} |")
        lines.append("")

    lines.extend(["## Amount Profiles", ""])
    for col, item in result["numeric_profiles"].items():
        if not item:
            continue
        lines.append(
            f"- {col}: distinct {item['distinct']:,}, p50 {number(item['p50'])}, "
            f"p95 {number(item['p95'])}, p99 {number(item['p99'])}, max {number(item['max'])}, "
            f"top10 share {pct(item['top10_share'])}, round(1000) share {pct(item['multiple_1000_share'])}"
        )
    lines.append("")

    lines.extend(["## Single-Feature Shortcuts", "", "| column | value | n | pos rate | lift | recall |", "|---|---|---:|---:|---:|---:|"])
    for item in result["single_feature_rules_top_non_id"][:12]:
        lines.append(
            f"| {item['column']} | {item['value']} | {item['count']:,} | "
            f"{pct(item['positive_rate'])} | {number(item['lift'])}x | {pct(item['recall'])} |"
        )
    lines.append("")

    if result["amount_rules"]:
        lines.extend(["## Amount Threshold Rules", ""])
        for col, rules in result["amount_rules"].items():
            zero_region = rules.get("zero_positive_low_region")
            if zero_region:
                lines.append(
                    f"- {col}: zero-positive low region `{col} <= {number(zero_region['threshold_lte'])}` "
                    f"covers {zero_region['rows']:,} rows ({pct(zero_region['share'])})."
                )
            for rule_name in ["best_high_threshold", "best_low_threshold"]:
                rule = rules.get(rule_name)
                if rule:
                    lines.append(
                        f"- {col} {rule_name}: `{rule['rule']}`, "
                        f"P={pct(rule['precision'])}, R={pct(rule['recall'])}, F1={number(rule['f1'])}"
                    )
        lines.append("")

    if result["baselines"]:
        lines.extend(["## Baselines", ""])
        for name, metric in result["baselines"].items():
            lines.append(metric_line(name, metric))
        lines.append("")

    lines.extend(["## Split Drift", "", "| column | JS divergence | id? |", "|---|---:|---:|"])
    for item in result["split_drift_top"][:10]:
        lines.append(
            f"| {item['column']} | {item['js_divergence']:.5f} | {str(item['is_id']).lower()} |"
        )
    lines.append("")

    lines.extend(["## Red Flags", ""])
    if result["red_flags"]:
        for flag in result["red_flags"]:
            lines.append(f"- [{flag['severity'].upper()}][{flag['gate']}] {flag['message']}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fraud dataset validity harness")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--thresholds", type=Path, default=None)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    config = load_config(args.config)
    thresholds = load_thresholds(args.thresholds)
    result = audit(config, thresholds)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = render_markdown(result)
    (args.out / "audit.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
