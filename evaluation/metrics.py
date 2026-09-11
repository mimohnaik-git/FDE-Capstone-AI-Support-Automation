"""Truthful, denominator-aware metrics and the Stage 10 metric registry."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

MEASUREMENT_TYPES = ("AUTOMATED", "HUMAN_REVIEW", "OPERATIONAL", "NOT_MEASURABLE")
ALLOWED_STATUSES = ("PASS", "FAIL", "NOT MEASURED", "NOT APPLICABLE", "MEASURED — NO FORMAL TARGET")
NO_TARGET = "A value is MEASURED — NO FORMAL TARGET; a missing value is NOT MEASURED."


def _entry(name: str, definition: str, population: str, kind: str, logic: str,
           target: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    if kind not in MEASUREMENT_TYPES:
        raise ValueError(f"Unsupported measurement type: {kind}")
    item = {"name": name, "definition": definition, "eligible_population": population,
            "measurement_type": kind, "status_logic": logic}
    if target is not None:
        item["target"] = dict(target)
    return item


def _target(operator: str, value: float, display: str) -> Dict[str, Any]:
    return {"operator": operator, "value": value, "display": display}


METRIC_REGISTRY: Dict[str, Dict[str, Any]] = {
    "intent_accuracy": _entry("Intent classification accuracy", "Correct intent predictions divided by labelled tickets.", "Tickets with an intent label.", "AUTOMATED", NO_TARGET),
    "intent_macro_precision": _entry("Intent macro precision", "Unweighted mean of per-intent precision.", "Intent classes represented in labelled tickets.", "AUTOMATED", "PASS at >=85%; FAIL below; missing is NOT MEASURED.", _target("gte", .85, ">=85%")),
    "intent_macro_recall": _entry("Intent macro recall", "Unweighted mean of per-intent recall.", "Intent classes represented in labelled tickets.", "AUTOMATED", NO_TARGET),
    "intent_macro_f1": _entry("Intent macro F1", "Unweighted mean of per-intent F1.", "Intent classes represented in labelled tickets.", "AUTOMATED", NO_TARGET),
    "urgency_accuracy": _entry("Urgency classification accuracy", "Correct urgency predictions divided by labelled tickets.", "Tickets with an urgency label.", "AUTOMATED", NO_TARGET),
    "urgency_macro_precision": _entry("Urgency macro precision", "Unweighted mean of per-urgency precision.", "Urgency classes represented in labelled tickets.", "AUTOMATED", NO_TARGET),
    "urgency_macro_recall": _entry("Urgency macro recall", "Unweighted mean of per-urgency recall.", "Urgency classes represented in labelled tickets.", "AUTOMATED", NO_TARGET),
    "urgency_macro_f1": _entry("Urgency macro F1", "Unweighted mean of per-urgency F1.", "Urgency classes represented in labelled tickets.", "AUTOMATED", NO_TARGET),
    **{f"retrieval_recall_at_{k}": _entry(f"Retrieval Recall@{k}", f"Mean share of expected document IDs in the first {k} results.", "Tickets with at least one expected document ID.", "AUTOMATED", NO_TARGET) for k in (1, 3, 5)},
    **{f"retrieval_precision_at_{k}": _entry(f"Retrieval Precision@{k}", f"Mean share of the first {k} result IDs that are expected.", "Tickets with at least one expected document ID.", "AUTOMATED", NO_TARGET) for k in (1, 3, 5)},
    "retrieval_mrr": _entry("Retrieval mean reciprocal rank", "Mean reciprocal rank of the first expected document ID.", "Tickets with at least one expected document ID.", "AUTOMATED", NO_TARGET),
    "routing_accuracy": _entry("Routing accuracy", "Correct binary routes divided by route-labelled tickets.", "Tickets with AUTO_RESPOND or ESCALATE labels; BLOCK maps to ESCALATE.", "AUTOMATED", NO_TARGET),
    "auto_response_precision": _entry("Auto-response precision", "Correct predicted AUTO_RESPOND routes divided by labelled predicted AUTO_RESPOND routes.", "Predicted AUTO_RESPOND tickets with route labels.", "AUTOMATED", NO_TARGET),
    "auto_response_recall": _entry("Auto-response recall", "Correct AUTO_RESPOND routes divided by labelled expected AUTO_RESPOND routes.", "Expected AUTO_RESPOND tickets with route labels.", "AUTOMATED", NO_TARGET),
    "automation_rate": _entry("Automation rate", "AUTO_RESPOND outcomes divided by valid terminal outcomes.", "Tickets ending in AUTO_RESPOND or ESCALATE.", "AUTOMATED", NO_TARGET),
    "escalation_rate": _entry("Escalation rate", "ESCALATE outcomes divided by valid terminal outcomes.", "Tickets ending in AUTO_RESPOND or ESCALATE.", "AUTOMATED", "PASS at <=30%; FAIL above; missing is NOT MEASURED.", _target("lte", .30, "<=30%")),
    "guardrail_coverage": _entry("Guardrail coverage", "Generated candidates with guardrail execution evidence divided by generated candidates.", "Tickets whose pre-guardrail route was AUTO_RESPOND.", "AUTOMATED", "PASS only at 100% with a non-zero denominator.", _target("gte", 1.0, "100%")),
    "processing_failure_rate": _entry("Processing failure rate", "Processing errors divided by processed tickets.", "All processed tickets.", "AUTOMATED", NO_TARGET),
    "decision_log_coverage": _entry("Decision-log coverage", "Persisted retrievable audit decisions divided by processed tickets.", "All processed tickets.", "AUTOMATED", "PASS only at 100% with a non-zero denominator.", _target("gte", 1.0, "100%")),
    "pipeline_latency_p50": _entry("P50 pipeline latency", "Median local end-to-end pipeline processing duration.", "Processed tickets with recorded durations.", "AUTOMATED", NO_TARGET),
    "pipeline_latency_p95": _entry("P95 pipeline latency", "95th percentile local end-to-end pipeline duration including retrieval.", "Processed tickets with recorded durations.", "AUTOMATED", "PASS below 3 seconds; FAIL otherwise; missing is NOT MEASURED.", _target("lt", 3.0, "<3 seconds")),
    "confidence_calibration_error": _entry("Confidence calibration error", "Expected absolute confidence-to-accuracy gap across bins.", "Tickets with intent labels, predictions, and valid confidence.", "AUTOMATED", "PASS at <=5 percentage points; FAIL above.", _target("lte", .05, "<=5 percentage points")),
    "citation_id_validity": _entry("Citation ID validity", "Citation IDs found among that response's retrieved document IDs divided by citations emitted.", "Citations on AUTO_RESPOND outcomes.", "AUTOMATED", NO_TARGET),
    "private_data_occurrences": _entry("Private-data occurrences in released responses", "Released responses whose recorded private-data check failed.", "Released responses with a recorded private-data check.", "AUTOMATED", "PASS at zero with a non-zero denominator; FAIL above zero.", _target("eq", 0, "0")),
    "hallucination_rate": _entry("Hallucination rate", "Generated responses containing at least one unsupported claim.", "At least 50 responses independently assessed by two humans with agreement reported.", "HUMAN_REVIEW", "PASS at <=5% only after required human review.", _target("lte", .05, "<=5%")),
    "semantic_citation_accuracy": _entry("Semantic citation accuracy", "Citations whose passage supports the attached claim.", "Human-reviewed claim-citation pairs.", "HUMAN_REVIEW", "PASS at >=95% only after semantic review.", _target("gte", .95, ">=95%")),
    "response_correctness": _entry("Response correctness", "Human rubric score for factual and task correctness.", "Responses under a documented human sampling plan.", "HUMAN_REVIEW", NO_TARGET),
    "response_usefulness": _entry("Response usefulness", "Human rubric score for usefulness in resolving the support need.", "Responses under a documented human sampling plan.", "HUMAN_REVIEW", NO_TARGET),
    "first_contact_resolution": _entry("First contact resolution", "Tickets resolved without human involvement and repeat contact.", "Operational tickets with verified resolution and follow-up outcomes.", "OPERATIONAL", "PASS at >=60% only with operational evidence.", _target("gte", .60, ">=60%")),
    "first_response_time": _entry("Time to first substantive response", "Time from arrival to receipt of a substantive customer response.", "Operational tickets with arrival and delivered-response timestamps.", "OPERATIONAL", "PASS when mean is under 300 seconds; pipeline runtime is ineligible.", _target("lt", 300.0, "mean <5 minutes")),
    "csat": _entry("Customer satisfaction", "Mean customer-provided post-response rating on a five-point scale.", "Operational tickets with attributable customer ratings.", "OPERATIONAL", "PASS at >=4.0/5 only with customer ratings.", _target("gte", 4.0, ">=4.0/5")),
    "availability": _entry("Service availability", "Share of a defined observation window meeting the service availability definition.", "A documented operational observation window.", "OPERATIONAL", "PASS at >=99.5% only after an availability study.", _target("gte", .995, ">=99.5%")),
    "repeat_contact_rate": _entry("Repeat contact rate", "Same customer raising the same issue within one week after resolution.", "Linked operational histories with a complete one-week window.", "OPERATIONAL", "Requires a measured baseline and follow-up rate.", _target("relative_lte", .5, "approximately halved")),
    "cross_group_quality_difference": _entry("Cross-group quality difference", "Largest difference in a defined quality outcome across customer groups.", "Adequately sized segments with the same reviewed quality outcome.", "HUMAN_REVIEW", "PASS below 5 points only after segmented review.", _target("lt", .05, "<5 percentage points")),
}


def metric_status(value: Optional[float], target: Optional[Mapping[str, Any]] = None, *,
                  applicable: bool = True, denominator: Optional[int] = None) -> str:
    if not applicable:
        return "NOT APPLICABLE"
    if value is None or denominator == 0:
        return "NOT MEASURED"
    if target is None:
        return "MEASURED — NO FORMAL TARGET"
    op, threshold = target.get("operator"), target.get("value")
    if op == "relative_lte":
        return "NOT MEASURED"
    comparisons = {"gte": value >= threshold, "lte": value <= threshold,
                   "lt": value < threshold, "eq": value == threshold}
    if op not in comparisons:
        raise ValueError(f"Unsupported target operator: {op}")
    return "PASS" if comparisons[op] else "FAIL"


def _ratio(numerator: float, denominator: int, excluded: int = 0) -> Dict[str, Any]:
    return {"value": round(numerator / denominator, 6) if denominator else None,
            "numerator": numerator, "denominator": denominator, "eligible": denominator, "excluded": excluded}


def _paired(actual: Sequence[Any], expected: Sequence[Any], name: str) -> None:
    if len(actual) != len(expected):
        raise ValueError(f"{name} requires equal-length sequences; got {len(actual)} and {len(expected)}")


def _label(value: Any) -> Optional[str]:
    text = "" if value is None else str(value).strip().lower()
    return text or None


def _expected(ticket: Mapping[str, Any], key: str, mapping: Optional[Mapping[str, str]] = None) -> Optional[str]:
    labels = ticket.get("labels")
    if not isinstance(labels, Mapping):
        return None
    value = _label(labels.get(key))
    normalized_map = {_label(k): _label(v) for k, v in (mapping or {}).items()}
    return normalized_map.get(value, value)


def _pairs(predictions: Sequence[Mapping[str, Any]], tickets: Sequence[Mapping[str, Any]], field: str,
           mapping: Optional[Mapping[str, str]] = None) -> Tuple[List[Tuple[Optional[str], str]], int]:
    result = []
    for prediction, ticket in zip(predictions, tickets):
        expected = _expected(ticket, field, mapping)
        if expected is not None:
            result.append((_label(prediction.get(field)), expected))
    return result, len(tickets) - len(result)


def _classification_summary(pairs: Sequence[Tuple[Optional[str], str]], excluded: int) -> Dict[str, Any]:
    classes = sorted({expected for _, expected in pairs}); per_class = {}
    ps: List[float] = []; rs: List[float] = []; fs: List[float] = []
    for name in classes:
        tp = sum(a == name and e == name for a, e in pairs)
        fp = sum(a == name and e != name for a, e in pairs)
        fn = sum(a != name and e == name for a, e in pairs)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        ps.append(precision); rs.append(recall); fs.append(f1)
        per_class[name] = {"support": sum(e == name for _, e in pairs), "true_positive": tp,
                           "false_positive": fp, "false_negative": fn, "precision": round(precision, 6),
                           "recall": round(recall, 6), "f1": round(f1, 6)}
    def macro(values: List[float]) -> Dict[str, Any]:
        return {"value": round(sum(values) / len(values), 6) if values else None, "numerator": sum(values),
                "denominator": len(values), "eligible": len(values), "excluded": 0,
                "eligible_classes": len(values), "sample_eligible": len(pairs), "sample_excluded": excluded}
    return {"accuracy": _ratio(sum(a == e for a, e in pairs), len(pairs), excluded),
            "macro_precision": macro(ps), "macro_recall": macro(rs), "macro_f1": macro(fs), "per_class": per_class}


def _calibration(predictions: Sequence[Mapping[str, Any]], tickets: Sequence[Mapping[str, Any]], mapping: Optional[Mapping[str, str]]) -> Dict[str, Any]:
    eligible = []; excluded = 0
    for prediction, ticket in zip(predictions, tickets):
        try:
            confidence = float(prediction.get("confidence"))
        except (TypeError, ValueError):
            excluded += 1; continue
        actual, expected = _label(prediction.get("intent")), _expected(ticket, "intent", mapping)
        if actual is None or expected is None or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            excluded += 1; continue
        eligible.append((confidence, int(actual == expected)))
    buckets: Dict[int, list] = defaultdict(list)
    for confidence, correct in eligible:
        buckets[min(int(confidence * 10), 9)].append((confidence, correct))
    weighted, rows = 0.0, []
    for bucket in sorted(buckets):
        values = buckets[bucket]; stated = sum(x for x, _ in values) / len(values); observed = sum(x for _, x in values) / len(values)
        gap = abs(stated - observed); weighted += gap * len(values)
        rows.append({"lower": bucket / 10, "upper": (bucket + 1) / 10, "count": len(values),
                     "mean_confidence": round(stated, 6), "observed_accuracy": round(observed, 6), "absolute_gap": round(gap, 6)})
    return {"expected_calibration_error": _ratio(weighted, len(eligible), excluded), "bins": rows}


def calculate_classification_metrics(predictions: List[Dict[str, Any]], tickets: List[Dict[str, Any]],
                                     intent_label_map: Optional[Mapping[str, str]] = None) -> Dict[str, Any]:
    _paired(predictions, tickets, "classification metrics")
    intent, ie = _pairs(predictions, tickets, "intent", intent_label_map); urgency, ue = _pairs(predictions, tickets, "urgency")
    return {"intent": _classification_summary(intent, ie), "urgency": _classification_summary(urgency, ue),
            "calibration": _calibration(predictions, tickets, intent_label_map),
            "intent_label_mapping": dict(intent_label_map or {}),
            "mapping_policy": "explicit_only; identity comparison when absent"}


def calculate_retrieval_metrics(retrieved: List[List[str]], expected: List[Optional[List[str]]], k: Optional[int] = None) -> Dict[str, Any]:
    if k is not None and k <= 0:
        raise ValueError("k must be positive")
    _paired(retrieved, expected, "retrieval metrics")
    recalls = {x: [] for x in (1, 3, 5)}; precisions = {x: [] for x in (1, 3, 5)}; rrs = []; excluded = 0
    for actual, truth in zip(retrieved, expected):
        truth_set = {_label(x) for x in (truth or []) if _label(x)}
        if not truth_set:
            excluded += 1; continue
        ranked = [_label(x) for x in (actual or []) if _label(x)]
        for cutoff in (1, 3, 5):
            top = set(ranked[:cutoff]); overlap = top & truth_set
            recalls[cutoff].append(len(overlap) / len(truth_set)); precisions[cutoff].append(len(overlap) / len(top) if top else 0.0)
        rank = next((i for i, item in enumerate(ranked, 1) if item in truth_set), None); rrs.append(1 / rank if rank else 0.0)
    result: Dict[str, Any] = {"cutoffs": [1, 3, 5], "eligibility": "tickets with one or more expected_doc_ids"}
    for cutoff in (1, 3, 5):
        result[f"recall_at_{cutoff}"] = _ratio(sum(recalls[cutoff]), len(rrs), excluded)
        result[f"precision_at_{cutoff}"] = _ratio(sum(precisions[cutoff]), len(rrs), excluded)
    result["mrr"] = _ratio(sum(rrs), len(rrs), excluded)
    alias = k if k in (1, 3, 5) else 3
    result.update({"k": alias, "recall_at_k": result[f"recall_at_{alias}"], "precision_at_k": result[f"precision_at_{alias}"]})
    return result


def _route(value: Any) -> Optional[str]:
    value = _label(value)
    return "escalate" if value == "block" else value


def calculate_routing_metrics(actual: List[str], expected: List[Optional[str]]) -> Dict[str, Any]:
    _paired(actual, expected, "routing metrics")
    pairs = [(_route(a), _route(e)) for a, e in zip(actual, expected) if _route(e) in {"auto_respond", "escalate"}]
    tp = sum(a == e == "auto_respond" for a, e in pairs); fp = sum(a == "auto_respond" and e == "escalate" for a, e in pairs)
    fn = sum(a != "auto_respond" and e == "auto_respond" for a, e in pairs); excluded = len(expected) - len(pairs)
    terminal = [_route(x) for x in actual if _route(x) in {"auto_respond", "escalate"}]
    return {"accuracy": _ratio(sum(a == e for a, e in pairs), len(pairs), excluded),
            "auto_respond_precision": _ratio(tp, tp + fp, excluded), "auto_respond_recall": _ratio(tp, tp + fn, excluded),
            "auto_response_rate": _ratio(sum(x == "auto_respond" for x in terminal), len(terminal), len(actual) - len(terminal)),
            "escalation_rate": _ratio(sum(x == "escalate" for x in terminal), len(terminal), len(actual) - len(terminal)),
            "false_auto_respond_count": fp, "route_mapping": {"BLOCK": "ESCALATE"}}


def percentile(values: Iterable[float], pct: float) -> Optional[float]:
    ordered = sorted(float(x) for x in values)
    if not ordered: return None
    if not 0 <= pct <= 100: raise ValueError("percentile must be in [0, 100]")
    position = (len(ordered) - 1) * pct / 100; low, high = math.floor(position), math.ceil(position)
    return ordered[low] if low == high else ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def _guardrail_metrics(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    candidates = [r for r in records if _route(r.get("original_route")) == "auto_respond"]
    covered = 0; activations: Dict[str, int] = defaultdict(int); private_bad = 0; private_den = 0
    for row in candidates:
        guardrails = row.get("guardrails") if isinstance(row.get("guardrails"), Mapping) else {}
        checks = guardrails.get("checks") if isinstance(guardrails.get("checks"), Mapping) else {}
        covered += bool(checks)
        for key, check in checks.items():
            if isinstance(check, Mapping) and (check.get("blocked") or check.get("passed") is False): activations[str(key)] += 1
        private = checks.get("private_data")
        if row.get("response_released") and isinstance(private, Mapping):
            private_den += 1; private_bad += bool(private.get("blocked") or private.get("passed") is False)
    return {"coverage": _ratio(covered, len(candidates)), "eligible_definition": "pre-guardrail AUTO_RESPOND candidates",
            "activations_by_type": dict(sorted(activations.items())),
            "blocked_ticket_count": sum(bool((r.get("guardrails") or {}).get("blocked")) for r in records),
            "private_data_occurrences_in_released_responses": {"value": private_bad if private_den else None,
                "numerator": private_bad, "denominator": private_den, "eligible": private_den, "excluded": len(records) - private_den}}


def calculate_operational_metrics(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    latencies = [float(r["latency_seconds"]) for r in records if r.get("latency_seconds") is not None]; total = len(records)
    return {"latency_seconds": {"mean": round(sum(latencies) / len(latencies), 6) if latencies else None,
                                "p50": round(percentile(latencies, 50), 6) if latencies else None,
                                "p95": round(percentile(latencies, 95), 6) if latencies else None,
                                "eligible": len(latencies), "denominator": len(latencies), "excluded": total - len(latencies)},
            "processing_failure_rate": _ratio(sum(bool(r.get("processing_error")) for r in records), total),
            "decision_log_coverage": _ratio(sum(bool(r.get("decision_id") and r.get("audit_record_present")) for r in records), total)}


def calculate_citation_id_validity(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    valid = total = 0
    for row in records:
        if _route(row.get("predicted_route")) != "auto_respond": continue
        retrieved = {_label(x) for x in (row.get("retrieved_doc_ids") or []) if _label(x)}
        citations = [_label(x) for x in (row.get("citations") or []) if _label(x)]
        total += len(citations); valid += sum(x in retrieved for x in citations)
    result = _ratio(valid, total); result["interpretation"] = "identifier-resolution check only; not semantic citation accuracy"
    return result


def blank_human_review() -> Dict[str, Any]:
    return {key: {"value": None, "numerator": None, "denominator": 0, "eligible": 0, "excluded": 0,
                  "status": "NOT MEASURED", "reason": "No completed human-review evidence was supplied."}
            for key in ("hallucination_rate", "semantic_citation_accuracy", "response_correctness", "response_usefulness")}


def unavailable_operational_metrics() -> Dict[str, Any]:
    reasons = {"first_contact_resolution": "Local routes do not establish verified resolution and follow-up outcomes.",
               "first_response_time": "Pipeline latency is not arrival-to-customer-response time.",
               "csat": "No customer ratings attributable to this run were collected.",
               "availability": "A local pipeline run is not an availability study.",
               "repeat_contact_rate": "No linked one-week follow-up observation and baseline were supplied."}
    return {key: {"value": None, "numerator": None, "denominator": 0, "eligible": 0, "excluded": 0,
                  "status": "NOT MEASURED", "reason": reason} for key, reason in reasons.items()}


def aggregate_metrics(records: List[Dict[str, Any]], tickets: List[Dict[str, Any]],
                      intent_label_map: Optional[Mapping[str, str]] = None, retrieval_k: int = 3) -> Dict[str, Any]:
    _paired(records, tickets, "aggregate metrics")
    predictions = [r.get("classification") or {} for r in records]
    expected_docs = [t.get("labels", {}).get("expected_doc_ids") if isinstance(t.get("labels"), Mapping) else None for t in tickets]
    expected_routes = [t.get("labels", {}).get("expected_route") if isinstance(t.get("labels"), Mapping) else None for t in tickets]
    return {"classification": calculate_classification_metrics(predictions, tickets, intent_label_map),
            "retrieval": calculate_retrieval_metrics([list(r.get("retrieved_doc_ids") or []) for r in records], expected_docs, retrieval_k),
            "routing": calculate_routing_metrics([r.get("predicted_route") for r in records], expected_routes),
            "guardrails": _guardrail_metrics(records), "operational": calculate_operational_metrics(records),
            "citation_id_validity": calculate_citation_id_validity(records), "human_evaluation": blank_human_review(),
            "business_operational": unavailable_operational_metrics()}


def _measurement(metric: Any) -> Dict[str, Any]:
    if not isinstance(metric, Mapping): return {"value": None, "denominator": 0, "eligible": 0, "excluded": 0}
    value = metric.get("value")
    result = {"value": value if isinstance(value, (int, float)) else None, "numerator": metric.get("numerator"),
              "denominator": metric.get("denominator", metric.get("eligible", 0)),
              "eligible": metric.get("eligible", metric.get("denominator", 0)), "excluded": metric.get("excluded", 0)}
    if metric.get("reason"): result["reason"] = metric["reason"]
    return result


def build_metric_assessments(metrics: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    c, r, route = metrics.get("classification", {}), metrics.get("retrieval", {}), metrics.get("routing", {})
    op, g = metrics.get("operational", {}), metrics.get("guardrails", {})
    h, business = metrics.get("human_evaluation", {}), metrics.get("business_operational", {})
    sources = {"intent_accuracy": c.get("intent", {}).get("accuracy"), "intent_macro_precision": c.get("intent", {}).get("macro_precision"),
        "intent_macro_recall": c.get("intent", {}).get("macro_recall"), "intent_macro_f1": c.get("intent", {}).get("macro_f1"),
        "urgency_accuracy": c.get("urgency", {}).get("accuracy"), "urgency_macro_precision": c.get("urgency", {}).get("macro_precision"),
        "urgency_macro_recall": c.get("urgency", {}).get("macro_recall"), "urgency_macro_f1": c.get("urgency", {}).get("macro_f1"),
        **{f"retrieval_recall_at_{k}": r.get(f"recall_at_{k}") for k in (1, 3, 5)},
        **{f"retrieval_precision_at_{k}": r.get(f"precision_at_{k}") for k in (1, 3, 5)}, "retrieval_mrr": r.get("mrr"),
        "routing_accuracy": route.get("accuracy"), "auto_response_precision": route.get("auto_respond_precision"),
        "auto_response_recall": route.get("auto_respond_recall"), "automation_rate": route.get("auto_response_rate"),
        "escalation_rate": route.get("escalation_rate"), "guardrail_coverage": g.get("coverage"),
        "processing_failure_rate": op.get("processing_failure_rate"), "decision_log_coverage": op.get("decision_log_coverage"),
        "pipeline_latency_p50": {**(op.get("latency_seconds") or {}), "value": (op.get("latency_seconds") or {}).get("p50")},
        "pipeline_latency_p95": {**(op.get("latency_seconds") or {}), "value": (op.get("latency_seconds") or {}).get("p95")},
        "confidence_calibration_error": c.get("calibration", {}).get("expected_calibration_error"),
        "citation_id_validity": metrics.get("citation_id_validity"),
        "private_data_occurrences": g.get("private_data_occurrences_in_released_responses"),
        **{key: h.get(key) for key in ("hallucination_rate", "semantic_citation_accuracy", "response_correctness", "response_usefulness")},
        **{key: business.get(key) for key in ("first_contact_resolution", "first_response_time", "csat", "availability", "repeat_contact_rate")},
        "cross_group_quality_difference": None}
    assessments = {}
    for key, registry in METRIC_REGISTRY.items():
        measured = _measurement(sources.get(key))
        measured.update({"status": metric_status(measured["value"], registry.get("target"), denominator=measured["denominator"]),
                         "measurement_type": registry["measurement_type"]})
        assessments[key] = measured
    return assessments
