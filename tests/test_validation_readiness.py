import json
from pathlib import Path

import pytest

from evaluation.calibration import run_stage11
from evaluation.freeze import VALIDATION_COMMAND, build_freeze_manifest
from evaluation.harness import _fingerprint_file, preflight_evaluation
from src.classify import load_training_tickets
from src.config import settings


def test_training_and_calibration_reject_validation_paths_before_loading(monkeypatch, tmp_path):
    validation = tmp_path / "validation_tickets.json"
    validation.write_text("content must remain unread", encoding="utf-8")

    def forbidden(*_args, **_kwargs):
        raise AssertionError("validation content must not be read")

    monkeypatch.setattr(Path, "read_text", forbidden)
    with pytest.raises(ValueError, match="restricted from validation"):
        load_training_tickets(validation)
    with pytest.raises(ValueError, match="development dataset"):
        run_stage11(validation)


def test_validation_preflight_does_not_load_or_fingerprint_dataset(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("validation data loader/fingerprint must not run")

    monkeypatch.setattr("evaluation.harness._load_dataset", forbidden)
    monkeypatch.setattr("evaluation.harness._fingerprint_file", forbidden)
    result = preflight_evaluation(
        "data/raw/validation_tickets.json",
        "evaluation/results/validation-final.json",
        dataset_role="validation",
    )
    assert result["dataset_content_read"] is False
    assert result["dataset_ticket_count"] == "NOT_LOADED"
    assert result["dataset_fingerprint"] == "DEFERRED_UNTIL_AUTHORIZED_EXECUTION"


def test_frozen_thresholds_and_stage11_decision_remain_unchanged():
    manifest = build_freeze_manifest(timestamp="2026-09-10T00:00:00+00:00")
    routing = manifest["frozen_configuration"]["routing"]
    assert routing == {"classification_confidence_threshold": 0.80, "retrieval_threshold": 0.30}
    assert settings.CLASSIFICATION_CONFIDENCE_THRESHOLD == 0.80
    assert settings.RETRIEVAL_ROUTING_THRESHOLD == 0.30
    assert manifest["stage11_threshold_decision"]["new_thresholds"] is None
    assert manifest["validation_executed"] is False


def test_validation_command_is_dataset_size_agnostic():
    assert "--dataset-role validation" in VALIDATION_COMMAND
    assert "--limit" not in VALIDATION_COMMAND
    assert "120" not in VALIDATION_COMMAND


def test_dataset_fingerprinting_is_content_based(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps([{"ticket_id": "A"}]), encoding="utf-8")
    second.write_bytes(first.read_bytes())
    assert _fingerprint_file(first) == _fingerprint_file(second)
    second.write_text(json.dumps([{"ticket_id": "B"}]), encoding="utf-8")
    assert _fingerprint_file(first) != _fingerprint_file(second)


def test_manifest_does_not_claim_validation_fingerprint():
    manifest = build_freeze_manifest(timestamp="2026-09-10T00:00:00+00:00")
    boundary = manifest["dataset_boundary"]
    assert boundary["validation_content_read_during_freeze"] is False
    assert boundary["validation_fingerprint"] == "DEFERRED_UNTIL_AUTHORIZED_EXECUTION"
    assert manifest["preflight"]["live_credential_required"] is False
