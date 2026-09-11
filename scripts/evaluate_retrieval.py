"""Development-only retrieval evaluation; never loads validation data."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np

from src.retrieve import (
    CHUNKING_CONFIGS,
    DEFAULT_CORPUS_PATH,
    DocumentationRetrievalEngine,
    load_authoritative_documents,
    chunk_document,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEVELOPMENT_PATH = PROJECT_ROOT / "data" / "raw" / "development_tickets.json"


class KeywordBaselineRetriever:
    """The pre-Stage-4 lexical fallback, preserved exactly as Baseline 0."""

    def __init__(self, corpus_path: Path | str = DEFAULT_CORPUS_PATH):
        self.documents = load_authoritative_documents(corpus_path)

    def query_authoritative_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
            "by", "is", "are", "was", "were", "my", "your", "our", "this", "that", "how", "do", "i",
        }
        words = [word.strip(".,!?:;\"'()[]{}") for word in query_lower.split()]
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        scored = []
        for doc in self.documents:
            title = doc["title"].lower()
            content = doc["content"].lower()
            category = doc["category"].lower()
            score = 5 if query_lower in title or query_lower in content else 0
            for keyword in keywords:
                score += 3 if keyword in title else 0
                score += 2 if keyword in category else 0
                score += 1 if keyword in content else 0
            if score > 0:
                scored.append(
                    {
                        "doc_id": doc["doc_id"],
                        "chunk_content": doc["content"][:300],
                        "relevance_score": min(score / 15.0, 1.0),
                    }
                )
        scored.sort(key=lambda row: row["relevance_score"], reverse=True)
        for rank, row in enumerate(scored[:top_k], start=1):
            row["rank"] = rank
        return scored[:top_k]


MODEL_CANDIDATES = {
    "minilm": "sentence-transformers/all-MiniLM-L6-v2",
    "bge_small": "BAAI/bge-small-en-v1.5",
    "e5_small": "intfloat/e5-small-v2",
}


class NumpySemanticExperimentRetriever:
    """Controlled semantic experiment using exact NumPy cosine ranking."""

    def __init__(self, model_name: str, strategy: str, min_score: float = -1.0):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.strategy = strategy
        self.min_score = min_score
        started = time.perf_counter()
        self.model = SentenceTransformer(model_name)
        self.documents = load_authoritative_documents()
        self.chunks: List[Dict[str, Any]] = []
        for doc in self.documents:
            for item in chunk_document(doc["content"], CHUNKING_CONFIGS[strategy]):
                self.chunks.append({**item, **{key: doc[key] for key in ("doc_id", "title", "category")}})
        passages = [self._passage_text(chunk["chunk_content"]) for chunk in self.chunks]
        self.embeddings = self.model.encode(
            passages,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        ).astype(np.float32)
        self.build_time_ms = (time.perf_counter() - started) * 1000.0
        self.parameter_count = sum(parameter.numel() for parameter in self.model.parameters())
        self.parameter_bytes = sum(parameter.numel() * parameter.element_size() for parameter in self.model.parameters())

    def _passage_text(self, text: str) -> str:
        return f"passage: {text}" if self.model_name == MODEL_CANDIDATES["e5_small"] else text

    def _query_text(self, text: str) -> str:
        if self.model_name == MODEL_CANDIDATES["e5_small"]:
            return f"query: {text}"
        if self.model_name == MODEL_CANDIDATES["bge_small"]:
            return f"Represent this sentence for searching relevant passages: {text}"
        return text

    def query_authoritative_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not query.strip() or top_k <= 0:
            return []
        query_vector = self.model.encode(
            [self._query_text(query)],
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )[0].astype(np.float32)
        scores = self.embeddings @ query_vector
        order = np.argsort(-scores, kind="stable")
        seen = set()
        results = []
        for index in order:
            chunk = self.chunks[int(index)]
            score = float(scores[int(index)])
            if score < self.min_score or chunk["doc_id"] in seen:
                continue
            seen.add(chunk["doc_id"])
            results.append(
                {
                    "doc_id": chunk["doc_id"],
                    "chunk_content": chunk["chunk_content"],
                    "relevance_score": score,
                    "rank": len(results) + 1,
                }
            )
            if len(results) == top_k:
                break
        return results


def load_tickets(path: Path | str) -> List[Dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list) and len(raw) == 1 and isinstance(raw[0], list):
        raw = raw[0]
    if not isinstance(raw, list):
        raise ValueError("Ticket dataset must be a JSON list")
    return raw


def ticket_query(ticket: Dict[str, Any]) -> str:
    return "\n".join(
        part.strip() for part in (str(ticket.get("subject", "")), str(ticket.get("body", ""))) if part.strip()
    )


def evaluate_tickets(
    engine: DocumentationRetrievalEngine,
    tickets: Sequence[Dict[str, Any]],
    cutoffs: Iterable[int] = (1, 3, 5),
) -> Dict[str, Any]:
    """Calculate document-level metrics with explicit eligible denominators."""

    ks = sorted(set(int(k) for k in cutoffs if int(k) > 0))
    if not ks:
        raise ValueError("At least one positive cutoff is required")
    rows: List[Dict[str, Any]] = []
    latencies: List[float] = []
    for ticket in tickets:
        started = time.perf_counter()
        results = engine.query_authoritative_knowledge(ticket_query(ticket), top_k=max(ks))
        latencies.append((time.perf_counter() - started) * 1000.0)
        expected = list(dict.fromkeys(ticket.get("labels", {}).get("expected_doc_ids", []) or []))
        retrieved = list(dict.fromkeys(result["doc_id"] for result in results))
        rows.append(
            {
                "ticket_id": ticket.get("ticket_id"),
                "query": ticket_query(ticket),
                "expected": expected,
                "retrieved": retrieved,
                "scores": [result["relevance_score"] for result in results],
            }
        )

    eligible = [row for row in rows if row["expected"]]
    unanswerable = [row for row in rows if not row["expected"]]
    metrics: Dict[str, Any] = {
        "ticket_count": len(rows),
        "eligible_count": len(eligible),
        "unanswerable_count": len(unanswerable),
        "no_result_count": sum(not row["retrieved"] for row in rows),
        "no_result_rate": sum(not row["retrieved"] for row in rows) / len(rows) if rows else None,
        "unanswerable_no_result_rate": (
            sum(not row["retrieved"] for row in unanswerable) / len(unanswerable) if unanswerable else None
        ),
    }
    for k in ks:
        recalls: List[float] = []
        precisions: List[float] = []
        reciprocal_ranks: List[float] = []
        hits = 0
        for row in eligible:
            returned = row["retrieved"][:k]
            expected = set(row["expected"])
            hit_count = len(expected.intersection(returned))
            recalls.append(hit_count / len(expected))
            # Precision is over documents actually returned at the cutoff; an
            # empty result is a zero, not an invented k-sized denominator.
            precisions.append(hit_count / len(returned) if returned else 0.0)
            hits += int(hit_count > 0)
            ranks = [index + 1 for index, doc_id in enumerate(returned) if doc_id in expected]
            reciprocal_ranks.append(1.0 / min(ranks) if ranks else 0.0)
        denominator = len(eligible)
        metrics[f"recall@{k}"] = statistics.fmean(recalls) if recalls else None
        metrics[f"precision@{k}"] = statistics.fmean(precisions) if precisions else None
        metrics[f"hit_rate@{k}"] = hits / denominator if denominator else None
        if k == max(ks):
            metrics["mrr"] = statistics.fmean(reciprocal_ranks) if reciprocal_ranks else None

    ordered = sorted(latencies)
    metrics["latency_ms_mean"] = statistics.fmean(latencies) if latencies else None
    metrics["latency_ms_p50"] = statistics.median(latencies) if latencies else None
    metrics["latency_ms_p95"] = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))] if ordered else None
    metrics["examples"] = select_examples(rows)
    return metrics


def select_examples(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    def first(predicate: Any) -> Any:
        return next((row for row in rows if predicate(row)), None)

    return {
        "strong": first(lambda row: bool(row["expected"]) and row["retrieved"][:1] == row["expected"][:1]),
        "ambiguous": first(
            lambda row: bool(row["expected"])
            and bool(set(row["expected"]).intersection(row["retrieved"]))
            and row["retrieved"][:1] != row["expected"][:1]
        ),
        "incorrect": first(
            lambda row: bool(row["expected"])
            and bool(row["retrieved"])
            and not set(row["expected"]).intersection(row["retrieved"])
        ),
        "no_result": first(lambda row: not row["retrieved"]),
    }


def run_production_smoke(tickets: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Exercise the real orchestrator entry point with controlled upstream confidence."""

    from src.orchestrator import SupportAutomationOrchestrator

    class SmokeClassifier:
        def process_classification(self, _ticket: Dict[str, Any]) -> Dict[str, Any]:
            return {"intent": "technical_support", "urgency": "medium", "confidence": 0.99}

    retriever = DocumentationRetrievalEngine()
    orchestrator = SupportAutomationOrchestrator(
        classifier=SmokeClassifier(),
        retriever=retriever,
        db_url="sqlite:///:memory:",
    )
    outcomes = []
    for ticket in tickets:
        result = orchestrator.process_ticket(ticket)
        retrieval = result.get("decision_record", {}).get("retrieval", [])
        outcomes.append(
            {
                "ticket_id": result.get("ticket_id"),
                "terminal_state": result.get("status"),
                "document_ids": [item["document_id"] for item in retrieval],
                "semantic_sources": [item.get("source") for item in retrieval],
            }
        )
    logged = orchestrator.logging_store.list_all_decisions()
    return {
        "ticket_count": len(tickets),
        "terminal_count": sum(item["terminal_state"] in {"AUTO_RESPOND", "ESCALATE", "BLOCK"} for item in outcomes),
        "logged_decision_count": len(logged),
        "semantic_retrieval_invoked": any(
            "authoritative_documentation" in item["semantic_sources"] for item in outcomes
        ),
        "retrieval_error": retriever.last_error,
        "outcomes": outcomes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development-data", type=Path, default=DEFAULT_DEVELOPMENT_PATH)
    parser.add_argument("--strategies", nargs="+", choices=sorted(CHUNKING_CONFIGS), default=sorted(CHUNKING_CONFIGS))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--min-score", type=float, default=0.30)
    parser.add_argument("--baseline-only", action="store_true")
    parser.add_argument("--experiment-matrix", action="store_true")
    parser.add_argument("--production-smoke", action="store_true")
    args = parser.parse_args()
    tickets = load_tickets(args.development_data)
    if args.limit is not None:
        tickets = tickets[: max(0, args.limit)]
    if args.production_smoke:
        print(json.dumps(run_production_smoke(tickets), indent=2, ensure_ascii=False))
        return
    report: Dict[str, Any] = {"baseline_0_keyword": evaluate_tickets(KeywordBaselineRetriever(), tickets)}
    if args.baseline_only:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    if args.experiment_matrix:
        chunk_reports = {}
        chunk_engines = {}
        for strategy in sorted(CHUNKING_CONFIGS):
            engine = NumpySemanticExperimentRetriever(MODEL_CANDIDATES["minilm"], strategy)
            metrics = evaluate_tickets(engine, tickets)
            metrics.update(
                {
                    "build_time_ms": engine.build_time_ms,
                    "chunk_count": len(engine.chunks),
                    "parameter_count": engine.parameter_count,
                    "parameter_bytes": engine.parameter_bytes,
                }
            )
            chunk_reports[strategy] = metrics
            chunk_engines[strategy] = engine
        report["chunking_minilm"] = chunk_reports
        chosen_strategy = max(
            chunk_reports,
            key=lambda name: (chunk_reports[name]["recall@3"], chunk_reports[name]["mrr"]),
        )
        report["chosen_chunking_by_recall3_then_mrr"] = chosen_strategy
        candidate_reports = {}
        candidate_engines = {}
        for label, model_name in MODEL_CANDIDATES.items():
            engine = (
                chunk_engines[chosen_strategy]
                if label == "minilm"
                else NumpySemanticExperimentRetriever(model_name, chosen_strategy)
            )
            metrics = evaluate_tickets(engine, tickets)
            metrics.update(
                {
                    "model_name": model_name,
                    "build_time_ms": engine.build_time_ms,
                    "chunk_count": len(engine.chunks),
                    "parameter_count": engine.parameter_count,
                    "parameter_bytes": engine.parameter_bytes,
                }
            )
            candidate_reports[label] = metrics
            candidate_engines[label] = engine
        report["embedding_candidates"] = candidate_reports
        chosen_model = max(
            candidate_reports,
            key=lambda name: (candidate_reports[name]["recall@3"], candidate_reports[name]["mrr"]),
        )
        report["chosen_model_by_recall3_then_mrr"] = chosen_model
        threshold_reports = {}
        engine = candidate_engines[chosen_model]
        for threshold in (0.0, 0.30, 0.40, 0.50, 0.60, 0.70):
            engine.min_score = threshold
            threshold_reports[f"{threshold:.2f}"] = evaluate_tickets(engine, tickets)
        report["threshold_analysis"] = threshold_reports
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    for strategy in args.strategies:
        engine = DocumentationRetrievalEngine(
            chunking_strategy=strategy,
            min_relevance_score=args.min_score,
        )
        report[strategy] = evaluate_tickets(engine, tickets)
        if engine.last_error:
            report[strategy]["retrieval_error"] = engine.last_error
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
