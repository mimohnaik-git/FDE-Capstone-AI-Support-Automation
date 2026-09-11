# CloudServe Evaluation Report

## Evidence classification

- Classification: **DEVELOPMENT**
- Dataset role: `development`
- Run ID: `b9070713-b47d-4794-9bb2-f8a7b28408ff`
- Dataset SHA-256: `6b38bf1f1f22ec5d9fbafff1f7bf033c77478a0cd8814b402781458c1713c38b`
- Evaluated tickets: `500` of `500`
- Started UTC: `2026-09-10T05:25:01.829879+00:00`
- Production entry point: `src.pipeline.SupportPipelineOrchestrator.process_ticket`

This report contains DEVELOPMENT evidence only.

## Reconciliation

- Status: **PASS**
- Source / evaluated / terminal / logged: 500 / 500 / 500 / 500
- Reconciled: `True`

## Metric registry results

| Metric | Type | Measured | Documented target | Status | Denominator or limitation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Intent classification accuracy | AUTOMATED | 100.0% | No formal target | MEASURED — NO FORMAL TARGET | 500 eligible / 0 excluded |
| Intent macro precision | AUTOMATED | 100.0% | >=85% | PASS | 22 eligible / 0 excluded |
| Intent macro recall | AUTOMATED | 100.0% | No formal target | MEASURED — NO FORMAL TARGET | 22 eligible / 0 excluded |
| Intent macro F1 | AUTOMATED | 100.0% | No formal target | MEASURED — NO FORMAL TARGET | 22 eligible / 0 excluded |
| Urgency classification accuracy | AUTOMATED | 65.0% | No formal target | MEASURED — NO FORMAL TARGET | 500 eligible / 0 excluded |
| Urgency macro precision | AUTOMATED | 64.3% | No formal target | MEASURED — NO FORMAL TARGET | 3 eligible / 0 excluded |
| Urgency macro recall | AUTOMATED | 63.2% | No formal target | MEASURED — NO FORMAL TARGET | 3 eligible / 0 excluded |
| Urgency macro F1 | AUTOMATED | 63.7% | No formal target | MEASURED — NO FORMAL TARGET | 3 eligible / 0 excluded |
| Retrieval Recall@1 | AUTOMATED | 74.4% | No formal target | MEASURED — NO FORMAL TARGET | 357 eligible / 143 excluded |
| Retrieval Recall@3 | AUTOMATED | 85.6% | No formal target | MEASURED — NO FORMAL TARGET | 357 eligible / 143 excluded |
| Retrieval Recall@5 | AUTOMATED | 88.4% | No formal target | MEASURED — NO FORMAL TARGET | 357 eligible / 143 excluded |
| Retrieval Precision@1 | AUTOMATED | 85.7% | No formal target | MEASURED — NO FORMAL TARGET | 357 eligible / 143 excluded |
| Retrieval Precision@3 | AUTOMATED | 34.8% | No formal target | MEASURED — NO FORMAL TARGET | 357 eligible / 143 excluded |
| Retrieval Precision@5 | AUTOMATED | 24.2% | No formal target | MEASURED — NO FORMAL TARGET | 357 eligible / 143 excluded |
| Retrieval mean reciprocal rank | AUTOMATED | 89.4% | No formal target | MEASURED — NO FORMAL TARGET | 357 eligible / 143 excluded |
| Routing accuracy | AUTOMATED | 37.8% | No formal target | MEASURED — NO FORMAL TARGET | 500 eligible / 0 excluded |
| Auto-response precision | AUTOMATED | - | No formal target | NOT MEASURED | 0 eligible / 0 excluded |
| Auto-response recall | AUTOMATED | 0.0% | No formal target | MEASURED — NO FORMAL TARGET | 311 eligible / 0 excluded |
| Automation rate | AUTOMATED | 0.0% | No formal target | MEASURED — NO FORMAL TARGET | 500 eligible / 0 excluded |
| Escalation rate | AUTOMATED | 100.0% | <=30% | FAIL | 500 eligible / 0 excluded |
| Guardrail coverage | AUTOMATED | - | 100% | NOT MEASURED | 0 eligible / 0 excluded |
| Processing failure rate | AUTOMATED | 0.0% | No formal target | MEASURED — NO FORMAL TARGET | 500 eligible / 0 excluded |
| Decision-log coverage | AUTOMATED | 100.0% | 100% | PASS | 500 eligible / 0 excluded |
| P50 pipeline latency | AUTOMATED | 0.0411s | No formal target | MEASURED — NO FORMAL TARGET | 500 eligible / 0 excluded |
| P95 pipeline latency | AUTOMATED | 0.1120s | <3 seconds | PASS | 500 eligible / 0 excluded |
| Confidence calibration error | AUTOMATED | 39.7% | <=5 percentage points | FAIL | 500 eligible / 0 excluded |
| Citation ID validity | AUTOMATED | - | No formal target | NOT MEASURED | 0 eligible / 0 excluded |
| Private-data occurrences in released responses | AUTOMATED | - | 0 | NOT MEASURED | 0 eligible / 500 excluded |
| Hallucination rate | HUMAN_REVIEW | - | <=5% | NOT MEASURED | No completed human-review evidence was supplied. |
| Semantic citation accuracy | HUMAN_REVIEW | - | >=95% | NOT MEASURED | No completed human-review evidence was supplied. |
| Response correctness | HUMAN_REVIEW | - | No formal target | NOT MEASURED | No completed human-review evidence was supplied. |
| Response usefulness | HUMAN_REVIEW | - | No formal target | NOT MEASURED | No completed human-review evidence was supplied. |
| First contact resolution | OPERATIONAL | - | >=60% | NOT MEASURED | Local routes do not establish verified resolution and follow-up outcomes. |
| Time to first substantive response | OPERATIONAL | - | mean <5 minutes | NOT MEASURED | Pipeline latency is not arrival-to-customer-response time. |
| Customer satisfaction | OPERATIONAL | - | >=4.0/5 | NOT MEASURED | No customer ratings attributable to this run were collected. |
| Service availability | OPERATIONAL | - | >=99.5% | NOT MEASURED | A local pipeline run is not an availability study. |
| Repeat contact rate | OPERATIONAL | - | approximately halved | NOT MEASURED | No linked one-week follow-up observation and baseline were supplied. |
| Cross-group quality difference | HUMAN_REVIEW | - | <5 percentage points | NOT MEASURED | 0 eligible / 0 excluded |

Only these statuses are permitted: **PASS**, **FAIL**, **NOT MEASURED**, **NOT APPLICABLE**, and **MEASURED — NO FORMAL TARGET**. Missing values never pass.

## Important measurement boundaries

- Citation ID validity checks only whether emitted IDs resolve to retrieved documents. It is not semantic citation accuracy.
- Pipeline latency measures local processing duration. It is not time to first substantive customer response.
- Hallucination, semantic citation accuracy, response correctness, and usefulness remain unmeasured until real human reviews complete the blank template.
- FCR, CSAT, availability, first-response time, and repeat-contact rate are not inferred from pipeline outcomes or historical dataset fields.

## Limitations

- This is development evidence re-aggregated from the complete Stage 9 development run, not validation or final evidence.
- The classifier was developed using the development dataset; its development score is not an unbiased generalization estimate.
- Automated citation ID validity does not establish semantic citation accuracy.
- Local pipeline latency does not measure customer first-response time or service availability.
- Human-review metrics are blank until real independent assessments are supplied.
- Business outcomes are not inferred from historical dataset fields or routing outcomes.
