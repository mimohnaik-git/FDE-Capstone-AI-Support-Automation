# Stage 3 Prompt and Specification Library

## 1. Purpose and frozen boundary

This library distinguishes model prompts from requirements implemented in deterministic code. Frozen V1 has one evidenced runtime model prompt: the grounded generation prompt at version generation-v1.0.0. Classification, retrieval, routing, logging, and guardrail enforcement are not prompt-driven.

| Control | Value |
|---|---|
| Frozen V1 fingerprint | ddf89e82e7340a0257ee0c2ae1ce340612070545bc04f559e1e4c3ad733f59c1 |
| Frozen runtime prompt | prompts/build/generation_v1.txt |
| Runtime prompt version | generation-v1.0.0 |
| Deployment state | Limited supervised pilot; NOT production-ready |

This document records existing behavior only. It does not alter the prompt, model, thresholds, evaluation, or frozen implementation.

## 2. Prompt category register

| Identifier | Classification | Version | Purpose | Evidence and current status |
|---|---|---|---|---|
| GEN-01 | Runtime prompt | generation-v1.0.0 | Constrain provider-neutral customer-response generation to retrieved evidence and a strict JSON schema. | Active and frozen; prompts/build/generation_v1.txt loaded by src/generate.py. |
| HDE-01 | Evaluation prompt / human-review specification | Schema 1.0; protocol document is unversioned | Tell two independent human reviewers how to judge unsupported claims, citation support, correctness, and usefulness on 50 development responses. | Completed DEVELOPMENT evaluation; docs/human_evaluation_protocol.md, evaluation/human_review.py, and reviewer forms. It is not sent to the runtime model. |
| DEV-01 | Build/development prompt category | No evidenced artifact | AI-assisted engineering instructions may have been used during development, but no additional repository prompt is evidenced as a frozen runtime input. | No prompt text invented; AI tool use is recorded separately in docs/ai_use_declaration.md. |
| SPEC-INGEST | Direct-code logic / no prompt | Frozen V1 | Input schema validation and four-channel normalization. | Active in src/ingest.py. |
| SPEC-CLASSIFY | Direct-code logic / no prompt | tfidf-logreg-22-v1 | Intent and urgency classification with probability confidence. | Active in src/classify.py; not LLM-prompt based. |
| SPEC-RETRIEVE | Direct-code logic / no prompt | Frozen V1 | MiniLM embeddings and NumPy exact-cosine retrieval. | Active in src/retrieve.py; Chroma and BM25 are not frozen components. |
| SPEC-ROUTE | Direct-code logic / no prompt | Frozen V1 | Deterministic AUTO_RESPOND/ESCALATE decision using typed evidence and thresholds. | Active in src/route.py; no routing prompt exists. |
| SPEC-GUARD | Direct-code logic / no prompt | Frozen V1 | Blocking safety and validation rules after generation and at input. | Active in src/guardrails.py. |
| SPEC-LOG | Direct-code logic / no prompt | Frozen V1 | Persistent decision logging and audit metadata. | Active in src/logging_store.py. |
| SPEC-EVAL | Direct-code logic / no prompt | Frozen V1 | Unattended arbitrary-size metric computation and reporting. | Active in evaluation/harness.py, evaluation/metrics.py, and evaluation/report.py. |
| PR-01 | Deprecated / historical | 1.2 in prior workbook | A documented LLM classifier prompt. | No evidence that frozen V1 used it; superseded by SPEC-CLASSIFY and must not be cited as runtime behavior. |
| PR-02 | Deprecated / historical | 1.3 in prior workbook | An earlier prose generation prompt. | Superseded by the exact GEN-01 artifact. |
| PR-03 | Deprecated / historical | 1.1 in prior workbook | A proposed LLM grounding auditor. | No evidence it was used by frozen V1; grounding is direct-code validation. |
| PR-04 | Deprecated placeholder / historical | No completed runtime version | The original template referenced an injection prompt without supplying its content. | Completed below as an evidence-supported direct-code specification, not a fictitious prompt. |

## 3. Requirement to specification register

| Requirement | Specification | Inputs | Outputs | Acceptance evidence |
|---|---|---|---|---|
| FR-01 | DIRECT-CODE IMPLEMENTATION — NO RUNTIME PROMPT. Validate and normalize four ticket channels while preserving source. | Raw ticket payload | Normalized ticket or controlled failure | tests/test_ingest.py; A2 evidence |
| FR-02 | DIRECT-CODE IMPLEMENTATION — NO RUNTIME PROMPT. TF-IDF word/character logistic regression predicts intent, urgency, and confidence. | Normalized subject/body | Structured classification | tests/test_classify.py; validation fields present for 80/80 tickets; urgency quality remains weak |
| FR-03 | DIRECT-CODE IMPLEMENTATION — NO RUNTIME PROMPT. MiniLM plus NumPy exact cosine returns traceable ranked passages or no result. | Ticket text, top-k | Document/chunk IDs, passages, scores | tests/test_retrieve.py; authoritative retrieval metrics |
| FR-04 | DIRECT-CODE IMPLEMENTATION — NO RUNTIME PROMPT. Deterministic routing evaluates validity, risk, answerability, confidence, retrieval, guardrails, and failure state. | Classification, retrieval, validation/failure signals | AUTO_RESPOND or ESCALATE with reason | tests/test_route.py and tests/test_pipeline.py |
| FR-05 | GEN-01 constrains provider-neutral grounded generation and structured citations. | Untrusted ticket data plus retrieved documentation JSON and required schema | JSON with answer, citations, supported, uncertainty | tests/test_generate.py; DEVELOPMENT human evaluation only |
| FR-06 | GEN-01 requests evidence-only output; SPEC-GUARD independently enforces grounding. | Generated result plus retrieved evidence | PROCEED or BLOCK/ESCALATE audit | tests/test_generate.py and tests/test_guardrails.py |
| FR-07 | DIRECT-CODE IMPLEMENTATION — NO RUNTIME PROMPT. Detect private data and secrets and block. | Generated response | Guardrail result/reason | tests/test_guardrails.py and logging tests |
| FR-08 | GEN-01 states system authority and untrusted-data separation; PR-04/SPEC-GUARD enforces injection and disclosure blocking in code. | Ticket and generated response | Guardrail result/reason | injection, disclosure, and pipeline tests |
| FR-09 | GEN-01 forbids unsupported commitments; deterministic routing and SPEC-GUARD enforce high-risk/commitment escalation. | Intent, ticket, evidence, response | BLOCK/ESCALATE where unsafe | tests/test_route.py, tests/test_generate.py, tests/test_guardrails.py |
| FR-10 | DIRECT-CODE IMPLEMENTATION — NO RUNTIME PROMPT. Orchestration/API constructs structured escalation context; the generator cannot choose routing. | Pipeline evidence and route reason | Structured escalation payload | tests/test_pipeline.py, tests/test_api.py, and generator route-isolation test |
| FR-11 | DIRECT-CODE IMPLEMENTATION — NO RUNTIME PROMPT. Persist sanitized decision and prompt/specification metadata. | Pipeline decision data | SQLite decision record and ID | tests/test_logging_store.py and validation 80/80 log coverage |
| FR-12 | DIRECT-CODE IMPLEMENTATION — NO RUNTIME PROMPT. Compute/report metrics unattended for arbitrary input sizes. HDE-01 governs only the separate human DEVELOPMENT review. | Dataset and recorded outcomes | JSON/Markdown metrics | evaluation tests, authoritative artifacts, and hosted CI |

All FR-01–FR-12 are represented. A prompt association is claimed only for FR-05, the generation-facing part of FR-06, the defense-in-depth portion of FR-08/FR-09, and the separate human evaluation protocol.

## 4. Runtime prompt GEN-01

| Field | Value |
|---|---|
| Name and purpose | Grounded customer-response generation |
| Classification | Runtime prompt |
| Identifier and version | GEN-01 / generation-v1.0.0 |
| Requirements | FR-05; defense in depth for FR-06, FR-08, and FR-09 |
| Implementation | prompts/build/generation_v1.txt; loaded and validated by src/generate.py |
| Provider behavior | Provider-neutral interface; the same authority, evidence, schema, and validation contract applies to supported providers |
| Inputs | Application instructions, untrusted ticket JSON, retrieved documentation JSON, and required output schema |
| Required output | Exactly one JSON object with answer, citations, supported, and uncertainty; no extra keys or prose |
| Citation contract | Every supported response includes at least one exact document_id/chunk_id pair supplied in retrieved evidence |
| Unsupported contract | If evidence is absent, irrelevant, contradictory, or insufficient: supported=false, answer=null, citations=[], and a concise uncertainty reason |
| Prohibitions | Memory-based answers, invented facts/IDs/URLs, unsupported commitments, system-prompt disclosure, routing changes, and instruction overrides |
| Current status | Active, frozen, and recorded in generation/audit metadata |

The authoritative prompt text remains in prompts/build/generation_v1.txt and is not duplicated here as an independently editable copy. src/generate.py appends clearly delimited ticket data, retrieved evidence, and the JSON schema, then validates structure, citation identity, disclosure, and commitment constraints. A malformed, unsupported, timed-out, rate-limited, or unavailable-provider result fails closed.

## 5. PR-04 injection-defense specification

PR-04 was an incomplete placeholder in the earlier workbook. Frozen V1 does not contain an injection-classifier prompt. Its actual specification is:

| Field | Evidence-supported content |
|---|---|
| Classification | Direct-code logic / no prompt, with GEN-01 defense in depth |
| Purpose | Prevent customer text from overriding application authority and prevent output from revealing system instructions or control metadata |
| Input handling | Ticket text is passed as untrusted JSON data, separate from the runtime instructions |
| Input detections | Override/disregard instructions, prompt-reveal requests, memory-based answering, pretend-documentation/citation requests, and jailbreak markers |
| Output detections | Instruction-override compliance, system-prompt/internal-instruction disclosure, chain-of-thought/developer-message references, and routing/guardrail control disclosure |
| Action | BLOCK and ESCALATE; never convert detection failure into a confident answer |
| Implementation | prompts/build/generation_v1.txt, src/generate.py, src/guardrails.py, and orchestration |
| Evidence | test_prompt_injection_cannot_override_source_authority; input/output injection and system-disclosure guardrail tests; end-to-end injection escalation test |
| Limitation | Functional and adversarial DEVELOPMENT tests exist. Validation attack coverage was NOT MEASURED and is not claimed. |

## 6. Guardrail specification register

| Guardrail | Prompt role | Direct-code implementation | Tests/evidence | Status |
|---|---|---|---|---|
| PII and secrets | GEN-01 forbids credentials/secrets disclosure. | PrivateDataGuardrail detects credential/token/private-data patterns and blocks. | Private-customer-data, API-key/secret, release-suppression, and sanitized-log tests. | Functional PASS; zero validation leakage outcome not established |
| Grounding | GEN-01 permits facts only from retrieved passages. | GroundingGuardrail requires valid evidence, supported/grounded state, citations, and minimum lexical support. | Grounding failure, missing evidence, safe grounded response, and pipeline tests. | Functional PASS |
| Citation validation | GEN-01 requires exact retrieved document_id/chunk_id pairs. | CitationIntegrityGuardrail rejects missing/malformed/unretrieved pairs, document IDs, and external URLs. | Citation identity, fabricated citation, and unsupported URL tests. | Functional PASS; validation human citation accuracy NOT MEASURED |
| Prompt injection/system disclosure | GEN-01 establishes authority and treats customer text as data. | PromptInjectionGuardrail checks input and output patterns; generator also rejects disclosure. | PR-04 evidence above. | Functional PASS; validation attack coverage NOT MEASURED |
| Unsupported commitments | GEN-01 forbids refunds, credits, guarantees, dates, SLA/contract exceptions, and roadmap promises. | UnsupportedCommitmentsGuardrail plus high-risk deterministic routing and generator validation. | Commitment tests across generation, routing, and guardrails. | Functional PASS |
| Malformed/invalid generation | Exact schema is included in the request. | GenerationValidityGuardrail and generator parser reject invalid JSON, prose, extra/missing/wrong-type fields, empty supported answers, and invalid citations. | Structured-schema and malformed-provider tests. | Functional PASS |
| Missing evidence | GEN-01 specifies the unsupported JSON response. | Generator avoids provider calls without context; grounding/citation guardrails block absent evidence. | No-context, unsupported-question, no-retrieval, and pipeline audit tests. | Functional PASS |
| Confidence/internal failures | No model prompt controls the final decision. | ConfidenceGuardrail validates probability fields/floor; exceptions yield GUARDRAIL_INTERNAL_ERROR and block; router fails closed. | Invalid-confidence, exploding-guardrail, timeout/outage/rate-limit, and logging tests. | Functional PASS; calibration target not met |

## 7. Prompt and evaluation checks

| Item | Test method | Expected constraint | Observed evidence | Status |
|---|---|---|---|---|
| GEN-01 structure | Automated unit tests with valid, invalid JSON, prose, missing/extra keys, wrong types, and unsupported forms | Exact four-field JSON contract | Parser/schema tests pass in repository and hosted CI | Functional PASS |
| GEN-01 grounding/citations | Unit and pipeline tests with matched, absent, and fabricated sources | Evidence-only answer and exact retrieved pairs | Functional blocking and citation identity demonstrated | Functional PASS |
| GEN-01 authority/security | Injection, disclosure, route-isolation, and evaluation-field leakage tests | Customer/evaluation data cannot rewrite instructions or route | Tests demonstrate rejection/isolation | Functional PASS |
| GEN-01 provider failures | Timeout, rate-limit, provider-outage, and malformed-output tests | Fail closed without customer release | Controlled unsupported result and escalation paths demonstrated | Functional PASS |
| GEN-01 answer quality | Two independent humans reviewed 50 development response candidates | Assess hallucination, semantic citation support, correctness, usefulness | Hallucination 2%, citation 98%, correctness 3.74/5, usefulness 2.87/5 | DEVELOPMENT ONLY; does not prove production readiness |
| HDE-01 review protocol | Schema validation, distinct reviewer IDs, independence confirmation, complete 50-item forms, agreement calculation | Genuine independent human ratings and explicit evidence boundary | Completed artifacts and aggregation report | Complete for DEVELOPMENT; validation human evaluation NOT MEASURED |

No human evaluation was performed on validation responses. Prompt quality does not establish availability, safe automation, business outcomes, or production readiness.

## 8. Prompt quality checklist

| Check from original template | GEN-01 evidence |
|---|---|
| Role and task separated | SYSTEM AUTHORITY identifies the generation role; task and non-routing boundary are explicit. |
| Inputs clearly delimited | Ticket and retrieved documentation are serialized as distinct untrusted/evidence JSON sections. |
| Output format exact | REQUIRED OUTPUT SCHEMA is appended and only the defined JSON object is accepted. |
| Unknown-answer behavior | UNCERTAINTY defines the exact fail-closed unsupported response. |
| Representative cases tested | Supported, unsupported, missing evidence, fabricated citations, injection, commitments, malformed output, timeout, rate limit, and outage cases exist. |
| Forbidden behavior explicit | Grounding, citation, commitment, security, disclosure, and routing prohibitions are explicit. |

## 9. Version and evidence boundaries

- generation-v1.0.0 is the only frozen runtime prompt version.
- HDE-01 is an evaluation/human-review specification and never becomes runtime context.
- PR-01 v1.2, PR-02 v1.3, and PR-03 v1.1 are deprecated workbook history, not frozen runtime prompts.
- PR-04 is now documented as direct-code injection defense; no prompt text is invented.
- Classification is TF-IDF/logistic regression; retrieval is MiniLM/NumPy exact cosine; routing and guardrails are deterministic Python.
- DEVELOPMENT human metrics remain DEVELOPMENT ONLY: hallucination 2%, semantic citation accuracy 98%, correctness 3.74/5, usefulness 2.87/5.
- Validation hallucination and validation semantic citation accuracy are NOT MEASURED.
- V1 automation was 0% and escalation 100%. No prompt result is used to claim production readiness.

## 10. Remaining limitations

- No separately versioned identifier is present for the human-review protocol beyond its schema/versioned artifacts; this document does not invent one.
- Validation-set human prompt evaluation and validation adversarial-attack coverage were not performed.
- Live-provider evidence is component-level only.
- The DEVELOPMENT usefulness score of 2.87/5, weak urgency performance, and poor validation calibration remain deployment limitations rather than prompt claims to tune away.
