# Stage 1: Discovery Workbook — CloudServe Solutions

## 1. Stakeholder Interview Summary

| Person & Role | What They Told You | What They Appear Not to Know | What You Verified in Data |
| :--- | :--- | :--- | :--- |
| **Marcus Adeyemi**<br>Head of Support | Ticket volume is crushing team; MTTR is high; commissioned automation to lower costs and speed response times. | Internal doc search fails due to keyword mismatch; agents reconstruct answers from memory using outdated personal files. | 71.4% of tickets are answerable by documentation vs 43.8% first contact resolution. |
| **Sofia Restrepo**<br>Tier 1 Agent | Spends most time searching for documentation; customers use vague terms ("deployment dying" vs "container health check failure"). Uses personal cheat sheets. | Personal cheat sheets contain stale policy details; official KB articles are updated regularly by Ines. | Ticket channel split (Email 42.4%, Chat 31.0%, Docs 15.6%) & 24.0% non-fluent users. |
| **Daniel Okonkwo**<br>Tier 2 Engineer | Escalations arrive with zero context, forcing re-reading threads and re-asking customers questions. | Tier 1 agents lack structured tools to capture context during ticket routing. | 100% of security, compliance, and billing tickets are escalated due to policy boundaries. |
| **Ines Varga**<br>Tech Writer | 29 KB articles cover recurring topics, but agents use unreviewed personal files because title search fails. | Customers search by problem symptoms rather than exact technical article titles. | Coverage of documentation against actual intent categories (71.4% total answerability). |
| **Ravi Menon**<br>Customer | Waiting is painful. Fine with automated response if honest, machine-labeled, and cites authoritative sources. | Tier-based SLA disparities (Enterprise gets 1hr response vs Standard/Business waiting hours). | CSAT average is 2.97/5.00; repeat contact rate is 21.6%. |

---

## 2. Transcript Disagreements Resolved via Data

1. **Doc Completeness vs Accessibility**: Marcus believed KB lacked answers; Ines claimed 29 articles cover recurring queries.
   - *Data settlement*: 357 / 500 tickets (71.4%) are answerable from existing docs. Ines is correct on coverage; keyword search is the bottleneck.
2. **Language Fluency Impact**: Sofia claimed non-fluent customers take longer and fail more often.
   - *Data settlement*: Non-fluent users (24% volume) achieve 45.8% FCR and 3.04 CSAT (higher than 2.97 avg). Semantic vector search bridges language phrasing gaps.
3. **Escalation Drivers**: Daniel assumed escalations are technical bugs.
   - *Data settlement*: Escalations are driven by safety policies (100% security, billing, compliance escalated).

---

## 3. Empirical Dataset Metrics (500 Development Tickets)

- **Total Sample**: 500 tickets (`development_tickets.json`)
- **Channel Split**: Email: 212 (42.4%), Chat: 155 (31.0%), Docs: 78 (15.6%), Forum: 55 (11.0%)
- **Urgency Split**: Medium: 226 (45.2%), High: 146 (29.2%), Low: 128 (25.6%)
- **First Contact Resolution (FCR)**: 219 / 500 (43.8%)
- **Average CSAT**: 2.97 / 5.00
- **Doc Answerability**: 357 / 500 (71.4%)
- **Repeat Contact Rate**: 108 / 500 (21.6%)
- **Non-Fluent Fluency**: 120 / 500 (24.0%)

---

## 4. Problem Statement

> CloudServe Solutions experiences excessive customer response latency (4+ hours) and low first-contact resolution (43.8%) despite 71.4% of incoming tickets being answerable by existing documentation. This inefficiency stems from keyword search failures that prevent support agents from discovering relevant knowledge base articles, forcing agents to rely on unverified personal cheat sheets or forward context-free escalations to Tier 2 engineering.
>
> To solve this, CloudServe requires an automated, documentation-grounded support system that semantically matches customer queries to official documentation, auto-responds to safe requests with explicit citations, and escalates high-risk or low-confidence tickets with structured diagnostic context while strictly preventing PII leakage and hallucination.
