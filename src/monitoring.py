"""Privacy-bounded Prometheus metrics for the operational API boundary."""

from __future__ import annotations

import math
import threading
from collections import deque
from typing import Any, Mapping

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest


REGISTRY = CollectorRegistry(auto_describe=True)
TICKETS = Counter("support_tickets_processed", "Processed support tickets.", ["channel", "terminal_action", "processing_status"], registry=REGISTRY)
GUARDRAIL_BLOCKS = Counter("support_guardrail_blocks", "Guardrail-blocked tickets.", ["reason"], registry=REGISTRY)
FAILURES = Counter("support_processing_failures", "Ticket processing failures.", ["category"], registry=REGISTRY)
LATENCY = Histogram("support_processing_latency_seconds", "End-to-end API processing latency.", buckets=(.01, .025, .05, .1, .25, .5, 1, 2, 3, 5, 10), registry=REGISTRY)
CONFIDENCE = Histogram("support_classification_confidence", "Classification confidence distribution.", buckets=(0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1), registry=REGISTRY)
AUTO_RATE = Gauge("support_auto_response_rate", "Process-lifetime auto-response rate.", registry=REGISTRY)
ESCALATION_RATE = Gauge("support_escalation_rate", "Process-lifetime escalation rate.", registry=REGISTRY)
LATENCY_P50 = Gauge("support_processing_latency_seconds_p50", "Rolling P50 API processing latency over up to 1024 requests.", registry=REGISTRY)
LATENCY_P95 = Gauge("support_processing_latency_seconds_p95", "Rolling P95 API processing latency over up to 1024 requests.", registry=REGISTRY)

_lock = threading.Lock()
_total = _auto = _escalated = 0
_latencies: deque[float] = deque(maxlen=1024)

CHANNELS = {"email", "live_chat", "documentation_comments", "community_forum", "unknown"}
CHANNEL_ALIASES = {"chat": "live_chat", "docs_comment": "documentation_comments", "forum": "community_forum"}
GUARDRAIL_REASONS = {
    "PRIVATE_DATA_LEAK", "SECRET_DISCLOSURE", "GROUNDING_FAILURE", "UNSUPPORTED_CITATION",
    "PROMPT_INJECTION", "SYSTEM_PROMPT_DISCLOSURE", "UNSUPPORTED_COMMITMENT",
    "INVALID_GENERATION", "MISSING_EVIDENCE", "CONFIDENCE_FAILURE", "GUARDRAIL_INTERNAL_ERROR",
}
FAILURE_CATEGORIES = {
    "INGESTION_FAILURE", "MALFORMED_INPUT", "CLASSIFICATION_FAILURE", "RETRIEVAL_FAILURE", "ROUTING_FAILURE",
    "GENERATION_FAILED", "GUARDRAIL_INTERNAL_ERROR", "PIPELINE_INTERNAL_ERROR",
    "AUDIT_PERSISTENCE_FAILED", "PROVIDER_TIMEOUT", "PROVIDER_RATE_LIMIT", "PROVIDER_UNAVAILABLE",
    "PROVIDER_ERROR", "GENERATION_FAILURE", "INVALID_PROVIDER_OUTPUT",
}


def _channel(value: Any) -> str:
    candidate = CHANNEL_ALIASES.get(str(value), str(value))
    return candidate if candidate in CHANNELS else "unknown"


def observe_ticket(channel: str, result: Mapping[str, Any], elapsed_seconds: float) -> None:
    """Observe only bounded enums and numeric values; never customer content or IDs."""
    global _total, _auto, _escalated
    action = "AUTO_RESPOND" if result.get("response_released") is True and result.get("status") == "AUTO_RESPOND" else "ESCALATE"
    status = "FAILED" if result.get("processing_status") == "FAILED" else "COMPLETED"
    TICKETS.labels(_channel(channel), action, status).inc()
    elapsed = max(0.0, float(elapsed_seconds))
    LATENCY.observe(elapsed)
    classification = result.get("classification") if isinstance(result.get("classification"), Mapping) else {}
    confidence = classification.get("confidence")
    if isinstance(confidence, (int, float)) and not isinstance(confidence, bool) and math.isfinite(confidence) and 0 <= confidence <= 1:
        CONFIDENCE.observe(float(confidence))
    guardrails = result.get("guardrails") if isinstance(result.get("guardrails"), Mapping) else {}
    if guardrails.get("blocked") or guardrails.get("passed") is False:
        reasons = guardrails.get("reason_codes") or [guardrails.get("primary_reason")]
        recorded = False
        for reason in reasons:
            if reason in GUARDRAIL_REASONS:
                GUARDRAIL_BLOCKS.labels(reason).inc(); recorded = True
        if not recorded:
            GUARDRAIL_BLOCKS.labels("OTHER").inc()
    if status == "FAILED":
        category = result.get("error_category") or result.get("failure_state") or result.get("reason_code")
        FAILURES.labels(category if category in FAILURE_CATEGORIES else "OTHER").inc()
    with _lock:
        _total += 1
        _auto += action == "AUTO_RESPOND"
        _escalated += action == "ESCALATE"
        _latencies.append(elapsed)
        ordered = sorted(_latencies)
        def percentile(pct: float) -> float:
            position = (len(ordered) - 1) * pct
            low, high = int(position), min(int(position) + 1, len(ordered) - 1)
            fraction = position - low
            return ordered[low] + (ordered[high] - ordered[low]) * fraction
        AUTO_RATE.set(_auto / _total)
        ESCALATION_RATE.set(_escalated / _total)
        LATENCY_P50.set(percentile(.50))
        LATENCY_P95.set(percentile(.95))


def prometheus_payload() -> bytes:
    return generate_latest(REGISTRY)
