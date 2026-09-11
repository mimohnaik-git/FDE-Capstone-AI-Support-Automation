"""Stage 18 fairness analysis and human-development-review preparation."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from evaluation.metrics import aggregate_metrics

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evaluation" / "results"
MIN_GROUP_SIZE = 20
SCHEMA_VERSION = "1.0"


def _load_tickets(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value and isinstance(value, list) and isinstance(value[0], list):
        value = value[0]
    if not isinstance(value, list):
        raise ValueError("Ticket dataset must be a list")
    return value


def _load_evidence(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    records = value.get("records")
    if not isinstance(records, list):
        raise ValueError("Evaluation evidence has no records")
    return records


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def segment_indices(tickets: Sequence[Mapping[str, Any]], dimension: str) -> tuple[dict[str, list[int]], dict[str, Any]]:
    """Return explicit/deterministic segments without demographic inference."""
    if dimension == "customer_tier":
        groups = {"enterprise": [], "other_tiers": []}
        for index, ticket in enumerate(tickets):
            tier = ticket.get("customer_tier")
            if tier == "enterprise":
                groups["enterprise"].append(index)
            elif tier in {"free", "standard", "business"}:
                groups["other_tiers"].append(index)
        return groups, {"source": "explicit customer_tier field", "inference": False}
    if dimension == "language_fluency":
        groups = {"fluent": [], "non_fluent": []}
        for index, ticket in enumerate(tickets):
            value = ticket.get("language_fluency")
            if value in groups:
                groups[value].append(index)
        return groups, {"source": "explicit language_fluency field", "inference": False}
    if dimension == "text_length":
        counts = [len(str(t.get("body") or t.get("content") or "").split()) for t in tickets]
        ordered = sorted(counts)
        median = (ordered[(len(ordered) - 1) // 2] + ordered[len(ordered) // 2]) / 2 if ordered else None
        groups = {"short": [], "long": []}
        if median is not None:
            for index, count in enumerate(counts):
                groups["short" if count <= median else "long"].append(index)
        return groups, {
            "source": "derived word count only", "inference": False, "median_words": median,
            "definition": "short <= dataset median; long > dataset median",
            "limitation": "Length is not a complexity label; complexity is NOT MEASURED.",
        }
    raise ValueError(f"Unsupported dimension: {dimension}")


def _value(metric: Mapping[str, Any] | None) -> float | None:
    value = (metric or {}).get("value")
    return float(value) if isinstance(value, (int, float)) else None


def _group_metrics(records: list[dict[str, Any]], tickets: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = aggregate_metrics(records, tickets)
    c, retrieval, routing = metrics["classification"], metrics["retrieval"], metrics["routing"]
    return {
        "intent_accuracy": c["intent"]["accuracy"],
        "intent_macro_f1": c["intent"]["macro_f1"],
        "urgency_accuracy": c["urgency"]["accuracy"],
        "urgency_macro_f1": c["urgency"]["macro_f1"],
        "retrieval_recall_at_3": retrieval["recall_at_3"],
        "retrieval_mrr": retrieval["mrr"],
        "routing_accuracy": routing["accuracy"],
        "automation_rate": routing["auto_response_rate"],
        "escalation_rate": routing["escalation_rate"],
    }


def evaluate_dimension(tickets: list[dict[str, Any]], records: list[dict[str, Any]], dimension: str) -> dict[str, Any]:
    groups, definition = segment_indices(tickets, dimension)
    output: dict[str, Any] = {"definition": definition, "minimum_group_size": MIN_GROUP_SIZE, "groups": {}}
    for name, indices in groups.items():
        row: dict[str, Any] = {"ticket_count": len(indices)}
        if len(indices) < MIN_GROUP_SIZE:
            row.update({"status": "NOT MEASURED", "reason": f"Fewer than {MIN_GROUP_SIZE} tickets."})
        else:
            row.update({
                "status": "MEASURED — NO FORMAL TARGET",
                "metrics": _group_metrics([records[i] for i in indices], [tickets[i] for i in indices]),
            })
        output["groups"][name] = row

    measured = [row for row in output["groups"].values() if "metrics" in row]
    for metric_name in (
        "intent_accuracy", "intent_macro_f1", "urgency_accuracy", "urgency_macro_f1",
        "retrieval_recall_at_3", "retrieval_mrr", "routing_accuracy", "automation_rate", "escalation_rate",
    ):
        values = [_value(row["metrics"].get(metric_name)) for row in measured]
        values = [value for value in values if value is not None]
        if len(values) < 2:
            for row in measured:
                if metric_name in row["metrics"]:
                    row["metrics"][metric_name]["difference_from_best_group"] = None
            continue
        best = min(values) if metric_name == "escalation_rate" else max(values)
        for row in measured:
            metric = row["metrics"].get(metric_name, {})
            current = _value(metric)
            metric["difference_from_best_group"] = round(
                (current - best) if metric_name == "escalation_rate" else (best - current), 6
            ) if current is not None else None
    return output


def build_fairness_results() -> dict[str, Any]:
    sources = {
        "DEVELOPMENT": (ROOT / "data/raw/development_tickets.json", RESULTS / "stage10-development.json"),
        "VALIDATION": (ROOT / "data/raw/validation_tickets.json", RESULTS / "validation-technical-rerun.json"),
    }
    evidence = {}
    for role, (dataset_path, result_path) in sources.items():
        tickets, records = _load_tickets(dataset_path), _load_evidence(result_path)
        if len(tickets) != len(records):
            raise ValueError(f"{role} evidence and dataset counts differ")
        evidence[role] = {
            "dataset_sha256": _sha256(dataset_path), "evaluation_sha256": _sha256(result_path),
            "ticket_count": len(tickets),
            "dimensions": {name: evaluate_dimension(tickets, records, name) for name in (
                "customer_tier", "language_fluency", "text_length",
            )},
        }
    freeze = json.loads((RESULTS / "stage12-freeze-manifest.json").read_text(encoding="utf-8"))
    frozen_files = freeze["fingerprints"]["files"]
    changed = [name for name, expected in frozen_files.items() if _sha256(ROOT / name) != expected]
    stage13_paths = [
        RESULTS / "validation-final.json", RESULTS / "validation-final.md",
        RESULTS / "validation-final.ccb57d71-618f-452d-88c5-ce017772fa6e.decisions.sqlite",
    ]
    return {
        "schema_version": SCHEMA_VERSION, "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_classification": ["DEVELOPMENT", "VALIDATION"],
        "method": {
            "separation": "Development and validation are reported separately; no pooling or tuning.",
            "minimum_group_size": MIN_GROUP_SIZE,
            "group_labels": "Only explicit tier/fluency fields; length uses deterministic word count.",
            "complexity": {"status": "NOT MEASURED", "reason": "No explicit complexity label exists."},
        },
        "results": evidence,
        "governance_threshold": {
            "metric": "cross_group_quality_difference", "target": "<5 percentage points",
            "status": "NOT MEASURED",
            "reason": "The registry requires the same human-reviewed quality outcome; human reviews are blank.",
        },
        "evidence_integrity": {
            "original_production_fingerprint": freeze["fingerprints"]["aggregate_sha256"],
            "production_fingerprint_unchanged": not changed, "changed_frozen_files": changed,
            "thresholds": {"classification": 0.80, "retrieval": 0.30},
            "stage13_artifact_sha256": {path.name: _sha256(path) for path in stage13_paths},
            "post_validation_tuning": False, "artificial_group_labels_added": False,
            "human_scores_fabricated": False,
        },
        "limitations": [
            "Automated subgroup gaps do not establish customer outcome fairness.",
            "Small groups are not assigned performance conclusions.",
            "No protected attributes were inferred and no post-validation tuning was performed.",
        ],
    }


def render_fairness_markdown(result: Mapping[str, Any]) -> str:
    lines = ["# Stage 18 Fairness Analysis", "", "Evidence: DEVELOPMENT and VALIDATION reported separately.", ""]
    for role, evidence in result["results"].items():
        lines.extend([f"## {role}", ""])
        for dimension, section in evidence["dimensions"].items():
            lines.extend([f"### {dimension}", "", "| Group | N | Status | Intent acc | Urgency acc | Recall@3 | Routing acc | Automation | Escalation |", "|---|---:|---|---:|---:|---:|---:|---:|---:|"])
            for name, row in section["groups"].items():
                metrics = row.get("metrics", {})
                show = lambda key: "—" if _value(metrics.get(key)) is None else f"{_value(metrics[key]):.3f}"
                lines.append(f"| {name} | {row['ticket_count']} | {row['status']} | {show('intent_accuracy')} | {show('urgency_accuracy')} | {show('retrieval_recall_at_3')} | {show('routing_accuracy')} | {show('automation_rate')} | {show('escalation_rate')} |")
            lines.append("")
            lines.extend(["Differences from the best eligible group (absolute rate; escalation uses the lowest rate as best):", ""])
            for name, row in section["groups"].items():
                if "metrics" not in row:
                    lines.append(f"- {name}: NOT MEASURED")
                    continue
                gaps = ", ".join(
                    f"{key}={metric.get('difference_from_best_group', '—')}"
                    for key, metric in row["metrics"].items()
                )
                lines.append(f"- {name}: {gaps}")
            lines.append("")
    lines.extend([
        "## Governance threshold", "", f"**{result['governance_threshold']['status']}** — {result['governance_threshold']['reason']}", "",
        "## Limitations", "", *[f"- {item}" for item in result["limitations"]], "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RESULTS / "stage18-fairness.json")
    args = parser.parse_args()
    result = build_fairness_results()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(render_fairness_markdown(result), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
