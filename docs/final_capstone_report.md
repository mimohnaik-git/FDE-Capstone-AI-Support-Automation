# CloudServe Support Automation Capstone Report Draft

**Author:** Forward Deployed Engineer  
**Client:** CloudServe Solutions  
**Evidence cut-off:** 12 September 2026
**Status:** Owner-reviewed submission draft requiring PDF production

This draft records the implemented system and the evidence currently available. It is
not yet the required 20–30 page submission PDF. Discovery baselines are historical
properties of the supplied development dataset; they are not outcomes caused by this
system.

## Executive summary

CloudServe supplied 500 development tickets, 80 validation tickets, 29 reviewed
knowledge-base articles, and stakeholder materials. Discovery analysis of the
development data recorded 71.4% document answerability, 43.8% historical first-contact
resolution, and mean historical CSAT of 2.97/5. Those FCR and CSAT values are discovery
baselines only. System-attributable FCR, CSAT, first-response time, availability, load
performance, alert delivery, and other business outcomes have **NOT BEEN MEASURED**.

Frozen V1 is a fail-closed, documentation-grounded support pipeline. On the authorized
technical validation rerun it processed and reconciled 80/80 tickets with no processing
failures and 100% decision-log coverage. It released no automatic responses: automation
was 0% and escalation was 100%. This is safe behavior, but it fails the documented
escalation target and is the most important limitation of V1.

## Problem and discovery context

The supplied stakeholder and development-ticket evidence describes long response
delays, weak discovery of relevant documentation, and context-poor escalations. The
project therefore implements ingestion, intent and urgency classification, semantic
retrieval over the authoritative corpus, deterministic routing, grounded generation,
blocking guardrails, structured escalation, and persistent decision logging.

The project owner, Mimoh Naik, completed review and approved the final
interpretation and deployment recommendation on 12 September 2026. The approved
recommendation is a **limited supervised pilot**; V1 is **not production-ready** and
safety takes priority over automation.

## Architecture and implementation

The production V1 path uses explicit Python components coordinated by
`SupportPipelineOrchestrator`:

```text
Ticket -> normalize -> classify -> retrieve -> route
                                      |          |
                                      |          +-> safe escalation
                                      +-> generate -> guardrails -> release or escalation
                                                            |
                                                            +-> SQLite decision log
```

- Four-channel ingestion supports email, live chat, documentation comments, and
  community forum inputs.
- Classification uses deterministic TF-IDF/logistic-regression models
  with explicit urgency logic and confidence output.
- Retrieval uses exact cosine search over locally loaded
  `sentence-transformers/all-MiniLM-L6-v2` embeddings and NumPy. V1 does not use
  ChromaDB or a BM25 fallback.
- Routing is deterministic with frozen classification and retrieval thresholds of
  0.80 and 0.30. High-risk and must-not-auto-respond cases fail closed.
- Generation is evidence constrained; exact citations must resolve to retrieved
  document/chunk identifiers.
- Guardrails can block private data, prompt injection effects, unsupported
  commitments, citation failures, and grounding failures.
- Every terminal decision is written to SQLite when the decision store is available.
- FastAPI exposes `/health`, `/tickets/process`, and Prometheus-compatible `/metrics`.
  A deterministic kill switch suppresses customer release while retaining escalation
  and audit logging.

The frozen V1 production fingerprint is
`ddf89e82e7340a0257ee0c2ae1ce340612070545bc04f559e1e4c3ad733f59c1`.

## Evaluation method and evidence classes

Development tuning, validation, human development review, and operational evidence are
kept separate. Validation attempt 1 failed because the embedding cache/token path was
not readable. The failure artifacts were preserved. After infrastructure-only
remediation loaded the same frozen model and left the production fingerprint unchanged,
the project owner authorized exactly one disclosed technical rerun. No tuning occurred
between the attempts.

The supplied validation evidence contains 80 tickets. The evaluation harness accepts
arbitrary input sizes and does not hard-code a ticket count; the Build Specification
expects a hidden final assessment of up to 120 tickets. That hidden assessment has not
been accessed or simulated in this report.

### Authorized technical validation rerun

Evidence classification: **VALIDATION**. Denominators are shown explicitly.

| Metric | Result | Population/status |
|---|---:|---|
| Source / evaluated / terminal / decisions | 80 / 80 / 80 / 80 | Reconciliation PASS |
| Intent accuracy / macro precision / recall / F1 | 100% / 100% / 100% / 100% | 80 tickets; PASS |
| Urgency accuracy | 42.5% | 80 tickets; FAIL |
| Urgency macro F1 | 41.4% | 80 tickets; FAIL |
| Retrieval Recall@1 / @3 / @5 | 76.4% / 87.7% / 88.7% | 53 eligible tickets |
| Retrieval Precision@1 / @3 / @5 | 90.6% / 36.8% / 25.6% | 53 eligible tickets |
| Retrieval MRR | 92.8% | 53 eligible tickets |
| Routing accuracy | 40.0% | 80 tickets; FAIL |
| Automation / escalation | 0.0% / 100.0% | 80 tickets; escalation FAIL |
| Auto-response precision | NOT MEASURED | No predicted automatic responses |
| Auto-response recall | 0.0% | Eligible routing population; FAIL |
| Processing failure rate | 0.0% | 80 tickets; PASS |
| Decision-log coverage | 100.0% | 80 terminal decisions; PASS |
| Pipeline latency P50 / P95 | 0.0502s / 0.0915s | 80 local sequential runs; PASS |
| Calibration error | 42.3% | 80 tickets; FAIL |

Pipeline latency is not customer first-response time and does not establish deployed
load performance or availability. Validation released zero responses, so validation
hallucination, semantic citation accuracy, response correctness/usefulness, citation-ID
validity on released responses, private-data release rate, and guardrail coverage were
**NOT MEASURED** or ineligible. Citation-ID validity is not semantic citation accuracy.

### Human development evaluation

Evidence classification: **HUMAN DEVELOPMENT EVALUATION**, not validation and not
production. Two independent reviewers assessed 50 legitimate development response
candidates.

| Metric | Result | Population/status |
|---|---:|---|
| Hallucination rate | 2% (1/50) | PASS against <=5% target |
| Semantic citation accuracy | 98% (49/50) | PASS against >=95% target |
| Response correctness | 3.74/5 | 100 reviewer ratings; no formal target |
| Response usefulness | 2.87/5 | 100 reviewer ratings; no formal target |

The hallucination and citation figures cannot be generalized to validation automatic
responses because V1 released none. Twenty-six samples had at least one ordinal rating
disagreement and were not adjudicated.

## Fairness and governance

Fairness analysis used only explicit customer-tier and language-fluency fields plus a
deterministic short/long text rule. It did not infer protected attributes. Validation
enterprise (n=8) and non-fluent (n=19) groups were below the registered minimum n=20 and
were reported **NOT MEASURED**. Cross-group human response-quality evidence remains
**NOT MEASURED**.

The repository contains a risk register, incident-response procedure, kill-switch
policy, provider-outage and audit-log failure handling, monitoring expectations, and
rollback/recovery guidance. These are documented and locally tested controls, not proof
of production availability, alert performance, recovery times, or operator readiness.

## V2 development experiment

Stage 20 used grouped development-only splits and did not load validation. Isotonic
calibration improved development evaluation calibration error from 63.48% to 3.34%,
but no evaluated routing policy achieved the required zero-false-auto safety condition.
The best observed policy still produced 18 false auto-responses. V2 was therefore
**REJECTED** and was never validated or promoted. V1 remains frozen.

## Reproducibility and limitations

The repository has a Git history, a documented clean setup, a local fresh-clone proof,
and a GitHub Actions workflow that runs dependency checks and the complete test suite.
Hosted GitHub Actions CI was observed **SUCCESS** on run `34683618597` for `main`
commit `1186641c253b5d6531f8dc0e739a015970e9dc37`. It covered checkout, Python 3.12,
dependency installation, `pip check`, the offline clean-checkout smoke check, and the
complete pytest suite. This is CI evidence, not a production availability study.

Material remaining gaps include the submission-ready PDF and video, operational outcome
studies, deployed security controls, alert delivery, load testing, backup/restore
rehearsal, and named operational owners.

## AI-use declaration and owner review

AI coding assistants supported repository inspection, implementation, testing,
evaluation utilities, and technical documentation. The confirmed tools are ChatGPT,
Codex in VS Code, and Claude. The owner corrected or rejected suggestions that conflicted
with evidence, safety, or project requirements, and retains final accountability.

**OWNER TARGET, NOT MEASURED RESULT:** 30% is the owner's minimum worthwhile future
automation target for a future pilot. It does not change frozen V1, whose validation
automation result remains 0%.
