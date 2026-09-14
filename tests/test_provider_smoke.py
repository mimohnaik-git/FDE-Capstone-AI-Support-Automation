from pathlib import Path

import pytest

from scripts.live_provider_generation_smoke import (
    HISTORICAL_OUTPUT_PATHS,
    _execution_failed,
    _sanitize_error_text,
    _validated_output_path,
)
from src.config import settings


def test_smoke_error_sanitizer_redacts_generic_and_configured_secrets(monkeypatch):
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "configured-private-value")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "gsk_private123456789")
    source = (
        "Authorization: Bearer abcdefghijklmnop "
        "api_key=configured-private-value "
        "url=https://example.invalid/?access_token=query-private "
        "gsk_private123456789"
    )
    sanitized = _sanitize_error_text(source)
    for secret in (
        "abcdefghijklmnop", "configured-private-value", "query-private",
        "gsk_private123456789",
    ):
        assert secret not in sanitized


def test_safe_guardrail_rejection_is_not_smoke_execution_failure():
    result = {
        "live_provider": "groq",
        "blockers": [],
        "cases": [{"providers": {"groq": {
            "failure_reason": None,
            "final_generation_acceptance": "REJECTED",
        }}}],
    }
    assert _execution_failed(result) is False


@pytest.mark.parametrize("failure_reason", ["PROVIDER_TIMEOUT", "PROVIDER_ERROR"])
def test_provider_transport_or_parsing_failure_sets_failed_exit_semantics(failure_reason):
    result = {
        "live_provider": "openrouter",
        "blockers": [],
        "cases": [{"providers": {"openrouter": {"failure_reason": failure_reason}}}],
    }
    assert _execution_failed(result) is True


def test_historical_smoke_outputs_cannot_be_overwritten():
    protected = next(iter(HISTORICAL_OUTPUT_PATHS))
    with pytest.raises(ValueError, match="preserved historical"):
        _validated_output_path(Path(protected))
