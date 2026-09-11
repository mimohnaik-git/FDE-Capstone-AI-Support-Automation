"""Reproducible development-only holdout evaluation for Stage 3 classification."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, List, Sequence

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from src.classify import (
    CANONICAL_INTENTS,
    CANONICAL_URGENCIES,
    DEFAULT_TRAINING_DATA_PATH,
    FEATURE_FIELDS,
    MODEL_VERSION,
    RANDOM_SEED,
    build_model_bundle,
    load_training_tickets,
    predict_with_bundle,
    stratified_group_holdout,
    text_group,
    training_data_sha256,
)


def _percentile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _confidence_summary(values: Sequence[float]) -> Dict[str, Any]:
    bins = []
    for index in range(5):
        lower = index / 5
        upper = (index + 1) / 5
        count = sum(lower <= value < upper or (index == 4 and value == 1.0) for value in values)
        bins.append({"lower": lower, "upper": upper, "count": count})
    return {
        "minimum": round(min(values), 6),
        "maximum": round(max(values), 6),
        "mean": round(mean(values), 6),
        "median": round(median(values), 6),
        "p05": round(_percentile(values, 0.05), 6),
        "p95": round(_percentile(values, 0.95), 6),
        "bins": bins,
    }


def _top_confusions(y_true: Sequence[str], y_pred: Sequence[str], limit: int = 10) -> List[Dict[str, Any]]:
    counts = Counter((expected, predicted) for expected, predicted in zip(y_true, y_pred) if expected != predicted)
    return [
        {"expected": expected, "predicted": predicted, "count": count}
        for (expected, predicted), count in counts.most_common(limit)
    ]


def _task_metrics(y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]) -> Dict[str, Any]:
    report = classification_report(y_true, y_pred, labels=list(labels), output_dict=True, zero_division=0)
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 6),
        "macro_precision": round(float(report["macro avg"]["precision"]), 6),
        "macro_recall": round(float(report["macro avg"]["recall"]), 6),
        "macro_f1": round(float(report["macro avg"]["f1-score"]), 6),
        "per_class": {
            label: {
                "precision": round(float(report[label]["precision"]), 6),
                "recall": round(float(report[label]["recall"]), 6),
                "f1": round(float(report[label]["f1-score"]), 6),
                "support": int(report[label]["support"]),
            }
            for label in labels
        },
        "confusion_matrix_labels": list(labels),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=list(labels)).tolist(),
        "top_confusions": _top_confusions(y_true, y_pred),
    }


def evaluate_development_holdout(
    dataset_path: Path | str = DEFAULT_TRAINING_DATA_PATH,
    random_seed: int = RANDOM_SEED,
) -> Dict[str, Any]:
    tickets = load_training_tickets(dataset_path)
    train, holdout = stratified_group_holdout(tickets, random_seed=random_seed)
    bundle = build_model_bundle(train)
    predictions = [predict_with_bundle(bundle, ticket) for ticket in holdout]
    true_intents = [ticket["labels"]["intent"] for ticket in holdout]
    predicted_intents = [prediction["intent"] for prediction in predictions]
    true_urgencies = [ticket["labels"]["urgency"] for ticket in holdout]
    predicted_urgencies = [prediction["urgency"] for prediction in predictions]
    confidences = [prediction["confidence"] for prediction in predictions]
    train_groups = {text_group(ticket) for ticket in train}
    holdout_groups = {text_group(ticket) for ticket in holdout}
    result = {
        "evaluation_role": "development_holdout",
        "model_version": MODEL_VERSION,
        "dataset_path": str(Path(dataset_path)),
        "dataset_sha256": training_data_sha256(dataset_path),
        "split": {
            "method": "first fold of shuffled StratifiedGroupKFold(n_splits=5), stratified by intent and grouped by normalized subject+body",
            "random_seed": random_seed,
            "train_size": len(train),
            "holdout_size": len(holdout),
            "train_unique_text_groups": len(train_groups),
            "holdout_unique_text_groups": len(holdout_groups),
            "text_group_overlap": len(train_groups & holdout_groups),
        },
        "features": list(FEATURE_FIELDS),
        "intent": _task_metrics(true_intents, predicted_intents, CANONICAL_INTENTS),
        "urgency": _task_metrics(true_urgencies, predicted_urgencies, CANONICAL_URGENCIES),
        "confidence_distribution": _confidence_summary(confidences),
    }
    result["intent"]["precision_target"] = 0.85
    result["intent"]["target_status"] = "PASS" if result["intent"]["macro_precision"] >= 0.85 else "FAIL"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Stage 3 classification on a grouped development holdout")
    parser.add_argument("--dataset", default=str(DEFAULT_TRAINING_DATA_PATH))
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()
    result = evaluate_development_holdout(args.dataset, args.seed)
    rendered = json.dumps(result, indent=2)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
