# Validation Classification Confusion Matrix Appendix

## Methodology and evidence boundary

This appendix derives classification confusion matrices from the preserved authorized
technical validation rerun, `evaluation/results/validation-technical-rerun.json`, and
the supplied labels in `data/raw/validation_tickets.json`. Records were joined only on
`ticket_id`. The rerun is `c5f1e1dc-531a-4586-b5d9-cbd1545789d4`, completed on 10
September 2026, and is the authoritative usable validation result.

The supplied validation set has 80 tickets. The preserved rerun has 80 records; all 80
ticket IDs matched, with no missing validation IDs and no unknown rerun IDs. No hidden
assessment data was used. No model inference, evaluation-harness execution, validation
rerun, V1 change, or threshold change occurred to produce this appendix.

Rows are actual labels and columns are predicted labels. The machine-readable source is
`evaluation/results/validation-confusion-matrices.json`.

This is **VALIDATION technical classification evidence only**. It is not validation
human evaluation and does not establish hallucination, semantic citation accuracy,
usefulness, fairness, FCR, CSAT, availability, or production readiness.

## Intent classification matrix

The preserved result contains all 22 intent classes. To keep the full 22-by-22 matrix
legible in a report appendix, the following key labels the row and column order.

```text
I01 account_access             I09 data_residency          I17 rate_limit
I02 api_key_issue              I10 database_issue          I18 rollback_request
I03 api_usage_question         I11 deployment_failure      I19 security_incident
I04 authentication_failure     I12 feature_request         I20 sso_configuration
I05 billing_query              I13 integration_help        I21 unclear_request
I06 compliance_request         I14 onboarding              I22 webhook_issue
I07 configuration_help         I15 performance_degradation
I08 data_export                I16 quota_or_overage
```

```text
Rows = actual; columns = predicted. Values are ticket counts.
Actual\\Pred I01 I02 I03 I04 I05 I06 I07 I08 I09 I10 I11 I12 I13 I14 I15 I16 I17 I18 I19 I20 I21 I22 Support
I01           4   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0       4
I02           0   6   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0       6
I03           0   0   4   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0       4
I04           0   0   0   3   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0       3
I05           0   0   0   0  10   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0      10
I06           0   0   0   0   0   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0       1
I07           0   0   0   0   0   0   3   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0       3
I08           0   0   0   0   0   0   0   1   0   0   0   0   0   0   0   0   0   0   0   0   0   0       1
I09           0   0   0   0   0   0   0   0   6   0   0   0   0   0   0   0   0   0   0   0   0   0       6
I10           0   0   0   0   0   0   0   0   0   1   0   0   0   0   0   0   0   0   0   0   0   0       1
I11           0   0   0   0   0   0   0   0   0   0   5   0   0   0   0   0   0   0   0   0   0   0       5
I12           0   0   0   0   0   0   0   0   0   0   0   3   0   0   0   0   0   0   0   0   0   0       3
I13           0   0   0   0   0   0   0   0   0   0   0   0   3   0   0   0   0   0   0   0   0   0       3
I14           0   0   0   0   0   0   0   0   0   0   0   0   0   4   0   0   0   0   0   0   0   0       4
I15           0   0   0   0   0   0   0   0   0   0   0   0   0   0   3   0   0   0   0   0   0   0       3
I16           0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   2   0   0   0   0   0   0       2
I17           0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   0   0   0   0   0       1
I18           0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   6   0   0   0   0       6
I19           0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   4   0   0   0       4
I20           0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   1   0   0       1
I21           0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   6   0       6
I22           0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   3       3
```

All 80 intent predictions are on the diagonal. Each of the 22 represented classes has
precision, recall, and F1 of 1.000; per-class supports are the final column. Derived
intent accuracy and macro precision are both 100.0%, matching the preserved rerun
metrics.

## Urgency classification matrix

```text
Rows = actual; columns = predicted. Values are ticket counts.
Actual\\Pred  high  medium  low  Support
high             9       9    7       25
medium           9      17    9       35
low              2      10    8       20
Predicted total 20      36   24       80
```

| Actual urgency | Support | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| high | 25 | 45.0% | 36.0% | 40.0% |
| medium | 35 | 47.2% | 48.6% | 47.9% |
| low | 20 | 33.3% | 40.0% | 36.4% |

The diagonal contains 34 of 80 tickets, producing 42.5% urgency accuracy. Derived
urgency macro F1 is 41.417%, which rounds to the preserved 41.4%; it matches the
authoritative rerun metric. Medium is the most frequently predicted urgency label
(36 predictions); the per-class supports total 80.
