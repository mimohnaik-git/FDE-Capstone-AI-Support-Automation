"""Stage 18 fairness and human-review readiness tests."""

import json
from pathlib import Path

import pytest

from evaluation.fairness import MIN_GROUP_SIZE, evaluate_dimension, segment_indices
from evaluation.human_review import aggregate_reviews, blank_reviewer_form
from evaluation.restore_human_reviews import parse_review_transcript
from src.config import settings


def _ticket(tier="standard", fluency="fluent", words=5):
    return {
        "customer_tier": tier, "language_fluency": fluency, "body": "word " * words,
        "labels": {"intent": "x", "urgency": "low", "expected_route": "ESCALATE", "expected_doc_ids": ["D1"]},
    }


def _record(correct=True):
    return {
        "classification": {"intent": "x" if correct else "y", "urgency": "low", "confidence": .9},
        "retrieved_doc_ids": ["D1"], "predicted_route": "ESCALATE", "original_route": "ESCALATE",
        "guardrails": {}, "decision_id": "D", "audit_record_present": True, "latency_seconds": .1,
    }


def test_group_segmentation_uses_explicit_tier_and_fluency_only():
    tickets = [_ticket("enterprise", "non_fluent"), _ticket("standard", "fluent")]
    tiers, tier_policy = segment_indices(tickets, "customer_tier")
    fluency, fluency_policy = segment_indices(tickets, "language_fluency")
    assert tiers == {"enterprise": [0], "other_tiers": [1]}
    assert fluency == {"fluent": [1], "non_fluent": [0]}
    assert tier_policy["inference"] is False and fluency_policy["inference"] is False


def test_missing_explicit_group_attribute_is_not_inferred_from_text():
    tickets = [{"body": "I am an enterprise customer and my English is fluent."}]
    assert segment_indices(tickets, "customer_tier")[0] == {"enterprise": [], "other_tiers": []}
    assert segment_indices(tickets, "language_fluency")[0] == {"fluent": [], "non_fluent": []}


def test_length_segmentation_is_deterministic_and_not_called_complexity():
    groups, policy = segment_indices([_ticket(words=2), _ticket(words=10)], "text_length")
    assert groups == {"short": [0], "long": [1]}
    assert "not a complexity label" in policy["limitation"]


def test_group_metric_calculation_and_difference_from_best():
    tickets = [_ticket("enterprise") for _ in range(MIN_GROUP_SIZE)] + [_ticket("standard") for _ in range(MIN_GROUP_SIZE)]
    records = [_record(True) for _ in range(MIN_GROUP_SIZE)] + [_record(False) for _ in range(MIN_GROUP_SIZE)]
    result = evaluate_dimension(tickets, records, "customer_tier")
    enterprise = result["groups"]["enterprise"]
    other = result["groups"]["other_tiers"]
    assert enterprise["metrics"]["intent_accuracy"]["value"] == 1.0
    assert other["metrics"]["intent_accuracy"]["value"] == 0.0
    assert enterprise["metrics"]["intent_accuracy"]["difference_from_best_group"] == 0.0
    assert other["metrics"]["intent_accuracy"]["difference_from_best_group"] == 1.0


def test_insufficient_group_is_not_measured():
    result = evaluate_dimension([_ticket("enterprise")], [_record()], "customer_tier")
    assert result["groups"]["enterprise"]["status"] == "NOT MEASURED"
    assert "metrics" not in result["groups"]["enterprise"]


def test_human_review_template_stays_blank():
    form = blank_reviewer_form([f"S-{i}" for i in range(50)])
    assert form["reviewer_id"] is None
    assert form["independent_review_confirmed"] is None
    assert all(all(row[field] is None for field in (
        "unsupported_claim_present", "citation_supports_claim",
        "response_correctness_score", "response_usefulness_score",
    )) for row in form["reviews"])
    with pytest.raises(ValueError, match="reviewer IDs"):
        aggregate_reviews(form, form)


def test_completed_human_reviews_report_targets_agreement_and_ordinal_statistics():
    ids = [f"HDE-{i:03d}" for i in range(1, 51)]
    forms = [blank_reviewer_form(ids), blank_reviewer_form(ids)]
    for number, form in enumerate(forms, 1):
        form["reviewer_id"] = f"reviewer-{number}"
        form["independent_review_confirmed"] = True
        for index, row in enumerate(form["reviews"]):
            row.update({
                "unsupported_claim_present": index == 0,
                "citation_supports_claim": index != 0,
                "response_correctness_score": 4 if number == 1 or index % 2 else 5,
                "response_usefulness_score": 3 if number == 1 or index % 2 else 4,
            })
    result = aggregate_reviews(*forms)
    assert result["metrics"]["hallucination_rate"] == {"value": .02, "numerator": 1, "denominator": 50, "status": "PASS"}
    assert result["metrics"]["semantic_citation_accuracy"]["status"] == "PASS"
    assert result["metrics"]["response_correctness"]["status"] == "MEASURED — NO FORMAL TARGET"
    assert result["reviewer_agreement"]["unsupported_claim"]["value"] == 1.0
    assert result["reviewer_agreement"]["correctness_quadratic_weighted_kappa"] is not None
    assert result["disagreements"]["adjudicated"] is False


def test_reviewer_transcript_parser_preserves_judgments():
    blocks = []
    for reviewer in (1, 2):
        blocks.append(f"# REVIEWER {reviewer}")
        blocks.extend(
            f"HDE-{i:03d} | {'A=' if i == 1 else ''}{'Yes' if i == 1 else 'No'} | "
            f"{'B=' if i == 1 else ''}{'No' if i == 1 else 'Yes'} | "
            f"{'C=' if i == 1 else ''}4 | {'D=' if i == 1 else ''}3 | reviewer {reviewer} note {i}"
            for i in range(1, 51)
        )
    parsed = parse_review_transcript("\n".join(blocks))
    assert parsed["reviewer-1"]["reviews"][0]["unsupported_claim_present"] is True
    assert parsed["reviewer-2"]["reviews"][1]["citation_supports_claim"] is True
    assert parsed["reviewer-1"]["reviews"][49]["reviewer_notes"] == "reviewer 1 note 50"


def test_frozen_thresholds_and_manifest_remain_unchanged():
    manifest = json.loads(Path("evaluation/results/stage15-rerun-freeze-manifest.json").read_text())
    frozen = manifest["frozen_system_comparison"]
    assert settings.CLASSIFICATION_CONFIDENCE_THRESHOLD == frozen["classification_threshold"] == 0.80
    assert settings.RETRIEVAL_ROUTING_THRESHOLD == frozen["retrieval_threshold"] == 0.30
    assert frozen["production_fingerprints_changed"] is False
