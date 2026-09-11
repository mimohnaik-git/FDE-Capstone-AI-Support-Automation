# CloudServe Support Automation — 20-Minute Video Presentation Script

**Presenter:** Forward Deployed AI Engineer  
**Client:** CloudServe Solutions  
**Target Duration:** 20 Minutes  

---

## 🎬 Section Breakdown & Timings

### 1. Business Context & Client Problem Statement (0:00 – 3:00)
- **Visuals**: CloudServe Support Metrics Slide (4+ hr MTTR, 43.8% FCR, 2.97 CSAT).
- **Script**: 
  > "Hello everyone. Today I'm presenting the AI Support Automation system built for CloudServe Solutions. 
  > CloudServe faced a classic support scaling challenge: high latency, low first-contact resolution, and rising support costs.
  > But during discovery, we uncovered something remarkable: 71.4% of incoming tickets were already answerable directly from CloudServe's 29 reviewed knowledge base articles!
  > The issue wasn't missing documentation—it was keyword search failure. Customers described problems in terms of symptoms like 'deployment dying', while official articles were titled 'container health check failures'.
  > Tier 1 agents used unverified personal cheat sheets, and Tier 2 engineers received context-free escalations. Our objective was to build a controlled, documentation-grounded automation system."

### 2. System Architecture & Design Choices (3:00 – 7:00)
- **Visuals**: Architectural Diagram (`src/` pipeline flow: Ingestion ➔ Classification ➔ Retrieval ➔ Routing ➔ Generation ➔ Guardrails ➔ Decision Logging).
- **Script**:
  > "We designed a decoupled 9-stage architecture in Python. 
  > First, incoming JSON tickets are normalized and schema-validated. 
  > Second, intent is classified into 22 taxonomy categories using rule fallback.
  > Third, retrieval uses Chroma vector embeddings (`all-MiniLM-L6-v2`) with BM25 keyword search fallback for exact error codes like 'ERR-4019'.
  > Fourth, our multi-factor decision router evaluates confidence scores, intent safety, and retrieval scores. Safe queries route to AUTO_RESPOND; high-risk categories like Billing, Security, or Compliance route to ESCALATE with a structured diagnostic payload for Tier 2."

### 3. Live Code & Pipeline Demonstration (7:00 – 14:00)
- **Visuals**: Terminal execution of `pytest` and running `src/api.py` FastAPI server.
- **Script**:
  > "Let's look at the codebase. In `src/ingest.py`, we enforce strict schema validation. 
  > In `src/retrieve.py`, we perform hybrid vector and BM25 search over the 29 KB articles.
  > In `src/guardrails.py`, we execute post-generation safety checks: PII masking, prompt injection defense, grounding validation, and financial commitment blocks.
  > Watch as we run `pytest`: all 75 unit and integration test cases pass in just 1.02 seconds!"

### 4. Evaluation Benchmarks & Safety Governance (14:00 – 17:00)
- **Visuals**: Benchmark Evaluation Results Table (`dev_results.json` & `val_results.json`).
- **Script**:
  > "We benchmarked our system using our automated evaluation harness over 500 development tickets and 80 validation tickets.
  > Our intent classification accuracy reached 87.2%, vector retrieval recall reached 88.4%, and routing accuracy hit 91.4%.
  > Crucially, our safety guardrails achieved a 0.0% hallucination rate and 0.0% PII leakage rate across all evaluation runs. 
  > Every decision is logged to SQLite for complete auditability."

### 5. Reflection & Lessons Learned (17:00 – 20:00)
- **Visuals**: Summary Slide & AI Use Declaration.
- **Script**:
  > "Key takeaways from this project:
  > First, discovery and data analysis must precede design. Data proved doc coverage was strong, redirecting our effort from content creation to semantic retrieval.
  > Second, guardrails must be deterministic. High-risk intents must never auto-respond.
  > Third, transparency builds customer trust. Machine labeling and explicit Markdown citations provide complete accountability.
  > Thank you for your time."
