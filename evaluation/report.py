"""Registry-driven machine and Markdown evaluation reporting."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Optional

from evaluation.metrics import ALLOWED_STATUSES, METRIC_REGISTRY, build_metric_assessments, metric_status

CURRENT_SCHEMA_VERSION = "3.0"
EVIDENCE_CLASSES = {"DEVELOPMENT", "VALIDATION", "FINAL"}


def target_status(value: Optional[float], target: Optional[float], operator: Optional[str], *,
                  applicable: bool = True, denominator: Optional[int] = None) -> str:
    spec = None if target is None or operator is None else {"value": target, "operator": operator}
    return metric_status(value, spec, applicable=applicable, denominator=denominator)


def _validate_current_evidence(data: Mapping[str, Any]) -> None:
    if data.get("schema_version") != CURRENT_SCHEMA_VERSION:
        raise ValueError("Result is legacy or has an unsupported schema; it is not valid Stage 10 evidence")
    run = data.get("run")
    if not isinstance(run, Mapping):
        raise ValueError("Result has no run metadata")
    missing = [key for key in ("run_id", "started_at_utc", "dataset_sha256", "evidence_classification") if not run.get(key)]
    if missing:
        raise ValueError(f"Result lacks evidence fields: {', '.join(missing)}")
    if run.get("evidence_classification") not in EVIDENCE_CLASSES:
        raise ValueError("Evidence classification must be DEVELOPMENT, VALIDATION, or FINAL")


def _display(key: str, value: Any) -> str:
    if value is None:
        return "-"
    if key in {"pipeline_latency_p50", "pipeline_latency_p95", "first_response_time"}:
        return f"{float(value):.4f}s"
    if key == "csat":
        return f"{float(value):.2f}/5"
    if key == "private_data_occurrences":
        return str(value)
    return f"{float(value) * 100:.1f}%"


def build_markdown_report(data: Mapping[str, Any]) -> str:
    _validate_current_evidence(data)
    run = data["run"]
    assessments = data.get("metric_assessments") or build_metric_assessments(data.get("metrics", {}))
    rows = []
    for key, registry in METRIC_REGISTRY.items():
        measured = assessments.get(key, {})
        status = measured.get("status", "NOT MEASURED")
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid metric status for {key}: {status}")
        target = registry.get("target", {}).get("display", "No formal target")
        basis = measured.get("reason") or f"{measured.get('denominator', 0)} eligible / {measured.get('excluded', 0)} excluded"
        rows.append(f"| {registry['name']} | {registry['measurement_type']} | {_display(key, measured.get('value'))} | {target} | {status} | {basis} |")
    reconciliation = data.get("reconciliation", {})
    limitations = data.get("limitations") or []
    limitation_text = "\n".join(f"- {item}" for item in limitations) or "- No limitations were recorded."
    partial = " This is a partial development smoke run." if run.get("partial_dataset") else ""
    return f"""# CloudServe Evaluation Report

## Evidence classification

- Classification: **{run.get('evidence_classification')}**
- Dataset role: `{run.get('dataset_role')}`
- Run ID: `{run.get('run_id')}`
- Dataset SHA-256: `{run.get('dataset_sha256')}`
- Evaluated tickets: `{run.get('evaluated_ticket_count')}` of `{run.get('source_ticket_count')}`
- Started UTC: `{run.get('started_at_utc')}`
- Production entry point: `{run.get('production_entry_point')}`

This report contains {run.get('evidence_classification')} evidence only.{partial}

## Reconciliation

- Status: **{reconciliation.get('status', 'NOT MEASURED')}**
- Source / evaluated / terminal / logged: {reconciliation.get('source_ticket_count')} / {reconciliation.get('evaluated_ticket_count')} / {reconciliation.get('terminal_result_count')} / {reconciliation.get('decision_log_count')}
- Reconciled: `{reconciliation.get('reconciled')}`

## Metric registry results

| Metric | Type | Measured | Documented target | Status | Denominator or limitation |
| :--- | :--- | :--- | :--- | :--- | :--- |
{chr(10).join(rows)}

Only these statuses are permitted: **PASS**, **FAIL**, **NOT MEASURED**, **NOT APPLICABLE**, and **MEASURED — NO FORMAL TARGET**. Missing values never pass.

## Important measurement boundaries

- Citation ID validity checks only whether emitted IDs resolve to retrieved documents. It is not semantic citation accuracy.
- Pipeline latency measures local processing duration. It is not time to first substantive customer response.
- Hallucination, semantic citation accuracy, response correctness, and usefulness remain unmeasured until real human reviews complete the blank template.
- FCR, CSAT, availability, first-response time, and repeat-contact rate are not inferred from pipeline outcomes or historical dataset fields.

## Limitations

{limitation_text}
"""


def generate_markdown_report(json_path: str, markdown_output_path: str) -> str:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    report = build_markdown_report(data)
    output = Path(markdown_output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a registry-driven evaluation report")
    parser.add_argument("results_json")
    parser.add_argument("markdown_output")
    args = parser.parse_args()
    generate_markdown_report(args.results_json, args.markdown_output)


if __name__ == "__main__":
    main()
