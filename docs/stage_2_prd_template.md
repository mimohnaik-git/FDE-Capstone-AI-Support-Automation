# Stage 2: Product Requirements Document (PRD) — CloudServe Support Automation

## 1. Document Control

| Field | Value |
| :--- | :--- |
| **Document Title** | Product Requirements Document — CloudServe Support Automation |
| **Version** | 1.0 (Baseline Approved) |
| **Author** | Forward Deployed AI Engineer |
| **Date** | 4 September 2026 |
| **Status** | Approved for Implementation |
| **Target Release** | 13 September 2026 |

---

## 2. Problem Statement

> CloudServe Solutions experiences excessive customer response latency (4+ hours) and low first-contact resolution (43.8%) despite 71.4% of incoming tickets being answerable by existing documentation. This inefficiency stems from keyword search failures that prevent support agents from discovering relevant knowledge base articles, forcing agents to rely on unverified personal cheat sheets or forward context-free escalations to Tier 2 engineering.
>
> To solve this, CloudServe requires an automated, documentation-grounded support system that semantically matches customer queries to official documentation, auto-responds to safe requests with explicit citations, and escalates high-risk or low-confidence tickets with structured diagnostic context while strictly preventing PII leakage and hallucination.

---

## 3. User Groups & User Needs

| User Group | Needs from System | Current Workaround | Success Criteria |
| :--- | :--- | :--- | :--- |
| **Tier 1 Support Agents** | Fast access to verified KB articles during ticket triaging. | Search internal KB via title keywords or check personal cheat sheets. | Search time reduced from 10 mins to <5 seconds; elimination of personal cheat sheets. |
| **Tier 2 Engineers** | Structured escalation packages with intent, docs, reasoning, and confidence score. | Receive raw forwarded tickets with zero context or history summary. | Zero time spent re-reading threads or re-asking previously answered questions. |
| **Support Management** | Higher first contact resolution (>65%) and significantly lower MTTR (<5 mins). | Manually review SLA breaches and high customer churn risks. | CSAT increased from 2.97 to >4.20; overall support operational cost reduced. |
| **CloudServe Customers** | Fast, accurate, machine-labeled auto-responses citing official documentation. | Wait 4+ hours for simple doc-answerable support questions. | Instant answers for 71.4% doc queries; explicit citation links provided. |
| **Technical Writer** | Full citation transparency linking responses directly to specific KB articles. | No visibility into whether support agents utilize reviewed KB articles. | 100% citation tracking to monitor KB usage and article quality. |
| **Security & Legal Team** | Guaranteed isolation of customer PII and zero unauthorized financial commitments. | Rely on manual agent vigilance to catch PII leaks or bad commitments. | Zero PII leak incidents; 100% blocking of billing/commitment auto-responses. |

---

## 4. Functional Requirements

| ID | Requirement | Priority | Discovery Link | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Ticket Ingestion & Validation: Ingest JSON support tickets, validate schema integrity, and normalize fields. | Must | Sofia transcript & Table 11 | 100% valid schema processing; invalid payloads rejected cleanly. |
| **FR-02** | Intent & Urgency Classification: Classify intent across 22 categories and score urgency using rule fallback. | Must | Marcus interview & Table 5 | Intent classification accuracy > 85% on benchmark set. |
| **FR-03** | Semantic Knowledge Retrieval: Execute dense vector retrieval (Chroma + all-MiniLM-L6-v2) with BM25 fallback. | Must | Ines & Sofia interviews | Doc retrieval Recall@k=3 > 85% across 29 KB articles. |
| **FR-04** | Multi-Factor Decision Routing: Route to AUTO_RESPOND, MANUAL_REVIEW, or ESCALATE based on safety & score. | Must | Daniel & Marcus interviews | 0 safe escalations missed; 100% unsafe tickets routed to human. |
| **FR-05** | Grounded Response Generation: Generate responses using retrieved KB chunks with Markdown source citations. | Must | Ravi & Ines interviews | 100% generated responses contain explicit article citations. |
| **FR-06** | Post-Generation Grounding Guardrail: Validate responses against doc chunks using factual overlap checks. | Must | Ravi interview & Risk 1 | 0 ungrounded claims or hallucinations allowed through guardrail. |
| **FR-07** | PII & Credentials Protection: Scan responses for API keys, passwords, account numbers, and mask/block PII. | Must | Daniel interview & Risk 2 | 0 PII leakage occurrences across all evaluation runs. |
| **FR-08** | Adversarial Injection Defense: Filter input for system prompt override attempts, jailbreaks, and adversarial text. | Must | Risk 4 & CLAUDE.md Sec 16 | 100% adversarial prompt injection attempts detected and blocked. |
| **FR-09** | Financial Commitment Block: Route billing, refund, contractual, and SLA queries to human escalation. | Must | Daniel interview & Risk 3 | 0 automated responses sent for billing or financial intents. |
| **FR-10** | Structured Escalation Payload: Construct diagnostic summary (intent, docs, reasoning, confidence) for Tier 2. | Must | Daniel interview | 100% escalations delivered with complete structured diagnostic package. |
| **FR-11** | Persistent Audit Logging: Record input, classification, vector scores, routing, response, and guardrails to SQLite. | Must | Governance & CLAUDE.md Sec 8 | 100% auditable log entries written to decision log database. |
| **FR-12** | Automated Evaluation Harness: Calculate FCR, accuracy, precision, recall, latency, and guardrail block rates. | Must | Marcus interview & Table 9 | Automated generation of markdown and JSON evaluation reports. |

---

## 5. Non-Functional Requirements

| ID | Category | Requirement | Verification Method |
| :--- | :--- | :--- | :--- |
| **NFR-01** | Latency | Processing latency for auto-response must be under 3.0s (p95). | Measured via evaluation harness log timer. |
| **NFR-02** | Availability | FastAPI service must support 99.9% uptime during operation. | Verified via `/health` endpoint checks. |
| **NFR-03** | Vector Efficiency | Vector similarity search must complete in < 50ms per query. | Benchmarked via Chroma execution logs. |
| **NFR-04** | Security | Secrets & API keys must never be logged or exposed in responses. | Automated static regex scanner on SQLite logs. |
| **NFR-05** | Coverage | Pipeline code in `src/` must maintain > 90% unit test coverage. | Measured via `pytest-cov` runner. |
| **NFR-06** | Auditability | Every response must link to SQLite decision ID and doc chunk IDs. | Verified via foreign key audit check. |
| **NFR-07** | Privacy | PII detection must comply with GDPR / CCPA masking rules. | Validated using synthetic PII test suite. |
| **NFR-08** | Robustness | Non-fluent English text must achieve > 80% classification accuracy. | Tested against 120 non-fluent dev tickets. |
| **NFR-09** | Autonomy | Pipeline must execute locally without cloud dependencies. | Validated in standalone isolated environment. |
| **NFR-10** | Modularity | Architecture must decouple ingestion, retrieval, routing, and safety. | Architectural code inspection of `src/`. |
