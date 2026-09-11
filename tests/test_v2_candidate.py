"""Development-only regression coverage for the isolated Stage 20 candidate."""

import json

import numpy as np
import pytest

from src.classify import load_training_tickets
from src.generate import FAILURE_INSUFFICIENT_DOCUMENTATION, ResponseGenerationEngine
from src.generate import FAILURE_UNSUPPORTED_CITATION
from evaluation.v2_experiment import route_metrics, run_stage20
from src.route import TicketRoutingEngine
from src.retrieve import DocumentationRetrievalEngine
from src.v2.calibration import grouped_development_partitions
from src.v2.generate import TaskOrientedGroundedProviderV2
from src.v2.retrieve import ResolutionAwareRetrievalEngineV2


class KeywordEmbedder:
    terms = ("rollback", "pagination", "health", "login", "invoice", "deployment")

    def encode(self, texts, **_kwargs):
        values = []
        for text in texts:
            lowered = text.lower()
            row = [float(lowered.count(term)) for term in self.terms]
            if not any(row):
                row.append(1.0)
            else:
                row.append(0.0)
            values.append(row)
        return np.asarray(values, dtype=np.float32)


def _engine(tmp_path, content, doc_id="DOC-TEST-001"):
    corpus = tmp_path / "documentation.json"
    corpus.write_text(json.dumps([[{"doc_id": doc_id, "title": "Operator guide",
        "category": "operations", "content": content}]]), encoding="utf-8")
    base = DocumentationRetrievalEngine(embedding_model=KeywordEmbedder(), corpus_path=corpus,
                                        min_relevance_score=-1.0)
    return ResolutionAwareRetrievalEngineV2(base=base)


@pytest.mark.parametrize("query,intent,keyword", [
    ("How do I rollback a deployment?", "rollback_request", "rollback"),
    ("How do I get the next page with pagination?", "api_usage_question", "pagination"),
    ("The health check is unhealthy; how do I troubleshoot it?", "deployment_failure", "health"),
])
def test_action_questions_select_same_document_resolution(tmp_path, query, intent, keyword):
    engine = _engine(tmp_path, f"# Guide\n\n{keyword} symptoms.\n\n## Common causes\n\nA documented cause."
                               f"\n\n## Resolution\n\n1. Follow the documented {keyword} procedure.\n2. Verify the result.")
    result = engine.query_authoritative_knowledge(query, top_k=1, intent=intent)[0]
    assert result["section"] == "Resolution"
    assert result["selection_reason"] == "action_seeking_same_document_resolution"
    assert "Follow the documented" in result["passage"]


def test_non_action_question_preserves_semantic_section(tmp_path):
    engine = _engine(tmp_path, "# Login\n\nlogin symptoms and definition.\n\n## Resolution\n\nReset login state.")
    result = engine.query_authoritative_knowledge("What is a login state?", top_k=1,
                                                  intent="billing_query")[0]
    assert result["section"] == "Login"


def test_insufficient_documentation_fails_closed():
    provider = TaskOrientedGroundedProviderV2()
    output = provider.generate("protected", "unsupported", [], {})
    assert output == {"answer": None, "citations": [], "supported": False,
                      "uncertainty": FAILURE_INSUFFICIENT_DOCUMENTATION}


def test_high_risk_ticket_still_escalates():
    decision = TicketRoutingEngine(.40, .30).route(
        {"intent": "security_incident", "urgency": "high", "confidence": 1.0},
        [{"doc_id": "DOC-SEC-001", "relevance_score": 1.0}],
    )
    assert decision["action"] == "ESCALATE"
    assert decision["reason_code"] == "HIGH_RISK_INTENT"


def test_grouped_calibration_partitions_have_no_leakage_and_are_deterministic():
    tickets = load_training_tickets()
    first = grouped_development_partitions(tickets).manifest()
    second = grouped_development_partitions(tickets).manifest()
    assert first == second
    assert first["leakage_detected"] is False
    assert set(first["group_overlap"].values()) == {0}


def test_routing_is_deterministic():
    router = TicketRoutingEngine(.70, .40)
    classification = {"intent": "rollback_request", "urgency": "medium", "confidence": .91}
    evidence = [{"doc_id": "DOC-DEPLOY-001", "relevance_score": .63}]
    assert router.route(classification, evidence) == router.route(classification, evidence)


def test_v2_generation_uses_exact_retrieved_citation():
    evidence = [{"document_id": "DOC-API-001", "doc_id": "DOC-API-001",
        "chunk_id": "DOC-API-001-resolution", "passage": "Use the documented next-page cursor.",
        "chunk_content": "Use the documented next-page cursor.", "similarity_score": .91,
        "relevance_score": .91, "rank": 1, "title": "Pagination", "section": "Resolution",
        "source": "authoritative_documentation"}]
    result = ResponseGenerationEngine(provider=TaskOrientedGroundedProviderV2()).generate_response(
        {"ticket_id": "dev-fixture", "raw_content": "How do I paginate?"},
        {"intent": "api_usage_question", "urgency": "low", "confidence": .95}, evidence)
    assert result["supported"] is True
    assert result["citations"] == [{"document_id": "DOC-API-001",
                                     "chunk_id": "DOC-API-001-resolution"}]
    assert "Use the documented next-page cursor." in result["answer"]


def test_false_auto_response_never_counts_as_strictly_safe():
    tickets = [{"labels": {"expected_route": "escalate", "must_not_auto_respond": False,
                            "intent": "billing_query"}}]
    predictions = [{"intent": "billing_query", "urgency": "medium", "confidence": .99}]
    evidence = [[{"doc_id": "DOC-BILL-001", "relevance_score": .99}]]
    metrics = route_metrics(tickets, predictions, evidence, .8, .3)
    assert metrics["false_auto_responses"] == 1
    assert metrics["safety_constraints_satisfied"] is False


def test_stage20_rejects_validation_path_without_loading_it(tmp_path):
    protected = tmp_path / "validation_tickets.json"
    protected.write_text("this must not be parsed", encoding="utf-8")
    with pytest.raises(ValueError, match="development_tickets.json only"):
        run_stage20(protected)


def test_invented_v2_citation_is_rejected():
    class BadCitationProvider(TaskOrientedGroundedProviderV2):
        def generate(self, *args, **kwargs):
            output = super().generate(*args, **kwargs)
            output["citations"][0]["chunk_id"] = "invented"
            return output

    evidence = [{"document_id": "DOC-API-001", "chunk_id": "real",
        "passage": "Use the documented cursor.", "similarity_score": .9,
        "relevance_score": .9, "rank": 1, "title": "Pagination", "section": "Resolution"}]
    result = ResponseGenerationEngine(provider=BadCitationProvider()).generate_response(
        {"ticket_id": "dev", "raw_content": "How?"},
        {"intent": "api_usage_question", "urgency": "low", "confidence": .95}, evidence)
    assert result["supported"] is False
    assert result["failure_reason"] == FAILURE_UNSUPPORTED_CITATION
