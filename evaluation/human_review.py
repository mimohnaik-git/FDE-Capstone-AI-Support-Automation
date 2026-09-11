"""Prepare and aggregate genuine two-reviewer human development evaluation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from src.classify import TicketClassificationEngine
from src.generate import ResponseGenerationEngine
from src.guardrails import GuardrailEngine
from src.ingest import TicketNormalizationEngine
from src.retrieve import DocumentationRetrievalEngine


REVIEW_FIELDS = (
    "unsupported_claim_present", "citation_supports_claim",
    "response_correctness_score", "response_usefulness_score",
)


def blank_reviewer_form(sample_ids: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "1.0", "evidence_classification": "HUMAN DEVELOPMENT EVALUATION",
        "reviewer_id": None, "independent_review_confirmed": None,
        "reviews": [{"sample_id": sample_id, **{field: None for field in REVIEW_FIELDS}, "reviewer_notes": None}
                    for sample_id in sample_ids],
    }


def aggregate_reviews(first: Mapping[str, Any], second: Mapping[str, Any]) -> dict[str, Any]:
    """Aggregate completed independent forms; reject blanks or inadequate samples."""
    reviewer_ids = [first.get("reviewer_id"), second.get("reviewer_id")]
    if not all(isinstance(value, str) and value.strip() for value in reviewer_ids) or reviewer_ids[0] == reviewer_ids[1]:
        raise ValueError("Two distinct reviewer IDs are required")
    if first.get("independent_review_confirmed") is not True or second.get("independent_review_confirmed") is not True:
        raise ValueError("Both reviewers must confirm independent review")
    rows = []
    maps = [{row.get("sample_id"): row for row in form.get("reviews", [])} for form in (first, second)]
    shared = sorted(set(maps[0]) & set(maps[1]))
    if len(shared) < 50:
        raise ValueError("At least 50 responses must be reviewed by both assessors")
    for sample_id in shared:
        pair = [maps[0][sample_id], maps[1][sample_id]]
        if any(any(row.get(field) is None for field in REVIEW_FIELDS) for row in pair):
            raise ValueError("Blank ratings cannot be aggregated")
        for row in pair:
            if not isinstance(row["unsupported_claim_present"], bool):
                raise ValueError("unsupported_claim_present must be boolean")
            if row["citation_supports_claim"] not in (True, False, "not_applicable"):
                raise ValueError("citation_supports_claim has an invalid value")
            for field in ("response_correctness_score", "response_usefulness_score"):
                if isinstance(row[field], bool) or not isinstance(row[field], int) or not 1 <= row[field] <= 5:
                    raise ValueError(f"{field} must be an integer from 1 to 5")
        rows.append(pair)
    unsupported_agreements = sum(a["unsupported_claim_present"] == b["unsupported_claim_present"] for a, b in rows)
    citation_agreements = sum(a["citation_supports_claim"] == b["citation_supports_claim"] for a, b in rows)
    hallucinated = sum(a["unsupported_claim_present"] or b["unsupported_claim_present"] for a, b in rows)
    citation_pairs = [(a, b) for a, b in rows if a["citation_supports_claim"] != "not_applicable" and b["citation_supports_claim"] != "not_applicable"]
    citation_supported = sum(a["citation_supports_claim"] is True and b["citation_supports_claim"] is True for a, b in citation_pairs)
    mean = lambda field: sum(float(row[field]) for pair in rows for row in pair) / (2 * len(rows))
    individual = {}
    for reviewer_id, index in zip(reviewer_ids, (0, 1)):
        reviewer_rows = [pair[index] for pair in rows]
        citation_rows = [row for row in reviewer_rows if row["citation_supports_claim"] != "not_applicable"]
        individual[reviewer_id] = {
            "reviewed_responses": len(reviewer_rows),
            "unsupported_claim_rate": sum(row["unsupported_claim_present"] for row in reviewer_rows) / len(reviewer_rows),
            "unsupported_claim_numerator": sum(row["unsupported_claim_present"] for row in reviewer_rows),
            "citation_support_accuracy": sum(row["citation_supports_claim"] is True for row in citation_rows) / len(citation_rows) if citation_rows else None,
            "citation_support_denominator": len(citation_rows),
            "correctness_mean": sum(row["response_correctness_score"] for row in reviewer_rows) / len(reviewer_rows),
            "usefulness_mean": sum(row["response_usefulness_score"] for row in reviewer_rows) / len(reviewer_rows),
        }
    disagreements = {
        field: [pair[0]["sample_id"] for pair in rows if pair[0][field] != pair[1][field]]
        for field in REVIEW_FIELDS
    }
    all_disagreements = sorted(set().union(*map(set, disagreements.values())))
    hallucination_rate = hallucinated / len(rows)
    citation_accuracy = citation_supported / len(citation_pairs) if citation_pairs else None
    return {
        "evidence_classification": "HUMAN DEVELOPMENT EVALUATION", "reviewed_responses": len(rows),
        "metrics": {
            "hallucination_rate": {"value": hallucination_rate, "numerator": hallucinated, "denominator": len(rows), "status": "PASS" if hallucination_rate <= .05 else "FAIL"},
            "semantic_citation_accuracy": {"value": citation_accuracy, "numerator": citation_supported, "denominator": len(citation_pairs), "status": "PASS" if citation_accuracy is not None and citation_accuracy >= .95 else ("FAIL" if citation_accuracy is not None else "NOT MEASURED")},
            "response_correctness": {"value": mean("response_correctness_score"), "denominator": 2 * len(rows), "status": "MEASURED — NO FORMAL TARGET"},
            "response_usefulness": {"value": mean("response_usefulness_score"), "denominator": 2 * len(rows), "status": "MEASURED — NO FORMAL TARGET"},
        },
        "reviewer_agreement": {
            "unsupported_claim": {"value": unsupported_agreements / len(rows), "agreements": unsupported_agreements, "denominator": len(rows)},
            "citation_support": {"value": citation_agreements / len(rows), "agreements": citation_agreements, "denominator": len(rows)},
            "correctness_quadratic_weighted_kappa": _quadratic_weighted_kappa([a["response_correctness_score"] for a, _ in rows], [b["response_correctness_score"] for _, b in rows]),
            "usefulness_quadratic_weighted_kappa": _quadratic_weighted_kappa([a["response_usefulness_score"] for a, _ in rows], [b["response_usefulness_score"] for _, b in rows]),
        },
        "individual_reviewers": individual,
        "disagreements": {"by_field": disagreements, "sample_ids": all_disagreements, "count": len(all_disagreements), "adjudicated": False},
    }


def _quadratic_weighted_kappa(first: list[int], second: list[int]) -> float | None:
    """Cohen's quadratic weighted kappa for ordinal 1–5 ratings."""
    if len(first) != len(second) or not first:
        return None
    size = 5
    observed = [[0 for _ in range(size)] for _ in range(size)]
    first_counts, second_counts = [0] * size, [0] * size
    for a, b in zip(first, second):
        observed[a - 1][b - 1] += 1
        first_counts[a - 1] += 1
        second_counts[b - 1] += 1
    total = len(first)
    observed_weight = sum(((i - j) ** 2 / 16) * observed[i][j] for i in range(size) for j in range(size)) / total
    expected_weight = sum(((i - j) ** 2 / 16) * first_counts[i] * second_counts[j] / total for i in range(size) for j in range(size)) / total
    return None if expected_weight == 0 else round(1 - observed_weight / expected_weight, 6)


def render_aggregate_markdown(result: Mapping[str, Any]) -> str:
    metrics, agreement, disagreements = result["metrics"], result["reviewer_agreement"], result["disagreements"]
    lines = [
        "# Stage 18B Human Development Evaluation", "", "Evidence classification: **HUMAN DEVELOPMENT EVALUATION**", "",
        "These 50 candidates are development review material, not validation responses or released production responses.", "",
        "## Human metrics", "", "| Metric | Value | Denominator | Status |", "|---|---:|---:|---|",
    ]
    for name, row in metrics.items():
        lines.append(f"| {name} | {row['value']:.6f} | {row['denominator']} | {row['status']} |")
    lines.extend(["", "## Reviewer agreement", "",
        f"- Unsupported-claim raw agreement: {agreement['unsupported_claim']['value']:.6f} ({agreement['unsupported_claim']['agreements']}/{agreement['unsupported_claim']['denominator']})",
        f"- Citation-support raw agreement: {agreement['citation_support']['value']:.6f} ({agreement['citation_support']['agreements']}/{agreement['citation_support']['denominator']})",
        f"- Correctness quadratic weighted kappa: {agreement['correctness_quadratic_weighted_kappa']}",
        f"- Usefulness quadratic weighted kappa: {agreement['usefulness_quadratic_weighted_kappa']}", "",
        "## Disagreements", "", f"Count: {disagreements['count']}", "", f"Sample IDs: {', '.join(disagreements['sample_ids']) or 'none'}", "",
        "No disagreements were automatically adjudicated.", "",
    ])
    return "\n".join(lines)


def load_and_aggregate(first_path: Path, second_path: Path) -> dict[str, Any]:
    return aggregate_reviews(json.loads(first_path.read_text()), json.loads(second_path.read_text()))


def prepare_development_sample(dataset_path: Path, *, sample_size: int = 50) -> dict[str, Any]:
    """Generate review candidates from development tickets using frozen components."""
    raw = json.loads(dataset_path.read_text(encoding="utf-8"))
    tickets = raw[0] if raw and isinstance(raw, list) and isinstance(raw[0], list) else raw
    if not isinstance(tickets, list):
        raise ValueError("Development dataset must be a list")
    ingester = TicketNormalizationEngine()
    classifier = TicketClassificationEngine()
    retriever = DocumentationRetrievalEngine()
    generator = ResponseGenerationEngine()
    guardrails = GuardrailEngine()
    samples = []
    for input_index, ticket in enumerate(tickets):
        normalized = ingester.normalize_ticket(ticket)
        if not guardrails.check_input(normalized)["passed"]:
            continue
        classification = classifier.process_classification(normalized)
        retrieval = retriever.query_authoritative_knowledge(normalized["raw_content"], top_k=5)
        if getattr(retriever, "last_error", None):
            raise RuntimeError("Frozen retriever failed while preparing development sample")
        generation = generator.generate_response(normalized, classification, retrieval)
        if not generation.get("supported"):
            continue
        review = guardrails.check(generation, classification, normalized, retrieval)
        evidence = generator.build_retrieved_context(retrieval)
        samples.append({
            "sample_id": f"HDE-{len(samples) + 1:03d}", "development_input_index": input_index,
            "ticket_id": normalized["ticket_id"], "channel": normalized["channel"],
            "customer_request": normalized["raw_content"], "response_candidate": generation["response_text"],
            "citations": generation["citations"],
            "retrieved_evidence": [{
                "document_id": item["document_id"], "chunk_id": item["chunk_id"],
                "title": item["title"], "passage": item["passage"], "similarity_score": item["similarity_score"],
            } for item in evidence],
            "guardrail_outcome": "PASS" if review.get("passed") else "BLOCK",
            "production_release_claim": False,
        })
        if len(samples) == sample_size:
            break
    if len(samples) < sample_size:
        raise ValueError(f"Only {len(samples)} eligible generated responses; {sample_size} required")
    return {
        "schema_version": "1.0", "evidence_classification": "HUMAN DEVELOPMENT EVALUATION",
        "purpose": "Unrated response candidates for independent human review; not validation auto-response evidence.",
        "sampling": {
            "dataset_role": "development", "selection": "first eligible records in source order",
            "sample_size": len(samples), "routing_thresholds_changed": False,
            "generation_path": "direct frozen retrieval/generation/guardrail evaluation",
            "classification_threshold": 0.80, "retrieval_threshold": 0.30,
            "response_release_interpretation": "Candidates are review material, not production releases.",
        },
        "human_scores": None, "samples": samples,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--aggregate", nargs=2, metavar=("REVIEWER_1", "REVIEWER_2"), type=Path)
    parser.add_argument("--dataset", type=Path, default=Path("data/raw/development_tickets.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("evaluation/results/human-development-evaluation"))
    parser.add_argument("--sample", type=Path, default=Path("evaluation/results/human-development-evaluation/human-review-sample.json"))
    parser.add_argument("--output", type=Path, default=Path("evaluation/results/stage18-human-evaluation.json"))
    args = parser.parse_args()
    if args.aggregate:
        forms = [json.loads(path.read_text(encoding="utf-8")) for path in args.aggregate]
        sample = json.loads(args.sample.read_text(encoding="utf-8"))
        sample_ids = [row.get("sample_id") for row in sample.get("samples", [])]
        expected = {f"HDE-{number:03d}" for number in range(1, 51)}
        if len(sample_ids) != 50 or len(set(sample_ids)) != 50 or set(sample_ids) != expected:
            raise ValueError("Source sample must contain exactly HDE-001 through HDE-050")
        for form in forms:
            ids = [row.get("sample_id") for row in form.get("reviews", [])]
            if len(ids) != 50 or len(set(ids)) != 50 or set(ids) != expected:
                raise ValueError("Completed form must contain exactly HDE-001 through HDE-050")
        result = aggregate_reviews(forms[0], forms[1])
        result.update({
            "schema_version": "1.0", "generated_at": datetime.now(timezone.utc).isoformat(),
            "candidate_interpretation": "Development review candidates; not validation responses or released production responses.",
            "source_files": {
                "sample": args.sample.as_posix(),
                "reviewer_1": args.aggregate[0].as_posix(), "reviewer_2": args.aggregate[1].as_posix(),
            },
        })
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        args.output.with_suffix(".md").write_text(render_aggregate_markdown(result), encoding="utf-8")
        disagreement_path = args.output.with_name(args.output.stem + "-disagreements.json")
        disagreement_path.write_text(json.dumps({
            "schema_version": "1.0", "evidence_classification": "HUMAN DEVELOPMENT EVALUATION",
            "status": "PENDING_HUMAN_ADJUDICATION", "automatically_adjudicated": False,
            **result["disagreements"],
        }, indent=2) + "\n", encoding="utf-8")
        return 0
    package = prepare_development_sample(args.dataset)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sample_path = args.output_dir / "human-review-sample.json"
    sample_path.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sample_ids = [row["sample_id"] for row in package["samples"]]
    form = blank_reviewer_form(sample_ids)
    for number in (1, 2):
        (args.output_dir / f"reviewer-{number}-blank.json").write_text(
            json.dumps(form, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
