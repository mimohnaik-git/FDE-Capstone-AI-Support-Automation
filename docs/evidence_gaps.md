# Evidence Gaps

`Evidence not available` means the project has no qualifying measurement. The labels
below describe when the gap should be closed; they do not imply that missing evidence passed.

## Required before submission

| Gap | Current evidence | Required action |
|---|---|---|
| Owner approval of reconciled submission claims | Stage 23 corrected the final-report and video inputs to HUMAN DEVELOPMENT EVALUATION hallucination 2% (1/50), semantic citation accuracy 98% (49/50), and validation hallucination NOT MEASURED. | Project owner must verify these claims and personally finalize evaluation/business interpretation and reflection. Do not rewrite historical evaluation artifacts. |
| Project-owner interpretation and reflection | `AGENTS.md` reserves evaluation interpretation, business conclusions, discovery problem statement, and reflection for the project owner. | Project owner must review and author/approve those assessed sections. AI-generated defense material cannot substitute for that work. |
| Hosted CI run | CI configuration exists and local/fresh-clone suites pass, but no GitHub remote or hosted workflow run exists. | Connect the intended repository only with owner authorization and obtain a successful GitHub Actions run, or disclose that CI is configured but not observed. |
| Submission evidence packaging decision | Immutable evaluation JSON contains original absolute execution paths, and SQLite decision evidence is locally preserved but intentionally ignored as runtime state. Stage 23 recorded hashes but did not package the databases. | Decide which decision databases the submission requires and how Git history will be supplied; do not edit frozen Stage 13/16 artifacts. |
| Final package production | Stage 23 audited the required structure and corrected `04_Source_Code`, but the MP4/link, 20–30 page PDF, completed workbook exports, updated effort-log PDF, owner filename, and final archive are missing. | Complete the owner-controlled artifacts, assemble the exact four-folder archive, and inspect its contents without rerunning validation. |

## Recommended

| Gap | Current evidence | Recommendation |
|---|---|---|
| Human-review disagreement adjudication | Twenty-six of 50 samples have at least one ordinal correctness/usefulness disagreement; no binary grounding disagreement exists. | Conduct a documented adjudication if the Evaluation Framework or assessor expects final consensus scores; preserve original ratings. |
| Validation subgroup power | Enterprise n=8 and non-fluent n=19 were below the registered minimum n=20. | Collect a new governed dataset for subgroup evidence. Do not reuse or tune against existing validation. |
| Cross-group human quality | Governance target `<5 percentage points` is NOT MEASURED. | Run appropriately powered human review stratified by explicit groups on new evidence. |
| Dependency locking | Several requirements use lower bounds, so future resolution may change. | Produce a tested lock/constraints file from a clean environment without altering V1 behavior. |
| CI portability observation | Local Windows and fresh-clone tests passed; Ubuntu GitHub Actions has not run. | Observe the configured Linux CI and document any platform-specific failures truthfully. |
| V2 answerability research | Stage 20 calibration improved but no strictly safe non-zero policy existed. | Continue only on development/new data with an inference-available answerability signal; retain V1 until a new validation cycle is authorized. |
| End-to-end generated-response validation | V1 validation released zero responses, so guardrail coverage, citation validity, and response quality were ineligible. | Evaluate a future version on a new frozen validation set only after safe automation is demonstrated on development evidence. |

## Production-only

| Gap | Why current evidence is insufficient | Required production evidence |
|---|---|---|
| Availability ≥99.5% | Local runs and `/health` are not an availability study. | Deployed observation window with defined service boundary and downtime accounting. |
| First substantive response time | Pipeline latency is not ticket-arrival-to-customer-response time. | Timestamped production workflow measurement. |
| FCR ≥60% and repeat contacts | Routing outcomes do not establish resolution or later contact. | Linked outcome/follow-up data with a governed baseline. |
| CSAT ≥4.0/5 | No customer ratings attributable to system responses exist. | Production or controlled-pilot survey evidence. |
| Load and latency under concurrency | Validation P95 0.0915 seconds was a local sequential pipeline measurement. | Representative load test covering API, retrieval, provider, database, and tail latency. |
| Alert delivery and response | Metrics/dashboard configuration and local tests do not prove paging. | Alert thresholds, routed notification test, acknowledgement and response-time exercise. |
| Backup and recovery | SQLite recovery behavior is documented but not rehearsed. | Restore drill with RPO/RTO, integrity, WAL handling, and decision reconciliation. |
| Authentication, authorization, and abuse controls | FastAPI exposes no measured production access-control boundary. | Identity, authorization, TLS, rate limiting, request limits, and security testing. |
| Live-provider reliability/cost | Offline mode was the default evidence path. | Provider SLA/error/latency/cost observation with approved retry and fallback policy. |
| Named accountable operators | Governance defines roles but explicitly says named individuals are unavailable. | Assign trained System Owner, on-call, Support Operations, Security, ML/Evaluation, and Platform owners. |
| Kill-switch operational performance | Synthetic tests prove logic, not fleet-wide propagation or human response time. | Rehearsed exercise across every instance, including in-flight traffic and audit failure. |
