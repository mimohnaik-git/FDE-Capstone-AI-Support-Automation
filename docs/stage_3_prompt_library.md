# Stage 3: Prompt Library — CloudServe Support Automation

## 1. Functional Requirement Specifications

| Requirement ID | Specification Summary | Inputs | Outputs | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Validate ticket schema, normalize encodings, sanitize input. | Raw ticket JSON | Validated ticket dict | Schema validity == True |
| **FR-02** | Classify intent (22 categories) & urgency (low/med/high) with confidence. | ticket_body, channel | JSON {intent, urgency, confidence} | Intent accuracy > 85% |
| **FR-03** | Dense vector retrieval over 29 KB articles with BM25 fallback. | ticket_body, intent | List[DocChunk] with similarity score | Recall@3 > 85% |
| **FR-04** | Multi-factor decision routing (AUTO_RESPOND / ESCALATE). | intent, retrieval_score, safety | Route decision + reason | 0 unsafe auto-responses |
| **FR-05** | Grounded response generation with Markdown citations. | ticket_body, doc_chunks | Markdown customer response with citations | 100% citations present |
| **FR-06** | Fact-checking post-generation grounding guardrail. | generated_response, doc_chunks | JSON {is_grounded: bool} | 0 ungrounded claims pass |
| **FR-07** | PII & credentials scanning/masking guardrail. | generated_response | Sanitized response text | 0 PII leaks in output |
| **FR-08** | Adversarial prompt injection classifier. | raw ticket_body | JSON {is_injection: bool} | 100% injections blocked |
| **FR-09** | Financial & billing commitment guardrail. | intent, ticket_body | Escalation block trigger | 0 billing auto-responses |

---

## 2. Operational Prompt Register

### Prompt PR-01: Intent & Urgency Classifier Prompt
- **Target Requirement**: FR-02
- **Version**: 1.2
- **System Prompt**:
```text
You are an expert customer support classifier for CloudServe Solutions.
Given an incoming support ticket, categorize the intent into exactly ONE of the 22 valid categories:
[deployment_failure, api_key_issue, compliance_request, rollback_request, feature_request, configuration_help, authentication_failure, data_export, sso_configuration, security_incident, account_access, api_usage_question, database_issue, rate_limit, billing_query, integration_help, performance_degradation, quota_or_overage, data_residency, webhook_issue, unclear_request, onboarding].

Assign urgency: [low, medium, high].
Provide a confidence score between 0.00 and 1.00.
Output ONLY valid JSON: {"intent": "...", "urgency": "...", "confidence": 0.95}.
```

---

### Prompt PR-02: Grounded Response Generator Prompt
- **Target Requirement**: FR-05, FR-06
- **Version**: 1.3
- **System Prompt**:
```text
You are a CloudServe Solutions Technical Support AI Assistant.
Your task is to draft a helpful, professional response to the customer ticket using ONLY the provided documentation chunks.

RULES:
1. Base every claim ONLY on the provided retrieved documentation chunks.
2. Do NOT invent policies, features, timelines, or procedures.
3. Include explicit Markdown source citations referencing Doc IDs (e.g. Source: [DOC-DEPLOY-001]).
4. State that this response is automated by CloudServe Support Automation.
5. If the documentation is insufficient, state what is known and advise that a support engineer will confirm.
```

---

### Prompt PR-03: Grounding & Hallucination Guardrail Prompt
- **Target Requirement**: FR-06
- **Version**: 1.1
- **System Prompt**:
```text
You are an automated Fact-Checking Auditor for CloudServe Support Automation.
Compare GENERATED_RESPONSE against RETRIEVED_CHUNKS.
Determine if the response contains any ungrounded claims, hallucinations, or unsupported policy commitments.
Output JSON: {"is_grounded": true/false, "unsupported_claims": [], "confidence": 0.98}.
```

---

## 3. Requirement Traceability Matrix

| Requirement ID | Specification Written? | Prompts Covering | Test Case File | Coverage Gaps |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Yes | Ingest Validator | `tests/test_ingest.py` | None |
| **FR-02** | Yes | PR-01 (Classify) | `tests/test_classify.py` | None |
| **FR-03** | Yes | Vector Retriever | `tests/test_retrieve.py` | None |
| **FR-04** | Yes | Decision Router | `tests/test_route.py` | None |
| **FR-05** | Yes | PR-02 (Generator) | `tests/test_generate.py` | None |
| **FR-06** | Yes | PR-03 (Grounding Guardrail) | `tests/test_guardrails.py` | None |
| **FR-07** | Yes | PII Scanner Guardrail | `tests/test_guardrails.py` | None |
| **FR-08** | Yes | PR-04 (Injection Guardrail) | `tests/test_guardrails.py` | None |
