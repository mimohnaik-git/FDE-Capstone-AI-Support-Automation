# Stage 4: Sprint Plan — CloudServe Support Automation

## 1. Capacity Planning

| Week | Realistically Available Hours | Primary Focus | Constraints / Risks |
| :--- | :--- | :--- | :--- |
| **Week 1** | 20 hours | Discovery, Stakeholder Analysis, PRD Baseline | None |
| **Week 2** | 22 hours | System Build (Ingest, Retrieve, Classify, Route, Generate, Guardrails) | Model API latency |
| **Week 3** | 18 hours | System Evaluation, Workbook Deliverables, Submission Package | Deadline constraint |

---

## 2. Master Work Breakdown Structure (WBS Backlog)

| Task ID | Item / Component | Est. Hours | Priority | Dependencies | Definition of Done |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TASK-01** | Environment & Config Setup (`src/config.py`) | 4h | Must | None | Environment variables load cleanly; unit test passes. |
| **TASK-02** | Data Ingestion & Normalization (`src/ingest.py`) | 5h | Must | TASK-01 | Ingests 500 dev tickets; invalid JSON rejected cleanly. |
| **TASK-03** | Vector Store & Retrieval (`src/retrieve.py`) | 8h | Must | TASK-01 | Chroma vector indexing; Recall@3 > 85% on 29 articles. |
| **TASK-04** | Intent & Urgency Classifier (`src/classify.py`) | 6h | Must | TASK-02 | 22 intent categories classified with confidence score. |
| **TASK-05** | Decision Router (`src/route.py`) | 6h | Must | TASK-03,04 | Multi-factor routing to AUTO_RESPOND or ESCALATE. |
| **TASK-06** | Response Generator (`src/generate.py`) | 8h | Must | TASK-05 | Grounded responses generated with explicit citations. |
| **TASK-07** | Safety Guardrails (`src/guardrails.py`) | 8h | Must | TASK-06 | PII scanning, injection blocking, grounding check. |
| **TASK-08** | SQLite Decision Logging (`src/logging.py`) | 4h | Must | TASK-05 | 100% of pipeline execution logs written to SQLite. |
| **TASK-09** | FastAPI Web Service (`src/api.py`) | 4h | Must | TASK-07 | FastAPI `/api/v1/ticket` & `/health` endpoints functional. |
| **TASK-10** | Evaluation Harness (`evaluation/`) | 7h | Must | TASK-09 | Full benchmark run over dev & val tickets completed. |

---

## 3. Daily Execution Plan (Week 2 & 3 Highlights)

- **Week 2 Day 1-2**: Complete Data Ingestion, Chroma Vector Indexing, and Semantic Retriever.
- **Week 2 Day 3-4**: Build Intent Classifier, Multi-factor Router, and Citation Response Generator.
- **Week 2 Day 5**: Complete Safety Guardrail Suite (PII, injection filter, grounding check) and SQLite logger.
- **Week 3 Day 1-2**: Execute Evaluation Harness on 500 `development_tickets.json` and 120 `validation_tickets.json`.
- **Week 3 Day 3-4**: Synthesize empirical results into evaluation reports and stage workbooks.
- **Week 3 Day 5**: Final Pytest regression test run (75/75 passing) and submission packaging.
