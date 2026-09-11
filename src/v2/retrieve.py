"""Section-aware evidence selection layered over the frozen V1 semantic index."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from src.retrieve import DocumentationRetrievalEngine

RETRIEVER_VERSION = "minilm-section-aware-v2.0.0"
_ACTION_PATTERN = re.compile(
    r"\b(how|steps?|fix|resolve|resolution|troubleshoot|rollback|revert|recover|configure|setup|set up|"
    r"paginate|pagination|next page|health check|unhealthy|what (?:do|should)|help me)\b", re.I)
_ACTION_INTENTS = frozenset({"account_access", "api_key_issue", "api_usage_question",
    "authentication_failure", "configuration_help", "data_export", "database_issue",
    "deployment_failure", "integration_help", "onboarding", "performance_degradation",
    "rate_limit", "rollback_request", "sso_configuration", "webhook_issue"})


def is_action_seeking(query: str, intent: Optional[str] = None) -> bool:
    return bool(_ACTION_PATTERN.search(query or "")) or intent in _ACTION_INTENTS


class ResolutionAwareRetrievalEngineV2:
    """Reuse V1 embeddings/ranking, then select supported sections within ranked docs."""
    version = RETRIEVER_VERSION

    def __init__(self, base: Optional[DocumentationRetrievalEngine] = None, **kwargs: Any):
        self.base = base or DocumentationRetrievalEngine(**kwargs)

    @property
    def last_error(self) -> Optional[str]:
        return self.base.last_error

    def query_authoritative_knowledge(self, query: str, top_k: int = 5,
                                      intent: Optional[str] = None) -> List[Dict[str, Any]]:
        base_results = self.base.query_authoritative_knowledge(query, top_k=top_k)
        if not base_results or not is_action_seeking(query, intent) or self.base._state is None:
            return [dict(row, selection_version=self.version) for row in base_results]
        query_embedding = self.base._encode(self.base._get_model(), [query.strip()])[0]
        scores = self.base._state.embeddings @ query_embedding
        selected: List[Dict[str, Any]] = []
        for original in base_results:
            doc_id = original["document_id"]
            candidates = [(index, chunk) for index, chunk in enumerate(self.base._state.chunks)
                          if chunk["document_id"] == doc_id
                          and chunk["section"].strip().lower() == "resolution"]
            if candidates:
                index, chunk = max(candidates,
                    key=lambda item: (float(scores[item[0]]), -item[1]["part_index"]))
                row = dict(original)
                row.update({"chunk_id": chunk["chunk_id"], "passage": chunk["chunk_content"],
                    "chunk_content": chunk["chunk_content"], "section": chunk["section"],
                    "semantic_score": float(scores[index]),
                    "selection_reason": "action_seeking_same_document_resolution",
                    "selection_version": self.version})
                row["source_metadata"] = dict(row["source_metadata"], section=chunk["section"])
            else:
                row = dict(original, selection_reason="no_resolution_section_available",
                           selection_version=self.version)
            selected.append(row)
        return selected

