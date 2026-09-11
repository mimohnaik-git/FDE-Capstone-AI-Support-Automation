# Stage 11 Confidence Calibration and Routing Threshold Selection

## Calibration Method

Evidence class: **DEVELOPMENT**. The unchanged classifier was fit on 305 tickets. Policy selection used 95 disjoint calibration tickets; confirmation used 100 disjoint evaluation tickets. Probabilities were measured, not transformed.

## Leakage Check

- Group key: normalized lowercase subject+body with collapsed whitespace
- Train/calibration overlap: 0
- Train/evaluation overlap: 0
- Calibration/evaluation overlap: 0
- Split assignment SHA-256: `d9b91a05a76b94f87bbdf9511993a4cc744aeaac8455d11bd1394f1b4c869810`
- Validation or final data loaded: `False`

## Calibration Metrics

| Population | Tickets | Expected calibration error |
| :--- | ---: | ---: |
| Calibration | 95 | 59.5% |
| Evaluation | 100 | 56.8% |

Reliability buckets and per-intent confidence behavior (minimum five examples) are recorded in the machine-readable result.

## Threshold Grid

| Class threshold | Retrieval threshold | Route accuracy | Auto precision | Auto recall | Automation | Escalation | False auto | False escalation | Must-not violations | High-risk violations | Safety satisfied |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| 0.30 | 0.30 | 69.5% | 83.6% | 75.7% | 70.5% | 29.5% | 11 | 18 | 0 | 0 | False |
| 0.30 | 0.40 | 69.5% | 83.6% | 75.7% | 70.5% | 29.5% | 11 | 18 | 0 | 0 | False |
| 0.30 | 0.50 | 65.3% | 82.5% | 70.3% | 66.3% | 33.7% | 11 | 22 | 0 | 0 | False |
| 0.30 | 0.60 | 50.5% | 81.4% | 47.3% | 45.3% | 54.7% | 8 | 39 | 0 | 0 | False |
| 0.40 | 0.30 | 60.0% | 84.6% | 59.5% | 54.7% | 45.3% | 8 | 30 | 0 | 0 | False |
| 0.40 | 0.40 | 60.0% | 84.6% | 59.5% | 54.7% | 45.3% | 8 | 30 | 0 | 0 | False |
| 0.40 | 0.50 | 55.8% | 83.3% | 54.1% | 50.5% | 49.5% | 8 | 34 | 0 | 0 | False |
| 0.40 | 0.60 | 46.3% | 81.1% | 40.5% | 38.9% | 61.1% | 7 | 44 | 0 | 0 | False |
| 0.50 | 0.30 | 36.8% | 88.9% | 21.6% | 18.9% | 81.1% | 2 | 58 | 0 | 0 | False |
| 0.50 | 0.40 | 36.8% | 88.9% | 21.6% | 18.9% | 81.1% | 2 | 58 | 0 | 0 | False |
| 0.50 | 0.50 | 34.7% | 87.5% | 18.9% | 16.8% | 83.2% | 2 | 60 | 0 | 0 | False |
| 0.50 | 0.60 | 27.4% | 77.8% | 9.5% | 9.5% | 90.5% | 2 | 67 | 0 | 0 | False |
| 0.60 | 0.30 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.60 | 0.40 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.60 | 0.50 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.60 | 0.60 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.70 | 0.30 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.70 | 0.40 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.70 | 0.50 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.70 | 0.60 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.80 | 0.30 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.80 | 0.40 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.80 | 0.50 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |
| 0.80 | 0.60 | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 | True |

## Candidate Policies

| Policy | Class / retrieval | Calibration automation | Evaluation automation | Evaluation safety |
| :--- | :--- | ---: | ---: | :---: |
| Safest viable candidate (fails strict safety if False below) | 0.50 / 0.40 | 18.9% | 26.0% | False |
| Best balanced candidate | 0.30 / 0.30 | 70.5% | 74.0% | False |
| Highest automation satisfying strict safety | 0.60 / 0.30 | 0.0% | 0.0% | True |

## Selected Thresholds

- Status: **CURRENT_DEFAULTS_RETAINED_INSUFFICIENT_EVIDENCE**
- Old thresholds: classification 0.80; retrieval 0.30
- New thresholds: none
- Production configuration changed: `False`
- Evidence: Calibration-fold selection and disjoint development evaluation-fold confirmation.
- Trade-off: Safety constraints are mandatory; higher escalation is accepted rather than unsafe automation.

## Safety Results

Safety-constrained candidates require zero false auto-responses, zero must-not-auto-respond violations, and zero true high-risk violations. The escalation target is not used as a selection constraint.

## Routing Metrics After Calibration

The unchanged current defaults reproduce the following behavior:

| Population | Route accuracy | Auto precision | Auto recall | Automation | Escalation | False auto | False escalation | Must-not violations | High-risk violations |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Calibration | 22.1% | - | 0.0% | 0.0% | 100.0% | 0 | 74 | 0 | 0 |
| Evaluation | 44.0% | - | 0.0% | 0.0% | 100.0% | 0 | 56 | 0 | 0 |

## Remaining Risks

- This is development evidence, not validation or final evidence.
- Small per-intent populations limit intent-specific calibration conclusions.
- Urgency remains weak but is not a routing input, so it was not redesigned in this stage.
