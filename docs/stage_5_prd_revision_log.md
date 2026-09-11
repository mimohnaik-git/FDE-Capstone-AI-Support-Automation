# Stage 5: PRD Revision Log — CloudServe Support Automation

## 1. Revision Summary

| Field | Value |
| :--- | :--- |
| **Document Title** | PRD Revision Log — CloudServe Support Automation |
| **Revision Version** | 2.0 (Post-Evaluation Revision) |
| **Author** | Forward Deployed AI Engineer |
| **Revision Date** | 8 September 2026 |
| **Total Changes Recorded** | 4 major requirement revisions |
| **Primary Revision Trigger** | Empirical evaluation benchmark findings & edge-case testing |
| **Approval Status** | Approved & Implemented in Pipeline |
| **Verification** | All 75 Pytest regression tests passing |

---

## 2. Requirement Changes

| Requirement ID | What it Said in Version 1 | What it Says in Version 2 | What Prompted the Change | Agreed By |
| :--- | :--- | :--- | :--- | :--- |
| **FR-03** | Dense vector similarity retrieval alone. | Hybrid dense vector + BM25 keyword search fallback. | Dense vector search missed exact error codes (e.g. `ERR-4019`). | System Architect & Ines |
| **FR-04** | Auto-respond on confidence >= 0.70. | Auto-respond threshold raised to >= 0.82 + mandatory intent safety rules. | Borderline 0.72 scores produced partially relevant responses. | Marcus & System Lead |
| **FR-07** | Basic regex check for API keys. | Multi-pattern scanner (API keys, DB URIs, JWT tokens, account IDs). | Test ticket containing database URI (`postgres://...`) passed regex scanner. | Security & Daniel |
| **FR-10** | Text summary for escalations. | Structured JSON diagnostic payload (intent, docs, reasoning, confidence). | Daniel's requirement to show structured diagnostic context. | Daniel & Tier 2 Ops |

---

## 3. Assumptions Validation Log

| Assumption from Version 1 | Did it Hold? | What You Found Instead | What You Changed Because of It |
| :--- | :--- | :--- | :--- |
| Dense vector search is sufficient for all doc queries. | **False** | Exact alphanumeric error codes match better with BM25 keyword index. | Added BM25 hybrid retrieval component (`src/retrieve.py`). |
| A single confidence threshold works for all intent types. | **False** | Compliance and billing queries require strict safety rules regardless of score. | Enforced mandatory escalation rules for high-risk intents (`src/route.py`). |
| Standard LLM context window preserves citation accuracy. | **True** | Providing explicit doc chunk IDs in prompt preserved citation accuracy. | Maintained explicit Markdown citation format (`src/generate.py`). |
| Non-fluent English queries cause lower retrieval scores. | **False** | Dense embeddings mapped non-fluent phrasing effectively to KB topics. | Maintained uniform retrieval pipeline for all fluency levels. |
