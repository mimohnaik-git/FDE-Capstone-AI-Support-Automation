# Architecture Decision Records

These records describe implemented choices and their observed evidence. V1 remains
frozen; this document does not authorize an implementation change.

## ADR-001 — Explicit staged pipeline

- **Context:** The system must classify, retrieve, route, generate, guard, log, and
  evaluate decisions transparently.
- **Alternatives:** One end-to-end LLM prompt; framework-managed agent graph; explicit
  Python components.
- **Choice:** Explicit Python stages coordinated by `SupportPipelineOrchestrator`.
- **Evidence:** Unit tests exist per stage; reliability tests inject failures; Stage 9
  processed and reconciled 500 development tickets.
- **Trade-offs:** More interfaces and result schemas, but clearer auditability and
  fail-closed behavior. Direct Python provides fewer orchestration features than a
  workflow engine.

## ADR-002 — TF-IDF logistic regression classifier

- **Context:** Twenty-two intents plus urgency require deterministic local inference
  and measurable probabilities.
- **Alternatives:** Prompt-only LLM classification; larger transformer classifier;
  TF-IDF logistic regression.
- **Choice:** Word/character TF-IDF with one-vs-rest logistic regression.
- **Evidence:** Stage 16 intent accuracy and macro precision/recall/F1 were 100% on 80
  validation tickets.
- **Trade-offs:** Fast, inspectable, offline, and reproducible, but V1 confidence was
  severely under-calibrated and urgency accuracy was 42.5%.

## ADR-003 — MiniLM embeddings retained

- **Context:** Retrieval needs semantic matching with manageable local cost.
- **Alternatives:** Lexical retrieval, BGE-small, E5-small, MiniLM.
- **Choice:** `sentence-transformers/all-MiniLM-L6-v2`.
- **Evidence:** Development comparison favored MiniLM Recall@3/latency/resource use;
  Stage 16 validation Recall@3 was 87.7% and MRR 92.8%.
- **Trade-offs:** Strong small-corpus performance and offline inference after
  provisioning; initial model acquisition/cache management remains operational work.

## ADR-004 — NumPy exact cosine index

- **Context:** The authoritative corpus is 29 documents and 170 chunks.
- **Alternatives:** Chroma approximate/local vector store; hosted vector service;
  in-process exact matrix ranking.
- **Choice:** NumPy normalized embeddings and exact cosine ranking.
- **Evidence:** Chroma versions caused Windows native/compatibility problems. The
  selected design completed development and validation retrieval with deterministic
  rankings.
- **Trade-offs:** Minimal lifecycle and deterministic results at this scale; unsuitable
  without reassessment for a large, dynamic corpus or multi-process shared index.

## ADR-005 — Frozen multi-signal deterministic router

- **Context:** Automatic release must depend on confidence, intent risk, retrieval,
  failure state, and guardrails—not generated prose.
- **Alternatives:** LLM-decided routing; confidence-only routing; deterministic rules.
- **Choice:** Deterministic router with V1 thresholds 0.80 classification and 0.30
  retrieval plus high-risk/unanswerable rules.
- **Evidence:** Stage 11 could not identify a safe alternative, so defaults were
  retained. Stage 16 had zero automation and 100% escalation.
- **Trade-offs:** Fail-closed safety and reproducibility, but poor routing utility and
  failure of the escalation target because confidence is under-calibrated.

## ADR-006 — Provider-neutral grounded generation with offline default

- **Context:** Tests and default operation must not require secrets, while optional
  live-provider access remains possible.
- **Alternatives:** Mandatory hosted provider; deterministic offline extraction;
  provider protocol with both.
- **Choice:** Structured provider boundary, offline grounded provider by default, and
  optional OpenRouter-compatible provider.
- **Evidence:** Clean-checkout smoke and 342 tests run credential-free; provider
  timeout/rate-limit/unavailable cases fail closed.
- **Trade-offs:** Reproducible and inexpensive default; deterministic extraction had
  only 2.87/5 human-development usefulness and is not equivalent to fluent live LLM output.

## ADR-007 — Exact citations plus blocking guardrails

- **Context:** Grounding requires more than a plausible answer or document name.
- **Alternatives:** Free-form citations; post-hoc warning; exact structured citations
  and blocking checks.
- **Choice:** Validate exact document/chunk pairs and block private data, prompt
  injection, unsupported commitments, grounding failures, malformed output, and low confidence.
- **Evidence:** Adversarial tests prove blocking; human-development semantic citation
  accuracy was 98% across 50 candidates.
- **Trade-offs:** Strong fail-closed behavior may suppress useful responses. Exact ID
  validity still cannot replace human semantic review.

## ADR-008 — SQLite audit store

- **Context:** Every terminal decision must be persistent and reconcilable without a
  database service dependency.
- **Alternatives:** Files, PostgreSQL, SQLite.
- **Choice:** Transactional SQLite with minimized audit records and read-back/reconciliation.
- **Evidence:** Stage 16 recorded and reconciled 80/80 decisions; failure tests prove
  automation suppression when persistence is uncertain.
- **Trade-offs:** Simple and portable for capstone scale; production concurrency,
  replication, backup, retention, and recovery need separate evidence.

## ADR-009 — Dataset-size-agnostic, role-labelled evaluation

- **Context:** Project sources mention varying evaluation sizes, including an expected
  hidden size of 120, while leakage boundaries are mandatory.
- **Alternatives:** Fixed-size scripts; filename-inferred roles; explicit role and
  dynamic denominators.
- **Choice:** Explicit `development`/`validation`/`final` role, arbitrary input count,
  per-metric eligibility, atomic checkpoints, and run-specific decision logs.
- **Evidence:** Tests cover arbitrary counts; Stage 10 evaluated 500 development rows;
  Stage 16 evaluated 80 validation rows without a hard-coded count.
- **Trade-offs:** More provenance metadata, but missing evidence remains visible and
  cannot accidentally become PASS.

## ADR-010 — Preserve and disclose validation infrastructure incident

- **Context:** The first validation attempt failed because the Hugging Face cache/token
  path was inaccessible.
- **Alternatives:** Overwrite/rerun silently; abandon validation; preserve, diagnose on
  non-validation data, remediate infrastructure only, and seek authorization.
- **Choice:** Preserve attempt 1, reproduce without validation, copy identical MiniLM
  weights to a workspace cache, run a synthetic preflight, then perform one authorized rerun.
- **Evidence:** Stage 15 records identical source/destination model-tree hash, unchanged
  V1 fingerprint, and successful offline retrieval; Stage 16 reconciled 80/80.
- **Trade-offs:** Validation remains usable with full disclosure, but assessors must
  understand why attempt 2—not attempt 1—is the technical result.

## ADR-011 — Reject the V2 development candidate

- **Context:** V1 confidence was under-calibrated and generated answers were weakly actionable.
- **Alternatives:** Lower V1 thresholds; manually scale confidence; isolated calibrated
  V2; retain V1.
- **Choice:** Evaluate sigmoid/isotonic calibration and section-aware resolution
  selection in an isolated V2, then reject it.
- **Evidence:** Isotonic improved held-out development ECE from 63.48% to 3.34%, and
  resolution selection improved fixture coverage, but the best policy produced 18
  false auto-responses.
- **Trade-offs:** Useful development knowledge was retained without weakening safety or
  invalidating V1 validation; no automation improvement was deployed.

## ADR-012 — File-based operational kill switch

- **Context:** Operators need immediate suppression of auto-response without a deployment.
- **Alternatives:** Redeploy configuration; remote feature flag; repository-relative
  sentinel file.
- **Choice:** Check `storage/auto_response.disabled` on every API request and emit an
  auditable `KILL_SWITCH_ENABLED` escalation.
- **Evidence:** API tests prove response suppression, escalation, persistence, and
  unchanged normal behavior when disabled.
- **Trade-offs:** Deterministic and dependency-free on one host; distributed deployment
  would need a shared, access-controlled control plane.

