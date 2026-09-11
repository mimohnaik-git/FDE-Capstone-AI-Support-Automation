"""Stage 12 validation-readiness manifest without validation-data access."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

from evaluation.harness import EVALUATION_SCHEMA_VERSION, _atomic_write, preflight_evaluation
from src.classify import DEFAULT_TRAINING_DATA_PATH, MODEL_VERSION, training_data_sha256
from src.config import settings
from src.generate import PROMPT_PATH, PROMPT_VERSION
from src.retrieve import (
    CHUNKING_CONFIGS,
    DEFAULT_CORPUS_PATH,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_MIN_RELEVANCE_SCORE,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FREEZE_SCHEMA_VERSION = "1.0"
VALIDATION_DATASET = PROJECT_ROOT / "data" / "raw" / "validation_tickets.json"
VALIDATION_OUTPUT = PROJECT_ROOT / "evaluation" / "results" / "validation-final.json"
STAGE11_EVIDENCE = PROJECT_ROOT / "evaluation" / "results" / "stage11-calibration.json"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "evaluation" / "results" / "stage12-freeze-manifest.json"
VALIDATION_COMMAND = (
    "python -m evaluation.harness --input data/raw/validation_tickets.json "
    "--output evaluation/results/validation-final.json --dataset-role validation"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fingerprints(paths: Iterable[Path]) -> Dict[str, str]:
    return {path.relative_to(PROJECT_ROOT).as_posix(): _sha256(path) for path in paths}


def build_freeze_manifest(*, timestamp: str | None = None) -> Dict[str, Any]:
    """Build the freeze record; validation existence is checked but content is not read."""

    if settings.CLASSIFICATION_CONFIDENCE_THRESHOLD != 0.80:
        raise RuntimeError("Frozen classification threshold must remain 0.80")
    if settings.RETRIEVAL_ROUTING_THRESHOLD != 0.30:
        raise RuntimeError("Frozen retrieval threshold must remain 0.30")

    preflight = preflight_evaluation(
        str(VALIDATION_DATASET), str(VALIDATION_OUTPUT), dataset_role="validation"
    )
    if preflight["status"] != "READY":
        raise RuntimeError("Offline validation preflight is not ready")

    stage11 = json.loads(STAGE11_EVIDENCE.read_text(encoding="utf-8"))
    decision = stage11.get("selected_thresholds", {})
    if decision.get("status") != "CURRENT_DEFAULTS_RETAINED_INSUFFICIENT_EVIDENCE":
        raise RuntimeError("Stage 11 threshold decision is not the expected retained-default policy")

    production_files = [
        PROJECT_ROOT / "src" / name
        for name in (
            "classify.py", "config.py", "retrieve.py", "route.py", "generate.py",
            "guardrails.py", "orchestrator.py", "logging_store.py",
        )
    ]
    evaluation_files = [
        PROJECT_ROOT / "evaluation" / name
        for name in ("harness.py", "metrics.py", "report.py", "calibration.py", "freeze.py")
    ]
    fingerprints = _fingerprints(
        [*production_files, *evaluation_files, PROMPT_PATH, DEFAULT_CORPUS_PATH,
         DEFAULT_TRAINING_DATA_PATH, PROJECT_ROOT / ".env.example", PROJECT_ROOT / "requirements.txt"]
    )
    aggregate = hashlib.sha256(
        json.dumps(fingerprints, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    chunking = CHUNKING_CONFIGS["strategy_a"]

    return {
        "freeze_schema_version": FREEZE_SCHEMA_VERSION,
        "created_at_utc": timestamp or datetime.now(timezone.utc).isoformat(),
        "evidence_status": "FROZEN_DEVELOPMENT_POLICY_VALIDATION_NOT_RUN",
        "validation_executed": False,
        "frozen_configuration": {
            "classifier": {
                "implementation": "TF-IDF word/character features with one-vs-rest logistic regression",
                "model_version": MODEL_VERSION,
                "training_dataset_role": "development",
                "training_data_sha256": training_data_sha256(),
            },
            "retriever": {
                "implementation": "exact cosine over sentence-transformer embeddings",
                "configured_embedding_model": settings.EMBEDDING_MODEL,
                "effective_embedding_model": (
                    DEFAULT_EMBEDDING_MODEL
                    if settings.EMBEDDING_MODEL == "all-MiniLM-L6-v2"
                    else settings.EMBEDDING_MODEL
                ),
                "chunking": {
                    "strategy": chunking.name,
                    "max_chars": chunking.max_chars,
                    "overlap_chars": chunking.overlap_chars,
                },
                "top_k": settings.RETRIEVAL_TOP_K,
                "minimum_relevance_score": DEFAULT_MIN_RELEVANCE_SCORE,
            },
            "generation": {
                "prompt_version": PROMPT_VERSION,
                "prompt_sha256": _sha256(PROMPT_PATH),
                "configured_provider": settings.GENERATION_PROVIDER,
                "configured_model": settings.MODEL_NAME,
                "effective_offline_provider": "offline-grounded",
                "effective_offline_model": "deterministic-evidence-extract-v1",
            },
            "routing": {
                "classification_confidence_threshold": 0.80,
                "retrieval_threshold": 0.30,
            },
            "guardrails": {
                "policy": [
                    "generation validity", "private-data protection", "grounding",
                    "citation integrity", "prompt injection", "unsupported commitments",
                    "confidence floor",
                ],
                "version": "src/guardrails.py@sha256:" + fingerprints["src/guardrails.py"],
            },
            "evaluation_schema_version": EVALUATION_SCHEMA_VERSION,
        },
        "dataset_boundary": {
            "development_tuning_complete": True,
            "validation_dataset_path": "data/raw/validation_tickets.json",
            "validation_dataset_role": "VALIDATION",
            "validation_content_read_during_freeze": False,
            "validation_fingerprint": "DEFERRED_UNTIL_AUTHORIZED_EXECUTION",
            "validation_labels_available_to_training_or_initialization": False,
            "post_validation_tuning_policy": "Any tuning after validation invalidates the validation claim.",
        },
        "stage11_threshold_decision": {
            "evidence_classification": stage11.get("evidence_classification"),
            "evidence_sha256": _sha256(STAGE11_EVIDENCE),
            "status": decision.get("status"),
            "old_thresholds": decision.get("old_thresholds"),
            "new_thresholds": decision.get("new_thresholds"),
            "production_config_changed": decision.get("production_config_changed"),
        },
        "validation_command": VALIDATION_COMMAND,
        "preflight": preflight,
        "fingerprints": {"files": fingerprints, "aggregate_sha256": aggregate},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze Stage 12 validation-readiness evidence")
    parser.add_argument("--output", default=str(DEFAULT_MANIFEST_PATH))
    args = parser.parse_args()
    manifest = build_freeze_manifest()
    _atomic_write(Path(args.output).resolve(), manifest)
    print(json.dumps({"status": "FROZEN", "output": str(Path(args.output).resolve())}, indent=2))


if __name__ == "__main__":
    main()
