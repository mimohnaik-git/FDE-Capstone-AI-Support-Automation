# CloudServe Support Automation

This repository contains a Python 3.12 support-ticket pipeline with deterministic
routing, documentation retrieval, grounded generation, guardrails, decision
logging, a FastAPI interface, Prometheus metrics, and unattended evaluation.

## Setup

Run every command from the repository root. Python 3.12 is the supported and CI-tested version.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS/Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

`.env.example` contains placeholders and safe defaults only. Keep
`GENERATION_PROVIDER=offline` for credential-free operation. To use the optional
OpenRouter adapter, set `GENERATION_PROVIDER=openrouter` and provide
`OPENROUTER_API_KEY` only in the untracked `.env` or process environment. Never
commit credentials.

The semantic retriever uses `sentence-transformers/all-MiniLM-L6-v2`. Normal first
use may download that public model. Fully disconnected operation requires the same
weights to be provisioned in a readable Hugging Face cache in advance; provider
credentials are not required.

## API and operational controls

Start the API from the repository root:

```bash
python -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

- `GET /health` reports application-process health without claiming downstream availability.
- `GET /metrics` exposes bounded, Prometheus-compatible operational metrics.
- `POST /tickets/process` processes one ticket through the production orchestrator.

The deterministic automatic-response kill switch is the exact file
`storage/auto_response.disabled`. An authorized operator enables it without a
deployment by creating that file. While it exists, customer auto-responses are
suppressed, tickets escalate with `KILL_SWITCH_ENABLED`, and decision logging
continues. Delete only that file to restore normal handling. See
`docs/governance.md` for authorization and incident procedures.

## Verification

The single documented complete test command is:

```bash
python -m pytest
```

Dependency consistency and the credential-free checkout smoke check are available as:

```bash
python -m pip check
python scripts/clean_checkout_smoke.py
```

The smoke check imports the application and evaluation tooling and calls `/health`;
it does not load validation data or initialize the embedding model.

## Evaluation

Run unattended evaluation with an explicitly classified dataset role:

```bash
python -m evaluation.harness --input data/raw/development_tickets.json --output evaluation/results/local-development.json --dataset-role development
```

The harness accepts arbitrary dataset sizes and writes JSON, Markdown, and a
run-specific decision database. Validation execution is governed by the frozen
evaluation procedure and must not be used for development tuning.
