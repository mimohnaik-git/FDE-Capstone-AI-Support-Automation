# Product Requirements Document Version 2 — CloudServe Support Automation

## Purpose and current decision

This version reconciles the original requirements with measured project evidence through
Stage 23. It does not change frozen V1 or authorize production. V1 remains the current
technical baseline because the development-only V2 candidate improved calibration but
failed the zero-false-automatic-response safety rule.

## Evidence summary

| Area | Observed evidence | Product implication |
|---|---|---|
| V1 routing | Validation automation 0%; escalation 100%; routing accuracy 40%; escalation target <=30% failed. | V1 is fail-closed but does not deliver the intended automation benefit. |
| Classification | Intent macro precision 100%; urgency accuracy 42.5%; urgency macro F1 41.4%; V1 ECE 42.3%. | Intent performance does not offset weak urgency and calibration. |
| Human response review | HUMAN DEVELOPMENT EVALUATION: hallucination 2% (1/50), semantic citation accuracy 98% (49/50), correctness 3.74/5, usefulness 2.87/5. | Grounding/citations met their human-development targets; usefulness has no formal target and requires owner interpretation. These are not validation-release metrics. |
| Fairness | Validation enterprise n=8 and non-fluent n=19 were underpowered; cross-group human quality was not measured. | The governance fairness target remains not measured. No protected attributes were inferred. |
| V2 | Development-only isotonic ECE improved from 63.48% to 3.34%; the selected policy still produced 18 false automatic responses. | V2 is rejected, unvalidated, and not promoted. |
| Operational foundation | Monitoring endpoint/dashboard configuration, governance artifacts, kill switch, CI configuration, and clean-checkout proof are complete locally. | These controls support further work but do not prove production operation. |

## Product objective

Build a controlled support automation system that normalizes four input channels,
classifies requests, retrieves authoritative CloudServe documentation, deterministically
chooses automatic response or escalation, blocks unsafe output, and records an auditable
decision. Automatic release is permitted only when measured evidence supports both
safety and useful customer outcomes.

## Version 2 requirements

| ID | Requirement | Acceptance gate | Current status |
|---|---|---|---|
| PRD2-01 | Preserve email, live chat, documentation comment, and community forum normalization. | All four channels and malformed inputs pass the documented test command. | Implemented and locally tested. |
| PRD2-02 | Produce intent, urgency, and meaningful calibrated confidence. | Intent target retained; owner must approve an urgency target. Calibration error must be <=5 percentage points on governed evidence. | Intent passes validation; urgency and V1 calibration fail. |
| PRD2-03 | Retrieve identifiable authoritative passages and support a no-result outcome. | Retrieval metrics and denominators reported on a governed dataset; no architecture-specific mandate. | Validation Recall@3 87.7% on 53 eligible tickets. |
| PRD2-04 | Make final routing deterministic, auditable, and fail-closed for risk, insufficient evidence, validation failure, and invalid confidence. | Zero false automatic responses and zero must-not-auto violations on the registered release evidence; business automation gate set by owner. | V1 safe by escalation but 0% automated; V2 rejected for false automatic responses. |
| PRD2-05 | Generate only documentation-grounded responses with exact, supportable citations. | Human semantic citation accuracy >=95% and hallucination <=5% on the release-candidate population; validation must contain eligible releases. | Development human evidence passes at 98% and 2%; validation evidence not available. |
| PRD2-06 | Block private-data leakage, prompt-injection effects, unsupported commitments, grounding failure, and citation failure. | Blocking demonstrated; deployed security boundary and abuse controls reviewed before production. | Locally implemented/tested; deployed evidence not available. |
| PRD2-07 | Provide useful structured escalation context. | Completeness tests plus owner-approved operator usability criterion. | Structure implemented; operator usability evidence not available. |
| PRD2-08 | Persist one auditable terminal decision per processed ticket while minimizing sensitive data. | 100% reconciliation; production retention, access, backup, and recovery controls approved. | Validation coverage 100%; production controls incomplete. |
| PRD2-09 | Run unattended evaluation for arbitrary dataset sizes and keep development, validation, human, and operational evidence separate. | JSON and Markdown outputs; no hard-coded ticket count; frozen evidence preserved. | Complete. |
| PRD2-10 | Evaluate fairness only on explicit/registered groups with adequate power. | Minimum group sizes and human-quality outcome defined before execution; underpowered results marked not measured. | Limitations recorded; cross-group human quality not measured. |
| PRD2-11 | Expose health and privacy-safe monitoring and provide a deployment-independent kill switch. | Local tests plus production scrape, alert, access-control, and kill-switch rehearsal evidence. | Local implementation complete; production evidence not available. |
| PRD2-12 | Remain reproducible from a clean checkout with one test command and no secrets. | Fresh-checkout setup, `python -m pytest`, `python -m pip check`, and hosted CI evidence. | Local clean-checkout complete; hosted CI not observed. |

## Production entry gaps

Evidence not available for production availability, FCR, first substantive response time,
CSAT, repeat-contact reduction, representative load behavior, alert delivery/response,
backup and restore, authentication/authorization/rate limiting, live-provider reliability
and cost, fleet-wide kill-switch performance, or named accountable operators. A new
release candidate also needs governed validation with eligible automatic responses and
appropriately powered fairness evidence.

## Owner decisions required

The owner must define or approve: the urgency acceptance target; the minimum useful
automation/pilot threshold; the safety-versus-business trade-off; whether 2.87/5
development usefulness is adequate for further experimentation; pilot versus production
gates; accountable operational owners; and the final business conclusion. No answer is
implied by this draft.
