"""Deterministic 22-intent and urgency classification.

The production classifier is a reproducible local baseline: TF-IDF text
features with separate logistic-regression models for intent and urgency.
Only ticket subject and body text are training/inference features.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import FeatureUnion, Pipeline


CANONICAL_INTENTS: Tuple[str, ...] = (
    "account_access",
    "api_key_issue",
    "api_usage_question",
    "authentication_failure",
    "billing_query",
    "compliance_request",
    "configuration_help",
    "data_export",
    "data_residency",
    "database_issue",
    "deployment_failure",
    "feature_request",
    "integration_help",
    "onboarding",
    "performance_degradation",
    "quota_or_overage",
    "rate_limit",
    "rollback_request",
    "security_incident",
    "sso_configuration",
    "unclear_request",
    "webhook_issue",
)
CANONICAL_URGENCIES: Tuple[str, ...] = ("high", "low", "medium")
FEATURE_FIELDS: Tuple[str, ...] = ("subject", "body")
MODEL_VERSION = "tfidf-logreg-22-v1"
RANDOM_SEED = 42
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAINING_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "development_tickets.json"
PROTECTED_EVALUATION_FILENAMES = {"validation_tickets.json", "final_tickets.json", "hidden_tickets.json"}


def _unwrap_tickets(raw: Any) -> List[Dict[str, Any]]:
    if isinstance(raw, list) and len(raw) == 1 and isinstance(raw[0], list):
        raw = raw[0]
    if not isinstance(raw, list) or not all(isinstance(ticket, dict) for ticket in raw):
        raise ValueError("Classifier training data must be a JSON list of ticket objects")
    return raw


def load_training_tickets(path: Path | str = DEFAULT_TRAINING_DATA_PATH) -> List[Dict[str, Any]]:
    """Load and validate labelled development tickets."""
    resolved = Path(path).resolve()
    if resolved.name.lower() in PROTECTED_EVALUATION_FILENAMES:
        raise ValueError("Classifier training is restricted from validation/final dataset paths")
    raw = json.loads(resolved.read_text(encoding="utf-8"))
    tickets = _unwrap_tickets(raw)
    for index, ticket in enumerate(tickets):
        labels = ticket.get("labels")
        if not isinstance(labels, Mapping):
            raise ValueError(f"Training ticket {index} has no labels object")
        if labels.get("intent") not in CANONICAL_INTENTS:
            raise ValueError(f"Training ticket {index} has unsupported intent label")
        if labels.get("urgency") not in CANONICAL_URGENCIES:
            raise ValueError(f"Training ticket {index} has unsupported urgency label")
        if not ticket_text(ticket):
            raise ValueError(f"Training ticket {index} has no subject/body text")
    return tickets


def ticket_text(ticket: Mapping[str, Any]) -> str:
    """Return the legitimate inference-time text used by both models."""
    metadata = ticket.get("metadata") if isinstance(ticket.get("metadata"), Mapping) else {}
    subject = ticket.get("subject")
    if subject is None:
        subject = metadata.get("original_subject", "")
    body = ticket.get("body")
    if body is None:
        body = ticket.get("raw_content", ticket.get("content", ""))
    return " ".join(part.strip() for part in (str(subject or ""), str(body or "")) if part and part.strip())


def text_group(ticket: Mapping[str, Any]) -> str:
    """Stable duplicate-group key used to prevent train/holdout overlap."""
    return re.sub(r"\s+", " ", ticket_text(ticket).lower()).strip()


def training_data_sha256(path: Path | str = DEFAULT_TRAINING_DATA_PATH) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _intent_pipeline() -> Pipeline:
    features = FeatureUnion(
        [
            ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
            ("character", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)),
        ]
    )
    return Pipeline(
        [
            ("features", features),
            ("classifier", LogisticRegression(
                class_weight="balanced", max_iter=2000, multi_class="ovr",
                random_state=RANDOM_SEED, solver="liblinear",
            )),
        ]
    )


def _urgency_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("features", TfidfVectorizer(ngram_range=(1, 1), min_df=1, sublinear_tf=True)),
            ("classifier", LogisticRegression(
                class_weight="balanced", max_iter=2000, multi_class="ovr",
                random_state=RANDOM_SEED, solver="liblinear",
            )),
        ]
    )


def build_model_bundle(tickets: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Fit one intent model and one urgency model from labelled tickets."""
    texts = [ticket_text(ticket) for ticket in tickets]
    intents = [ticket["labels"]["intent"] for ticket in tickets]
    urgencies = [ticket["labels"]["urgency"] for ticket in tickets]
    if set(intents) != set(CANONICAL_INTENTS):
        missing = sorted(set(CANONICAL_INTENTS) - set(intents))
        raise ValueError(f"Training partition does not support all canonical intents: {missing}")
    if set(urgencies) != set(CANONICAL_URGENCIES):
        missing = sorted(set(CANONICAL_URGENCIES) - set(urgencies))
        raise ValueError(f"Training partition does not support all canonical urgencies: {missing}")
    intent_model = _intent_pipeline().fit(texts, intents)
    urgency_model = _urgency_pipeline().fit(texts, urgencies)
    return {
        "intent_model": intent_model,
        "urgency_model": urgency_model,
        "model_version": MODEL_VERSION,
        "training_size": len(tickets),
        "feature_fields": FEATURE_FIELDS,
    }


def _ranked_probabilities(model: Pipeline, text: str) -> List[Tuple[str, float]]:
    probabilities = model.predict_proba([text])[0]
    classes = model.named_steps["classifier"].classes_
    return sorted(
        ((str(label), float(probability)) for label, probability in zip(classes, probabilities)),
        key=lambda item: (-item[1], item[0]),
    )


def predict_with_bundle(bundle: Mapping[str, Any], ticket: Mapping[str, Any]) -> Dict[str, Any]:
    """Classify one valid-text ticket with an already fitted model bundle."""
    text = ticket_text(ticket)
    ranked_intents = _ranked_probabilities(bundle["intent_model"], text)
    ranked_urgencies = _ranked_probabilities(bundle["urgency_model"], text)
    intent, confidence = ranked_intents[0]
    urgency, urgency_confidence = ranked_urgencies[0]
    alternatives = [
        {"intent": label, "confidence": round(probability, 6)}
        for label, probability in ranked_intents[1:4]
    ]
    return {
        "intent": intent,
        "urgency": urgency,
        "confidence": round(confidence, 6),
        "urgency_confidence": round(urgency_confidence, 6),
        "reasoning": "Deterministic TF-IDF logistic-regression prediction from subject and body text.",
        "alternative_intent": alternatives[0]["intent"] if alternatives else None,
        "alternative_intents": alternatives,
        "model_name": MODEL_VERSION,
        "model_version": MODEL_VERSION,
        "training_data_sha256": bundle.get("training_data_sha256"),
    }


def stratified_group_holdout(
    tickets: Sequence[Mapping[str, Any]], random_seed: int = RANDOM_SEED, folds: int = 5
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Create a reproducible intent-stratified holdout with no exact-text overlap."""
    texts = [ticket_text(ticket) for ticket in tickets]
    intents = [ticket["labels"]["intent"] for ticket in tickets]
    groups = [text_group(ticket) for ticket in tickets]
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=random_seed)
    train_indices, holdout_indices = next(splitter.split(texts, intents, groups))
    train = [dict(tickets[index]) for index in train_indices]
    holdout = [dict(tickets[index]) for index in holdout_indices]
    if {text_group(ticket) for ticket in train} & {text_group(ticket) for ticket in holdout}:
        raise RuntimeError("Duplicate text groups leaked across train and holdout")
    return train, holdout


class TicketClassificationEngine:
    """Classify normalized tickets using one lazily trained process-wide model."""

    _bundle_cache: Dict[str, Dict[str, Any]] = {}
    _cache_lock = threading.Lock()

    def __init__(
        self,
        client: Optional[Any] = None,
        training_data_path: Path | str = DEFAULT_TRAINING_DATA_PATH,
    ):
        # ``client`` remains accepted for public-interface compatibility. The
        # reproducible production baseline is local and does not call it.
        self.client = client
        self.training_data_path = Path(training_data_path)
        self.model_name = MODEL_VERSION

    @property
    def supported_intents(self) -> Tuple[str, ...]:
        return CANONICAL_INTENTS

    @property
    def supported_urgencies(self) -> Tuple[str, ...]:
        return CANONICAL_URGENCIES

    def get_classification_prompt(self, ticket_content: str) -> List[Dict[str, str]]:
        """Retained structured contract for integrations that display a prompt."""
        intents = ", ".join(CANONICAL_INTENTS)
        system_instruction = (
            "Classify one CloudServe ticket into exactly one canonical intent and urgency. "
            f"Intents: [{intents}]. Urgencies: [low, medium, high]. "
            "Return intent, urgency, numeric confidence, and alternatives as JSON."
        )
        return [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Ticket Content:\n{ticket_content}"},
        ]

    def _get_bundle(self) -> Dict[str, Any]:
        cache_key = str(self.training_data_path.resolve())
        bundle = self._bundle_cache.get(cache_key)
        if bundle is not None:
            return bundle
        with self._cache_lock:
            bundle = self._bundle_cache.get(cache_key)
            if bundle is None:
                bundle = build_model_bundle(load_training_tickets(self.training_data_path))
                bundle["training_data_sha256"] = training_data_sha256(self.training_data_path)
                self._bundle_cache[cache_key] = bundle
        return bundle

    def process_classification(self, normalized_ticket: Any) -> Dict[str, Any]:
        """Return canonical labels and probability-derived confidence, or fail safely."""
        if not isinstance(normalized_ticket, Mapping):
            return self._fallback("Classifier input must be a mapping")
        text = ticket_text(normalized_ticket)
        if not text.strip():
            return self._fallback("Ticket contains no classifiable subject or body text")
        try:
            bundle = self._get_bundle()
            return predict_with_bundle(bundle, normalized_ticket)
        except Exception as exc:
            return self._fallback("Classifier unavailable", type(exc).__name__)

    @staticmethod
    def _fallback(reason: str, error_type: Optional[str] = None) -> Dict[str, Any]:
        return {
            "failure_code": "CLASSIFICATION_FAILURE",
            "error_type": error_type,
            "intent": "unclear_request",
            "urgency": "medium",
            "confidence": 0.0,
            "urgency_confidence": 0.0,
            "reasoning": reason,
            "alternative_intent": None,
            "alternative_intents": [],
            "model_name": MODEL_VERSION,
            "model_version": MODEL_VERSION,
            "training_data_sha256": None,
        }
