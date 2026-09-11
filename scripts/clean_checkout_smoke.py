"""Credential-free clean-checkout smoke check; never opens evaluation datasets."""

from __future__ import annotations

import os


def main() -> None:
    os.environ["GENERATION_PROVIDER"] = "offline"
    os.environ.pop("OPENROUTER_API_KEY", None)

    from fastapi.testclient import TestClient

    import evaluation.harness  # noqa: F401
    import evaluation.metrics  # noqa: F401
    import evaluation.report  # noqa: F401
    from src.api import app

    response = TestClient(app).get("/health")
    if response.status_code != 200 or response.json().get("status") != "healthy":
        raise RuntimeError("Offline application health check failed")
    print("clean-checkout smoke: PASS (offline, credential-free, no dataset loaded)")


if __name__ == "__main__":
    main()
