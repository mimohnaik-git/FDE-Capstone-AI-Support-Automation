# Technical Defense Q&A

These answers distinguish observed evidence from interpretation. They are a defense
aid, not a substitute for the project owner's own assessed conclusions.

## Why this architecture instead of a chatbot?

The specification requires separate ingestion, classification, retrieval, routing,
generation, guardrails, logging, and evaluation stages. The implementation keeps
those boundaries explicit so safety decisions are deterministic and auditable rather
than delegated to an opaque language-model call. Tests can inject failure at each
stage and prove that failure becomes escalation rather than a customer response.

## Why retrieval-augmented generation?

Customer-facing claims must come from the supplied authoritative CloudServe corpus.
Retrieval supplies identifiable document and chunk IDs, while generation is allowed
to use only that context and guardrails verify grounding and citation identity. This
reduces unsupported generation risk, but does not guarantee semantic correctness;
that is why semantic citation accuracy required human review.

## Why MiniLM?

MiniLM was retained after a development comparison. The recorded architecture
evidence reports Recall@3 of 0.888, approximately 90.9 MB of parameters, and 25.00 ms
experiment P95. BGE-small and E5-small were roughly 133.4 MB and about twice as slow,
without beating MiniLM on the primary Recall@3 criterion. Stage 16 later measured
validation Recall@3 of 87.7% and MRR of 92.8%.

## Why NumPy exact cosine instead of Chroma?

The corpus contains 29 documents and 170 chunks, so exact matrix ranking is small and
deterministic. Chroma introduced a native Windows access violation/version burden in
development. NumPy avoided a database service, index migration, and approximate
ranking variability. The trade-off is that it is not designed for a large or rapidly
changing corpus; that would justify revisiting a vector database.

## Why SQLite?

SQLite gives durable local decision records, transactions, simple reconciliation,
and no service dependency for the capstone scale. Validation recorded all 80 decisions
and reconciled them. It is replaceable at the logging boundary, but production scale
would require evidence for concurrency, backup, recovery, retention, and potentially
a managed database.

## Why direct Python instead of LangGraph orchestration?

The required pipeline is linear with explicit fail-closed branches. Direct Python
keeps control flow visible, deterministic, and easy to unit test. Adding a graph
framework would not improve measured quality here and would add dependency and state
complexity. The stages remain modular, so adopting a workflow engine later would not
require changing their core contracts.

## Can the LLM provider, embedding model, or database be changed?

Technically yes, but not silently. Generation uses a provider boundary with offline
and OpenRouter-compatible adapters. Retrieval accepts a configured embedding model,
and logging is isolated behind the decision-store interface. Any production change
to the frozen model, corpus processing, provider behavior, or logging semantics must
be versioned, retested, and re-evaluated; flexibility is not permission to bypass the
freeze.

## Does the evaluator assume 80 or the hidden 120 tickets?

No. The harness iterates the supplied dataset and computes denominators from actual
eligible records. Tests cover arbitrary counts and wrapper formats. The validation
set happened to contain 80 tickets. The project materials say the hidden final set is
expected to contain 120, but 120 is not hard-coded.

## Why are the thresholds 0.80 and 0.30?

They are the frozen V1 classification and retrieval thresholds. Stage 11 tested a
compact development grid on grouped, held-out predictions. No alternative policy met
the established strict safety constraints with useful automation, so the existing
defaults were retained rather than tuned against validation. They are evidence-gated
defaults, not a claim that 0.80 is well calibrated.

## Is classifier confidence calibrated?

No for frozen V1. Stage 16 validation expected calibration error was 42.3%, failing
the ≤5-point governance target. Stage 20 showed that an isolated isotonic V2 candidate
could reduce development-evaluation ECE from 63.48% to 3.34%, but the associated
routing policies did not satisfy strict false-auto safety. That candidate was rejected
and never validated.

## Why did V1 automate 0% of validation tickets?

The classifier is severely under-confident relative to its observed intent accuracy,
so predictions did not clear the 0.80 routing threshold. V1 therefore escalated all
80 validation tickets. This achieved fail-closed behavior and zero processing
failures on the technical rerun, but routing accuracy was only 40%, auto-response
recall was 0%, and the 100% escalation rate failed the ≤30% target.

## Why was V2 rejected if its calibration improved?

Calibration improvement was insufficient for safe routing. The best development
policy at 0.70/0.40 had 77% routing accuracy and 69% automation, but it produced 18
false auto-responses. Safety was not redefined to make that result pass. V2 remains a
rejected development experiment and did not change V1.

## Can the project claim a 2% hallucination rate?

Only for the **HUMAN DEVELOPMENT EVALUATION** sample of 50 generated candidates—not
for validation or production. Two independent reviewers both marked one unsupported
candidate; raw unsupported-claim agreement was 50/50. Validation released zero
responses, so validation hallucination rate was NOT MEASURED.

## Is citation accuracy automated?

Citation-ID validity is automated, but semantic citation accuracy is not. Exact ID
checks prove that a citation resolves to retrieved evidence; they cannot prove the
passage supports the accompanying claim. Two-reviewer development evidence measured
semantic citation accuracy at 98% (49/50), while validation citation metrics were NOT
MEASURED because no responses were released.

## What did human reviewers say about answer quality?

Across 100 reviewer ratings for 50 development candidates, mean correctness was
3.74/5 and usefulness 2.87/5. Correctness and usefulness quadratic weighted kappas
were 0.712 and 0.941. The evidence supports concern about action-oriented usefulness,
but it does not establish validation or production response quality.

## What did fairness analysis show?

Groups used only explicit tier and language-fluency fields plus deterministic text
length; no protected attribute was inferred. Development showed lower Recall@3 for
non-fluent tickets than fluent tickets (0.799 versus 0.874). Validation enterprise
(n=8) and non-fluent (n=19) groups were below the minimum group size of 20 and were
reported NOT MEASURED. Validation short/long urgency accuracy differed materially
(0.279 versus 0.595), but automated gaps do not establish customer-outcome fairness.
The required cross-group human quality metric remains NOT MEASURED.

## Why was validation run twice?

Attempt 1 encountered a documented Hugging Face cache/token-path `PermissionError`.
Its artifacts and hashes were preserved. The same failure was diagnosed outside
validation, classified as infrastructure-only, and repaired by copying the same
MiniLM weights to a workspace-readable offline cache. A real synthetic retrieval
preflight then passed with the frozen fingerprint unchanged. The project owner
authorized exactly one disclosed technical rerun. Attempt 2 used the same dataset
fingerprint and frozen implementation; no tuning occurred between attempts.

## How does failure handling work?

Malformed input, invalid classifier/retriever/provider output, timeout, rate limit,
provider outage, missing evidence, guardrail failure, and logging failure all have
controlled paths. The orchestrator suppresses customer release and escalates. The
reliability suite also proves batch continuation, atomic checkpoints, bounded write
retries, and audit uncertainty handling.

## What makes audit logging defensible?

Each terminal event receives a run ID, input index, decision ID where persistence
succeeds, action, reason, model/config metadata, retrieved source identifiers, and
guardrail state without storing full secret-bearing content. Reconciliation compares
source, evaluated, terminal, and decision counts. The technical validation rerun had
80/80/80/80 and 100% decision coverage.

## What does monitoring prove?

The API exports Prometheus-compatible counters, bounded labels, confidence buckets,
latency histograms, rolling P50/P95, failures, and guardrail blocks. Tests prove the
endpoint and absence of sensitive labels. Grafana/Prometheus configuration exists.
This proves instrumentation behavior locally, not service availability, alert
delivery, retention, or production SLO compliance.

## What are the largest remaining production gaps?

No evidence establishes authentication/authorization, abuse controls, deployed
availability, load behavior, provider reliability, alert delivery, backup recovery,
FCR, first-response time, CSAT, or repeat-contact outcomes. Named operational owners
and a rehearsed incident/kill-switch process are also required before customer traffic.

