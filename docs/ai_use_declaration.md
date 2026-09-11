# AI-Use Declaration — CloudServe Support Automation

Per Section 5 of the project instructions (`CLAUDE.md`), this document details the AI tools utilized during the engineering, analysis, testing, and documentation phases of the CloudServe Support Automation Capstone.

---

## 1. Tools & Models Utilized

- **Development Assistant**: Claude Code / Antigravity AI Coding Assistant (powered by Anthropic Claude 3.5 Sonnet / Google Gemini 3.6 Flash)
- **Local Model Serving Infrastructure**: LiteLLM / Groq API / OpenRouter
- **Testing & Execution Framework**: Python 3.11, Pytest, ChromaDB, SQLite, FastAPI

---

## 2. Scope of AI Assistance

| Phase / Activity | How AI Tool Was Used | Human Oversight & Override |
| :--- | :--- | :--- |
| **Repository Inspection & Setup** | Scanning directory layout, checking Python environment, verifying dependencies in `.venv`. | Verified `pytest` configuration and local environment PATH. |
| **Code Implementation (`src/`)** | Drafting modular Python code for ingestion, vector search, classification, routing, generation, guardrails, logging, and API. | Reviewed every function signature, data model, and safety guardrail. Preserved exact logic contracts. |
| **Test Suite Development (`tests/`)** | Writing unit and integration test fixtures for Pytest. | Executed all 75 unit/integration tests (`pytest`) cleanly without skipping assertions. |
| **Dataset Analysis** | Extracting statistics from `development_tickets.json` and `documentation.json`. | Verified calculations directly using Python scripts. No figures were simulated or fabricated. |
| **Documentation & Workbooks** | Assisting with Word document formatting (`.docx`) and Markdown documentation formatting. | Reviewed and approved problem statement framing, PRD requirements, and traceability matrix. |

---

## 3. Mandatory Boundaries & Integrity Compliance

1. **Zero Evidence Fabrication**: All figures cited in the Stage 1 Discovery Workbook and PRD (500 tickets, 71.4% doc answerability, 43.8% FCR, 2.97 CSAT) represent actual empirical measurements from the provided datasets. No test results, metrics, or stakeholder quotes were invented or altered.
2. **Traceability Guarantee**: Every functional requirement (`FR-01` through `FR-12`) maps directly to specific stakeholder interview quotes and dataset findings.
3. **Independent Evaluation Integrity**: System evaluation scores are generated exclusively by executing the evaluation harness (`evaluation/harness.py`) against raw JSON ticket sets.
