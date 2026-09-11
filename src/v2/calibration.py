"""Leakage-safe probability calibration for the development-only V2 candidate."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedGroupKFold

from src.classify import RANDOM_SEED, _intent_pipeline, _urgency_pipeline, text_group, ticket_text

CALIBRATION_VERSION = "grouped-calibration-v2.0.0"
PARTITION_NAMES = ("calibration", "policy_selection", "train", "train", "evaluation")


@dataclass(frozen=True)
class DevelopmentPartitions:
    train: List[Dict[str, Any]]
    calibration: List[Dict[str, Any]]
    policy_selection: List[Dict[str, Any]]
    evaluation: List[Dict[str, Any]]

    def manifest(self) -> Dict[str, Any]:
        populations = {"train": self.train, "calibration": self.calibration,
                       "policy_selection": self.policy_selection, "evaluation": self.evaluation}
        group_sets = {name: {text_group(t) for t in rows} for name, rows in populations.items()}
        overlaps = {f"{left}_{right}": len(group_sets[left] & group_sets[right])
                    for index, left in enumerate(populations)
                    for right in list(populations)[index + 1:]}
        assignment = sorted((str(t.get("ticket_id")), name)
                            for name, rows in populations.items() for t in rows)
        return {
            "strategy": "StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)",
            "group_key": "normalized subject + body (duplicate-text group)",
            "counts": {name: len(rows) for name, rows in populations.items()},
            "group_overlap": overlaps,
            "leakage_detected": any(overlaps.values()),
            "assignment_sha256": hashlib.sha256(
                json.dumps(assignment, separators=(",", ":")).encode("utf-8")).hexdigest(),
        }


def grouped_development_partitions(tickets: Sequence[Mapping[str, Any]],
                                   random_seed: int = RANDOM_SEED) -> DevelopmentPartitions:
    """Make four disjoint populations; final evaluation is never used for selection."""
    rows = [dict(ticket) for ticket in tickets]
    texts = [ticket_text(ticket) for ticket in rows]
    labels = [ticket["labels"]["intent"] for ticket in rows]
    groups = [text_group(ticket) for ticket in rows]
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=random_seed)
    buckets: Dict[str, List[Dict[str, Any]]] = {name: [] for name in set(PARTITION_NAMES)}
    seen: set[int] = set()
    for fold, (_, held_out) in enumerate(splitter.split(texts, labels, groups)):
        name = PARTITION_NAMES[fold]
        for index in held_out:
            if int(index) in seen:
                raise RuntimeError("A development row was assigned more than once")
            seen.add(int(index)); buckets[name].append(rows[int(index)])
    if len(seen) != len(rows):
        raise RuntimeError("Development partition assignment is incomplete")
    result = DevelopmentPartitions(train=buckets["train"], calibration=buckets["calibration"],
                                   policy_selection=buckets["policy_selection"],
                                   evaluation=buckets["evaluation"])
    if result.manifest()["leakage_detected"]:
        raise RuntimeError("Duplicate text groups leaked across development partitions")
    return result


def fit_candidate_models(train: Sequence[Mapping[str, Any]],
                         calibration: Sequence[Mapping[str, Any]], method: str) -> Dict[str, Any]:
    """Fit the unchanged base classifier on train, then calibrate on separate rows."""
    if method not in {"sigmoid", "isotonic"}:
        raise ValueError("Calibration method must be sigmoid or isotonic")
    train_text = [ticket_text(t) for t in train]
    base = _intent_pipeline().fit(train_text, [t["labels"]["intent"] for t in train])
    calibrated = CalibratedClassifierCV(estimator=base, method=method, cv="prefit")
    calibrated.fit([ticket_text(t) for t in calibration],
                   [t["labels"]["intent"] for t in calibration])
    urgency = _urgency_pipeline().fit(train_text, [t["labels"]["urgency"] for t in train])
    return {"intent_model": calibrated, "urgency_model": urgency, "method": method}


def predict_candidate(bundle: Mapping[str, Any], ticket: Mapping[str, Any]) -> Dict[str, Any]:
    text = ticket_text(ticket); model = bundle["intent_model"]
    probabilities = model.predict_proba([text])[0]
    ranked = sorted(zip(model.classes_, probabilities), key=lambda item: (-item[1], str(item[0])))
    urgency_model = bundle["urgency_model"]; urgency_probs = urgency_model.predict_proba([text])[0]
    urgency_index = int(np.argmax(urgency_probs))
    return {"intent": str(ranked[0][0]), "confidence": round(float(ranked[0][1]), 6),
            "urgency": str(urgency_model.classes_[urgency_index]),
            "urgency_confidence": round(float(urgency_probs[urgency_index]), 6),
            "model_version": f"tfidf-logreg-22-v1+{bundle['method']}-{CALIBRATION_VERSION}"}

