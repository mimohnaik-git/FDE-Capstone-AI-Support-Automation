"""Suite-wide isolation from developer-specific generation-provider settings."""

import os

import pytest


# Root conftest modules load before pytest imports test modules. Establish the
# deterministic provider before any test import can initialize src.config.settings.
os.environ["GENERATION_PROVIDER"] = "offline"

from src.config import settings  # noqa: E402


@pytest.fixture(autouse=True)
def deterministic_default_generation_provider(monkeypatch):
    """Use the committed offline default unless a test injects a provider explicitly."""
    monkeypatch.setenv("GENERATION_PROVIDER", "offline")
    monkeypatch.setattr(settings, "GENERATION_PROVIDER", "offline")
