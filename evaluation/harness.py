"""Production-path evaluation harness for CloudServe Support Automation.

The harness calls ``SupportPipelineOrchestrator.process_ticket`` exactly once
per input ticket and derives evaluation evidence from that public result.

>>> _extract_tickets([[{'ticket_id': 'T-1'}]])[0]['ticket_id']
'T-1'
>>> _extract_tickets({'tickets': [{'ticket_id': 'T-2'}]})[0]['ticket_id']
'T-2'
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional

from evaluation.metrics import METRIC_REGISTRY, aggregate_metrics, build_metric_assessments
from evaluation.report import build_markdown_report
from src.config import settings
from src.pipeline import SupportPipelineOrchestrator

EVALUATION_SCHEMA_VERSION = "3.0"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_RESULTS_ROOT = PROJECT_ROOT / "evaluation" / "results"

EVIDENCE_CLASSIFICATIONS = {
    "development": "DEVELOPMENT",
    "validation": "VALIDATION",
    "hidden": "FINAL",
    "final": "FINAL",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_tickets(raw_data: Any) -> List[Any]:
    if isinstance(raw_data, Mapping):
        raw_data = raw_data.get("tickets")
    if isinstance(raw_data, list) and len(raw_data) == 1 and isinstance(raw_data[0], list):
        raw_data = raw_data[0]
    if not isinstance(raw_data, list):
        raise ValueError("Dataset must be a JSON list, a single wrapped list, or an object with a 'tickets' list")
    # Individual invalid items belong to the production ingestion boundary.
    return raw_data


def _load_dataset(dataset_path: str) -> tuple[List[Dict[str, Any]], str]:
    path = Path(dataset_path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
    content = path.read_bytes()
    try:
        raw_data = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Dataset is not valid UTF-8 JSON: {dataset_path}") from exc
    return _extract_tickets(raw_data), hashlib.sha256(content).hexdigest()


def _fingerprint_file(path: Path | str) -> str:
    """Return a content fingerprint without interpreting file contents."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _doc_ids(retrieval: Any) -> List[str]:
    if not isinstance(retrieval, list):
        return []
    return [str(item.get("document_id") or item.get("doc_id")) for item in retrieval
            if isinstance(item, Mapping) and (item.get("document_id") or item.get("doc_id"))]


def _record_result(ticket: Mapping[str, Any], result: Mapping[str, Any], latency_seconds: float) -> Dict[str, Any]:
    ticket = ticket if isinstance(ticket, Mapping) else {}
    decision = result.get("decision_record")
    if not isinstance(decision, Mapping):
        decision = {}
    classification = result.get("classification")
    if not isinstance(classification, Mapping):
        classification = decision.get("classification")
    if not isinstance(classification, Mapping):
        classification = {}
    retrieval = decision.get("retrieval")
    response = result.get("response")
    if not isinstance(response, Mapping):
        response = decision.get("generation")
    if not isinstance(response, Mapping):
        response = {}
    guardrails = result.get("guardrails")
    if not isinstance(guardrails, Mapping):
        guardrails = decision.get("guardrails")
    if not isinstance(guardrails, Mapping):
        guardrails = {}
    labels = ticket.get("labels") if isinstance(ticket.get("labels"), Mapping) else {}
    return {
        "ticket_id": str(result.get("ticket_id", ticket.get("ticket_id", "UNKNOWN"))),
        "classification": dict(classification),
        "retrieved_doc_ids": _doc_ids(retrieval),
        "predicted_route": result.get("status") or result.get("action"),
        "expected_route": labels.get("expected_route"),
        "expected_doc_ids": labels.get("expected_doc_ids"),
        "citations": [
            citation.get("document_id")
            if isinstance(citation, dict)
            else citation
            for citation in (response.get("citations") or [])
        ],
        "guardrails": dict(guardrails),
        "decision_id": result.get("decision_id"),
        "audit_record_present": isinstance(result.get("audit_record"), Mapping),
        "latency_seconds": round(latency_seconds, 9),
        "reason_code": result.get("reason_code"),
        "routing_reason_code": (result.get("routing") or {}).get("reason_code"),
        "original_route": (result.get("routing") or {}).get("action"),
        "response_released": result.get("response_released", False),
        "failure_state": result.get("failure_state"),
        "processing_error": (
            {"type": result.get("error_type"), "category": result.get("error_category") or result.get("failure_state")}
            if result.get("failure_state") or result.get("error_category") else None
        ),
    }


def _error_record(ticket: Mapping[str, Any], exc: Exception, latency_seconds: float) -> Dict[str, Any]:
    ticket = ticket if isinstance(ticket, Mapping) else {}
    labels = ticket.get("labels") if isinstance(ticket.get("labels"), Mapping) else {}
    return {
        "ticket_id": str(ticket.get("ticket_id", "UNKNOWN")),
        "classification": {}, "retrieved_doc_ids": [], "predicted_route": "ESCALATE",
        "expected_route": labels.get("expected_route"), "expected_doc_ids": labels.get("expected_doc_ids"),
        "citations": [], "guardrails": {}, "decision_id": None, "audit_record_present": False,
        "latency_seconds": round(latency_seconds, 9),
        "reason_code": "PIPELINE_INTERNAL_ERROR", "routing_reason_code": None,
        "original_route": None, "response_released": False,
        "failure_state": "PIPELINE_INTERNAL_ERROR",
        "processing_error": {"type": type(exc).__name__, "category": "PIPELINE_INTERNAL_ERROR"},
    }


def _atomic_write(path: Path, value: Mapping[str, Any]) -> None:
    """An interruption leaves either the previous complete checkpoint or the next."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=True, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        # Windows readers/virus scanners can briefly deny replacement. Retry only
        # this atomic operation; never rerun a ticket or duplicate its audit event.
        for attempt in range(4):
            try:
                os.replace(temporary, path)
                break
            except PermissionError:
                if attempt == 3:
                    raise
                time.sleep(0.05 * (2 ** attempt))
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _output_paths(output_path: Optional[str]) -> tuple[Optional[Path], Optional[Path]]:
    if output_path is None:
        return None, None
    requested = Path(output_path).resolve()
    if requested.is_dir() or requested.suffix.lower() != ".json":
        return requested / "evaluation_results.json", requested / "evaluation_report.md"
    return requested, requested.with_suffix(".md")


def preflight_evaluation(dataset_path: str, output_path: str, *, dataset_role: str) -> Dict[str, Any]:
    """Validate a future run without reading or deserializing its dataset."""

    if dataset_role not in EVIDENCE_CLASSIFICATIONS:
        raise ValueError("dataset_role must be development, validation, final, or hidden")
    dataset = Path(dataset_path).resolve()
    if not dataset.is_file():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
    output, markdown_output = _output_paths(output_path)
    if output is None:
        raise ValueError("An output path is required for validation preflight")
    if output == dataset:
        raise ValueError("Output must not overwrite input data")
    if dataset_role in {"validation", "final", "hidden"}:
        try:
            output.relative_to(EVALUATION_RESULTS_ROOT.resolve())
        except ValueError as exc:
            raise ValueError("Validation/final output must remain under evaluation/results") from exc

    required = {
        "dataset": dataset,
        "documentation_corpus": PROJECT_ROOT / "data" / "raw" / "documentation.json",
        "generation_prompt": PROJECT_ROOT / "prompts" / "build" / "generation_v1.txt",
        "stage11_evidence": EVALUATION_RESULTS_ROOT / "stage11-calibration.json",
    }
    checks = {name: path.is_file() for name, path in required.items()}
    if not all(checks.values()):
        missing = ", ".join(name for name, present in checks.items() if not present)
        raise FileNotFoundError(f"Required validation inputs are missing: {missing}")

    offline = settings.GENERATION_PROVIDER == "offline"
    return {
        "status": "READY" if offline else "LIVE_PROVIDER_CREDENTIAL_REQUIRED",
        "dataset_role": dataset_role,
        "evidence_classification": EVIDENCE_CLASSIFICATIONS[dataset_role],
        "dataset_path": str(dataset),
        "dataset_content_read": False,
        "dataset_fingerprint": "DEFERRED_UNTIL_AUTHORIZED_EXECUTION",
        "dataset_ticket_count": "NOT_LOADED",
        "dataset_size_assumption": None,
        "output_path": str(output),
        "markdown_output_path": str(markdown_output),
        "output_isolated": True,
        "decision_log_policy": "run-specific SQLite file beside output; run UUID assigned at execution",
        "partial_run_policy": "atomic checkpoint marked RUNNING/partial_run; no automatic resume",
        "generation_provider": settings.GENERATION_PROVIDER,
        "live_credential_required": not offline,
        "required_files": checks,
    }


def _reconcile(pipeline: Any, run_id: str, records: List[Dict[str, Any]],
               source_count: int) -> Dict[str, Any]:
    terminal_count = sum(row["predicted_route"] in ("AUTO_RESPOND", "ESCALATE") for row in records)
    count = None
    indexed = {}
    verified = False
    error = None
    try:
        store = pipeline.logging_store
        rows = store.get_decisions_for_run(run_id)
        count = len(rows)
        indexed = {row["decision_id"]: row for row in rows}
        verified = len(indexed) == count and all(
            row.get("decision_id") in indexed
            and indexed[row["decision_id"]]["terminal_action"] == row["predicted_route"]
            and indexed[row["decision_id"]]["ticket_id"] == row["ticket_id"]
            and indexed[row["decision_id"]]["response_released"] == row["response_released"]
            for row in records
        )
    except Exception as exc:
        error = type(exc).__name__
    return {
        "source_ticket_count": source_count, "evaluated_ticket_count": len(records),
        "terminal_result_count": terminal_count, "decision_log_count": count,
        "decision_log_coverage": (
            sum(row.get("decision_id") in indexed for row in records) / len(records)
            if count is not None and records else None
        ),
        "reconciled": verified and len(records) == terminal_count == count,
        "query_error_type": error,
    }


def run_evaluation(
    dataset_path: str,
    output_path: Optional[str] = None,
    *,
    limit: Optional[int] = None,
    dataset_role: str = "development",
    retrieval_k: int = 3,
    intent_label_map: Optional[Mapping[str, str]] = None,
    orchestrator: Optional[Any] = None,
    orchestrator_factory: Callable[..., Any] = SupportPipelineOrchestrator,
) -> Dict[str, Any]:
    """Evaluate arbitrary JSON ticket data through the production entry point.

    ``limit`` is intended for development smoke runs. Omit it for a complete
    dataset run; no dataset size or filename is assumed.
    """
    if limit is not None and limit <= 0:
        raise ValueError("limit must be a positive integer when provided")
    if retrieval_k <= 0:
        raise ValueError("retrieval_k must be positive")
    if dataset_role not in EVIDENCE_CLASSIFICATIONS:
        raise ValueError("dataset_role must be development, validation, final, or hidden")
    all_tickets, dataset_sha256 = _load_dataset(dataset_path)
    tickets = all_tickets[:limit] if limit is not None else all_tickets
    run_id = str(uuid.uuid4())
    started_at = _utc_now()
    output, markdown_output = _output_paths(output_path)
    if output is not None and output == Path(dataset_path).resolve():
        raise ValueError("Output must not overwrite input data")
    temporary_database = None
    pipeline = orchestrator
    records: List[Dict[str, Any]] = []
    run_start = time.perf_counter()
    database_path = None
    run = {
        "run_id": run_id, "started_at_utc": started_at, "finished_at_utc": None,
        "status": "RUNNING", "evidence_status": "partial_run",
        "dataset_role": str(dataset_role), "dataset_path": str(Path(dataset_path)),
        "evidence_classification": EVIDENCE_CLASSIFICATIONS[dataset_role],
        "dataset_sha256": dataset_sha256, "source_ticket_count": len(all_tickets),
        "evaluated_ticket_count": 0, "partial_dataset": len(tickets) < len(all_tickets),
        "production_entry_point": "src.pipeline.SupportPipelineOrchestrator.process_ticket",
    }
    try:
        if pipeline is None:
            if output is None:
                temporary_database = tempfile.TemporaryDirectory(prefix="cloudserve-eval-")
                database_path = Path(temporary_database.name) / "decisions.db"
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                database_path = output.with_name(f"{output.stem}.{run_id}.decisions.sqlite")
            pipeline = orchestrator_factory(db_url=f"sqlite:///{database_path.as_posix()}")
        if not callable(getattr(pipeline, "process_ticket", None)):
            raise TypeError("Production orchestrator must expose process_ticket")
        run["decision_database"] = str(database_path) if database_path and output else None
        if output:
            _atomic_write(output, {"schema_version": EVALUATION_SCHEMA_VERSION, "run": run, "records": records})
        for index, ticket in enumerate(tickets):
            ticket_start = time.perf_counter()
            try:
                result = pipeline.process_ticket(ticket, run_id=run_id)
                if not isinstance(result, Mapping) or result.get("status") not in ("AUTO_RESPOND", "ESCALATE"):
                    raise TypeError("Invalid production terminal result")
                record = _record_result(ticket, result, time.perf_counter() - ticket_start)
            except Exception as exc:
                record = _error_record(ticket, exc, time.perf_counter() - ticket_start)
            record.update({"run_id": run_id, "input_index": index})
            records.append(record)
            run["evaluated_ticket_count"] = len(records)
            if output:
                _atomic_write(output, {"schema_version": EVALUATION_SCHEMA_VERSION, "run": run, "records": records})
        reconciliation = _reconcile(pipeline, run_id, records, len(all_tickets))
        reconciliation["status"] = (
            "NOT APPLICABLE" if not records else "PASS" if reconciliation["reconciled"] else "FAIL"
        )
        run.update({
            "status": "COMPLETED", "finished_at_utc": _utc_now(),
            "evidence_status": "development_smoke" if run["partial_dataset"] else "current_run",
            "elapsed_seconds": round(time.perf_counter() - run_start, 6),
        })
        # Invalid entries have no eligible labels, but still count as processing events.
        metric_tickets = [
            {**ticket, "labels": ticket.get("labels") if isinstance(ticket.get("labels"), Mapping) else {}}
            if isinstance(ticket, Mapping) else {} for ticket in tickets
        ]
        metrics = aggregate_metrics(records, metric_tickets, intent_label_map=intent_label_map, retrieval_k=retrieval_k)
        report = {
            "schema_version": EVALUATION_SCHEMA_VERSION, "run": run,
            "reconciliation": reconciliation,
            "label_schema": {
                "intent_mapping": dict(intent_label_map or {}),
                "intent_mapping_policy": "explicit_only; identity comparison when absent",
                "route_mapping": {"BLOCK": "ESCALATE"},
            },
            "metric_registry": METRIC_REGISTRY,
            "metrics": metrics,
            "metric_assessments": build_metric_assessments(metrics),
            "human_review_template": "evaluation/human_review_template.json",
            "limitations": [
                "Automated citation ID validity does not establish semantic citation accuracy.",
                "Local pipeline latency does not measure customer first-response time or service availability.",
                "Human-review metrics are blank until real independent assessments are supplied.",
                "Business outcomes are not inferred from historical dataset fields or routing outcomes.",
                "Development evidence must not be presented as validation or final evidence.",
            ],
            "records": records,
        }
        if output:
            _atomic_write(output, report)
            _atomic_write_text(markdown_output, build_markdown_report(report))
            report["artifacts"] = {"machine_readable": str(output), "markdown": str(markdown_output)}
            _atomic_write(output, report)
        return report
    except BaseException as exc:
        run.update({"status": "INTERRUPTED" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "FAILED",
                    "evidence_status": "partial_run", "error_type": type(exc).__name__})
        if output:
            try:
                _atomic_write(output, {"schema_version": EVALUATION_SCHEMA_VERSION, "run": run, "records": records})
            except OSError:
                pass
        raise
    finally:
        if orchestrator is None and pipeline is not None:
            engine = getattr(getattr(pipeline, "logging_store", None), "engine", None)
            if engine is not None:
                engine.dispose()
        if temporary_database is not None:
            temporary_database.cleanup()


def _load_mapping(path: Optional[str]) -> Optional[Dict[str, str]]:
    if not path:
        return None
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
        raise ValueError("Intent mapping must be a JSON object of string-to-string entries")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the production support orchestrator")
    parser.add_argument("--dataset", "--input", dest="dataset", required=True, help="Input ticket dataset JSON")
    parser.add_argument("--output", help="Optional machine-readable JSON output path")
    parser.add_argument("--limit", type=int, help="Development smoke limit; omit for a complete run")
    parser.add_argument("--dataset-role", default="development", choices=("development", "validation", "final", "hidden"), help="Explicit evidence role; hidden and final are classified as FINAL")
    parser.add_argument("--retrieval-k", type=int, default=3)
    parser.add_argument("--intent-label-map", help="Optional explicit dataset-to-production label map JSON")
    parser.add_argument("--preflight", action="store_true", help="Check readiness without reading the dataset")
    args = parser.parse_args()
    try:
        if args.preflight:
            result = preflight_evaluation(args.dataset, args.output, dataset_role=args.dataset_role)
            print(json.dumps(result, indent=2))
            return
        result = run_evaluation(args.dataset, args.output, limit=args.limit, dataset_role=args.dataset_role, retrieval_k=args.retrieval_k, intent_label_map=_load_mapping(args.intent_label_map))
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__}), file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps({"run": result["run"], "reconciliation": result["reconciliation"],
                      "operational": result["metrics"]["operational"]}, indent=2))


if __name__ == "__main__":
    main()
