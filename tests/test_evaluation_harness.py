import json

from evaluation.harness import run_evaluation
from src.logging_store import DecisionLogStore


class ReconciledPipeline:
    def __init__(self, db_url="sqlite:///:memory:"):
        self.logging_store = DecisionLogStore(db_url)

    def process_ticket(self, ticket, *, run_id=None):
        action = ticket.get("expected_action", "ESCALATE")
        decision_id = self.logging_store.log_decision({
            "ticket_id": ticket["ticket_id"], "run_id": run_id,
            "selected_action": action, "reason": "synthetic contract result",
            "reason_code": "TEST_TERMINAL", "response_released": action == "AUTO_RESPOND",
        })
        audit = self.logging_store.get_decision(decision_id)
        return {
            "ticket_id": ticket["ticket_id"], "status": action,
            "response_released": action == "AUTO_RESPOND",
            "decision_id": decision_id, "audit_record": audit,
            "decision_record": {"classification": {}, "retrieval": [], "guardrails": {}},
        }


def test_evaluation_run_id_and_decision_rows_reconcile(tmp_path):
    dataset = tmp_path / "arbitrary-name.json"
    dataset.write_text(json.dumps([
        {"ticket_id": "E-1", "expected_action": "AUTO_RESPOND", "labels": {}},
        {"ticket_id": "E-2", "expected_action": "ESCALATE", "labels": {}},
    ]), encoding="utf-8")
    pipeline = ReconciledPipeline()
    report = run_evaluation(str(dataset), dataset_role="development", orchestrator=pipeline)
    run_id = report["run"]["run_id"]
    assert report["reconciliation"] == {
        "source_ticket_count": 2, "evaluated_ticket_count": 2,
        "terminal_result_count": 2, "decision_log_count": 2,
        "decision_log_coverage": 1.0, "reconciled": True,
        "query_error_type": None, "status": "PASS",
    }
    assert {row["run_id"] for row in pipeline.logging_store.get_decisions_for_run(run_id)} == {run_id}


def test_default_evaluation_database_is_temporary_and_reconciled(tmp_path):
    dataset = tmp_path / "one-ticket.json"
    dataset.write_text(json.dumps([{"ticket_id": "E-3", "labels": {}}]), encoding="utf-8")
    report = run_evaluation(
        str(dataset), dataset_role="development", orchestrator_factory=ReconciledPipeline
    )
    assert report["reconciliation"]["reconciled"] is True
    assert report["reconciliation"]["decision_log_count"] == 1
