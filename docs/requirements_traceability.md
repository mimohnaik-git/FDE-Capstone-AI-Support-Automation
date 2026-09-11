# Requirements traceability

## Stage 12 validation-readiness traceability

| Requirement | Frozen implementation/evidence | Stage 12 result |
|---|---|---|
| Development and validation evidence remain separate | Calibration accepts only development; classifier training rejects protected validation/final filenames | PASS |
| Validation is not loaded during readiness review | Harness preflight performs path/configuration checks without dataset reads | PASS |
| Thresholds are evidence-gated | Stage 11 retained `0.80` / `0.30`; the manifest asserts those exact values | PASS |
| Evaluation is dataset-size agnostic | Frozen command has no limit or expected-count argument | PASS |
| Evaluation evidence is reproducible | Schema, development data, prompt, corpus, code, and configuration are fingerprinted | PASS |
| Partial runs remain distinguishable | Atomic checkpoints remain `RUNNING` / `partial_run`; each restart gets a new run and decision database | PASS |

Development tuning is complete and validation remains untouched. Post-validation
tuning invalidates the validation claim unless a new isolated validation set is
introduced and the policy is frozen again before it is inspected.

## Stage 19 monitoring and governance traceability

| Requirement | Implementation/evidence | Status |
|---|---|---|
| Prometheus metrics endpoint | `src/monitoring.py`; FastAPI `GET /metrics` | IMPLEMENTED / locally tested |
| Tickets by channel/outcome | Bounded labels on `support_tickets_processed_total` | IMPLEMENTED |
| Automation/escalation rate | Process-lifetime gauges and counter-based PromQL | IMPLEMENTED |
| Processing latency P50/P95 | Histogram plus rolling 1,024-request P50/P95 gauges | IMPLEMENTED; production SLO not measured |
| Guardrail and failure visibility | Controlled reason/category counters | IMPLEMENTED |
| Confidence distribution | Fixed-bucket histogram without ticket identifiers | IMPLEMENTED |
| Sensitive-data-safe metrics | No body, customer, response, passage, citation, or ticket-ID labels | TESTED |
| Kill switch | Per-request file check; audited `KILL_SWITCH_ENABLED` escalation | IMPLEMENTED / TESTED |
| Incident response and risk register | `docs/governance.md` | DOCUMENTED |
| Operational availability/alerts | Requires deployed observation and alert-delivery exercise | NOT MEASURED |

Stage 19 changes are confined to the operational API, new operational modules,
monitoring configuration, tests, and documentation. Frozen V1 fingerprints and all
validation/human-review evidence remain unchanged.
# Stage 21 repository reproducibility evidence

| Criterion | Implementation evidence | Verification |
|---|---|---|
| A1 — Clean Checkout | Root `README.md`, placeholder-only `.env.example`, `.gitignore`, and `scripts/clean_checkout_smoke.py` document and exercise the credential-free offline path without developer-specific paths. | Fresh repository checkout: dependency installation, application/evaluation imports, `/health`, complete tests, and `pip check`. |
| A12 — Tests | `.github/workflows/ci.yml` installs Python 3.12 dependencies, runs `pip check`, executes the clean-checkout smoke check, and runs the full suite using the README's single test command. | `python -m pytest` from repository root. |
