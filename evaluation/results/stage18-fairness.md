# Stage 18 Fairness Analysis

Evidence: DEVELOPMENT and VALIDATION reported separately.

## DEVELOPMENT

### customer_tier

| Group | N | Status | Intent acc | Urgency acc | Recall@3 | Routing acc | Automation | Escalation |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| enterprise | 83 | MEASURED — NO FORMAL TARGET | 1.000 | 0.639 | 0.856 | 0.386 | 0.000 | 1.000 |
| other_tiers | 417 | MEASURED — NO FORMAL TARGET | 1.000 | 0.652 | 0.856 | 0.376 | 0.000 | 1.000 |

Differences from the best eligible group (absolute rate; escalation uses the lowest rate as best):

- enterprise: intent_accuracy=0.0, intent_macro_f1=0.0, urgency_accuracy=0.013724, urgency_macro_f1=0.03301, retrieval_recall_at_3=0.0, retrieval_mrr=0.0, routing_accuracy=0.0, automation_rate=0.0, escalation_rate=0.0
- other_tiers: intent_accuracy=0.0, intent_macro_f1=0.0, urgency_accuracy=0.0, urgency_macro_f1=0.0, retrieval_recall_at_3=0.000227, retrieval_mrr=0.033382, routing_accuracy=0.009043, automation_rate=0.0, escalation_rate=0.0

### language_fluency

| Group | N | Status | Intent acc | Urgency acc | Recall@3 | Routing acc | Automation | Escalation |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| fluent | 380 | MEASURED — NO FORMAL TARGET | 1.000 | 0.629 | 0.874 | 0.392 | 0.000 | 1.000 |
| non_fluent | 120 | MEASURED — NO FORMAL TARGET | 1.000 | 0.717 | 0.799 | 0.333 | 0.000 | 1.000 |

Differences from the best eligible group (absolute rate; escalation uses the lowest rate as best):

- fluent: intent_accuracy=0.0, intent_macro_f1=0.0, urgency_accuracy=0.08772, urgency_macro_f1=0.08608, retrieval_recall_at_3=0.0, retrieval_mrr=0.0, routing_accuracy=0.0, automation_rate=0.0, escalation_rate=0.0
- non_fluent: intent_accuracy=0.0, intent_macro_f1=0.0, urgency_accuracy=0.0, urgency_macro_f1=0.0, retrieval_recall_at_3=0.075223, retrieval_mrr=0.067026, routing_accuracy=0.058772, automation_rate=0.0, escalation_rate=0.0

### text_length

| Group | N | Status | Intent acc | Urgency acc | Recall@3 | Routing acc | Automation | Escalation |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| short | 271 | MEASURED — NO FORMAL TARGET | 1.000 | 0.672 | 0.826 | 0.406 | 0.000 | 1.000 |
| long | 229 | MEASURED — NO FORMAL TARGET | 1.000 | 0.624 | 0.891 | 0.345 | 0.000 | 1.000 |

Differences from the best eligible group (absolute rate; escalation uses the lowest rate as best):

- short: intent_accuracy=0.0, intent_macro_f1=0.0, urgency_accuracy=0.0, urgency_macro_f1=0.0, retrieval_recall_at_3=0.065388, retrieval_mrr=0.108805, routing_accuracy=0.0, automation_rate=0.0, escalation_rate=0.0
- long: intent_accuracy=0.0, intent_macro_f1=0.0, urgency_accuracy=0.047133, urgency_macro_f1=0.066681, retrieval_recall_at_3=0.0, retrieval_mrr=0.0, routing_accuracy=0.060926, automation_rate=0.0, escalation_rate=0.0

## VALIDATION

### customer_tier

| Group | N | Status | Intent acc | Urgency acc | Recall@3 | Routing acc | Automation | Escalation |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| enterprise | 8 | NOT MEASURED | — | — | — | — | — | — |
| other_tiers | 72 | MEASURED — NO FORMAL TARGET | 1.000 | 0.403 | 0.883 | 0.417 | 0.000 | 1.000 |

Differences from the best eligible group (absolute rate; escalation uses the lowest rate as best):

- enterprise: NOT MEASURED
- other_tiers: intent_accuracy=None, intent_macro_f1=None, urgency_accuracy=None, urgency_macro_f1=None, retrieval_recall_at_3=None, retrieval_mrr=None, routing_accuracy=None, automation_rate=None, escalation_rate=None

### language_fluency

| Group | N | Status | Intent acc | Urgency acc | Recall@3 | Routing acc | Automation | Escalation |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| fluent | 61 | MEASURED — NO FORMAL TARGET | 1.000 | 0.426 | 0.875 | 0.344 | 0.000 | 1.000 |
| non_fluent | 19 | NOT MEASURED | — | — | — | — | — | — |

Differences from the best eligible group (absolute rate; escalation uses the lowest rate as best):

- fluent: intent_accuracy=None, intent_macro_f1=None, urgency_accuracy=None, urgency_macro_f1=None, retrieval_recall_at_3=None, retrieval_mrr=None, routing_accuracy=None, automation_rate=None, escalation_rate=None
- non_fluent: NOT MEASURED

### text_length

| Group | N | Status | Intent acc | Urgency acc | Recall@3 | Routing acc | Automation | Escalation |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| short | 43 | MEASURED — NO FORMAL TARGET | 1.000 | 0.279 | 0.857 | 0.395 | 0.000 | 1.000 |
| long | 37 | MEASURED — NO FORMAL TARGET | 1.000 | 0.595 | 0.900 | 0.405 | 0.000 | 1.000 |

Differences from the best eligible group (absolute rate; escalation uses the lowest rate as best):

- short: intent_accuracy=0.0, intent_macro_f1=0.0, urgency_accuracy=0.315525, urgency_macro_f1=0.326831, retrieval_recall_at_3=0.042857, retrieval_mrr=0.086428, routing_accuracy=0.010056, automation_rate=0.0, escalation_rate=0.0
- long: intent_accuracy=0.0, intent_macro_f1=0.0, urgency_accuracy=0.0, urgency_macro_f1=0.0, retrieval_recall_at_3=0.0, retrieval_mrr=0.0, routing_accuracy=0.0, automation_rate=0.0, escalation_rate=0.0

## Governance threshold

**NOT MEASURED** — The registry requires the same human-reviewed quality outcome; human reviews are blank.

## Limitations

- Automated subgroup gaps do not establish customer outcome fairness.
- Small groups are not assigned performance conclusions.
- No protected attributes were inferred and no post-validation tuning was performed.
