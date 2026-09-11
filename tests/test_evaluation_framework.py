import json

from evaluation.harness import run_evaluation
from evaluation.metrics import METRIC_REGISTRY, build_metric_assessments, calculate_retrieval_metrics, metric_status
from evaluation.report import build_markdown_report
from tests.test_evaluation_harness import ReconciledPipeline


def test_missing_metric_never_passes_and_failed_target_fails():
    assert metric_status(None, {"operator": "gte", "value": 0.85}) == "NOT MEASURED"
    assert metric_status(0.80, {"operator": "gte", "value": 0.85}, denominator=10) == "FAIL"
    assert metric_status(0.90, None, denominator=10) == "MEASURED — NO FORMAL TARGET"


def test_required_retrieval_cutoffs_and_mrr_are_reported():
    result = calculate_retrieval_metrics([["A", "B", "C"]], [["B"]])
    assert all(f"recall_at_{k}" in result and f"precision_at_{k}" in result for k in (1, 3, 5))
    assert result["mrr"]["value"] == 0.5
    assert result["mrr"]["denominator"] == 1


def test_human_and_business_metrics_are_not_fabricated(tmp_path):
    dataset = tmp_path / "development.json"
    dataset.write_text(json.dumps([{"ticket_id": "D-1", "labels": {}}]), encoding="utf-8")
    report = run_evaluation(str(dataset), dataset_role="development", orchestrator=ReconciledPipeline())
    assessments = report["metric_assessments"]
    for key in ("hallucination_rate", "semantic_citation_accuracy", "response_correctness", "response_usefulness",
                "first_contact_resolution", "first_response_time", "csat", "availability", "repeat_contact_rate"):
        assert assessments[key]["status"] == "NOT MEASURED"
        assert assessments[key]["value"] is None


def test_citation_id_validity_and_pipeline_latency_are_not_misnamed(tmp_path):
    dataset = tmp_path / "development.json"
    output = tmp_path / "results.json"
    dataset.write_text(json.dumps([{"ticket_id": "D-2", "labels": {}}]), encoding="utf-8")
    report = run_evaluation(str(dataset), str(output), dataset_role="development", orchestrator=ReconciledPipeline())
    markdown = output.with_suffix(".md").read_text(encoding="utf-8")
    assert "Citation ID validity" in markdown
    assert "not semantic citation accuracy" in markdown
    assert "Pipeline latency" in markdown
    assert "not time to first substantive customer response" in markdown
    assert report["metric_assessments"]["first_response_time"]["status"] == "NOT MEASURED"


def test_development_validation_and_final_evidence_classifications_are_explicit(tmp_path):
    dataset = tmp_path / "tickets.json"
    dataset.write_text(json.dumps([{"ticket_id": "E-1", "labels": {}}]), encoding="utf-8")
    classifications = []
    for role in ("development", "validation", "final"):
        result = run_evaluation(str(dataset), dataset_role=role, orchestrator=ReconciledPipeline())
        classifications.append(result["run"]["evidence_classification"])
    assert classifications == ["DEVELOPMENT", "VALIDATION", "FINAL"]


def test_unattended_run_writes_machine_and_markdown_reports(tmp_path):
    dataset = tmp_path / "development.json"
    output_dir = tmp_path / "unattended"
    dataset.write_text(json.dumps([{"ticket_id": "D-3", "labels": {}}]), encoding="utf-8")
    result = run_evaluation(str(dataset), str(output_dir), dataset_role="development", orchestrator=ReconciledPipeline())
    json_path = output_dir / "evaluation_results.json"
    markdown_path = output_dir / "evaluation_report.md"
    assert json_path.is_file() and markdown_path.is_file()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["metric_registry"] == METRIC_REGISTRY
    assert "## Reconciliation" in build_markdown_report(saved)
    assert result["reconciliation"]["status"] == "PASS"


def test_every_registry_record_has_required_fields_and_targets_only_when_documented():
    for item in METRIC_REGISTRY.values():
        assert {"name", "definition", "eligible_population", "measurement_type", "status_logic"} <= item.keys()
    assert "target" not in METRIC_REGISTRY["retrieval_mrr"]
    assert METRIC_REGISTRY["semantic_citation_accuracy"]["target"]["value"] == 0.95


def test_assessment_statuses_are_closed_vocabulary():
    assessments = build_metric_assessments({})
    assert {item["status"] for item in assessments.values()} == {"NOT MEASURED"}
