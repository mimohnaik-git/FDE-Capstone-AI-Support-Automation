# PRD Revision Record — CloudServe Support Automation

## Document control

| Field | Value |
|---|---|
| Revision | 2.0 evidence reconciliation draft |
| Date | 11 September 2026 |
| Scope | Reconcile the original PRD with Stage 18–23 evidence |
| Evidence boundary | Frozen V1 validation, human development evaluation, development-only V2 experiment, and local operational/reproducibility evidence |
| Approval status | Owner review required; no approval is claimed |
| Production decision | Frozen V1 remains unchanged; V2 rejected |

This record supersedes the earlier revision narrative that claimed a BM25 implementation,
a 0.82 threshold, 75 passing tests, and stakeholder approval. Those claims do not describe
the frozen V1 evidence and are withdrawn from the current revision record. The original
source-pack workbooks remain historical inputs and are not altered.

## Requirement changes

| Requirement | Version 1 expectation | Version 2 evidence-based requirement or status | Trigger and evidence | Owner decision |
|---|---|---|---|---|
| FR-02 classification | Intent and urgency classification with intent precision above 85% | Retain intent classification; treat urgency quality and confidence calibration as unresolved quality gaps. Any successor must define urgency acceptance criteria and demonstrate calibration within the governance tolerance before release. | Validation intent macro precision was 100%, but urgency accuracy was 42.5%, urgency macro F1 was 41.4%, and V1 ECE was 42.3%. | Required: decide whether the urgency requirement should be redesigned, retrained, or narrowed. |
| FR-03 retrieval | Chroma plus MiniLM with BM25 fallback and Recall@3 above 85% | Require identifiable authoritative passages and measured retrieval quality without prescribing Chroma or BM25. Frozen V1 uses exact cosine over MiniLM/NumPy. | Validation Recall@3 was 87.7% over 53 eligible tickets. Architecture and clean-checkout evidence contradict the V1 design prescription. | Required: approve outcome-based wording and the recorded stack deviation. |
| FR-04 routing | Safe automatic response or escalation using multi-factor routing | Retain deterministic fail-closed routing, but do not call V1 operationally successful: it produced 0% automation and 100% escalation. A successor may be promoted only after zero false automatic responses under the registered safety rule and a new governed validation cycle. | Validation routing accuracy was 40%; escalation target <=30% failed. Stage 20 V2 policies produced false automatic responses. | Required: set the acceptable business/safety trade-off and pilot gate. |
| FR-05 and FR-06 generation and grounding | Grounded answers with explicit citations and no released hallucinations | Preserve grounding and citation controls. Report response-quality evidence only within its population: human development evaluation, not validation releases. | Two reviewers on 50 development candidates measured hallucination 2% (1/50), semantic citation accuracy 98% (49/50), correctness 3.74/5, and usefulness 2.87/5. Validation released no responses. | Required: interpret whether usefulness is adequate for a future pilot; evidence alone makes no owner conclusion. |
| FR-07 to FR-09 safety | Block private data, injection effects, and unsupported financial commitments | Retain blocking controls and mandatory escalation. Production claims require deployed security and abuse-control evidence. | Unit/integration evidence demonstrates blocking; validation guardrail coverage and private-data release rate were ineligible because no response was released. | Required: approve the production security gate. |
| FR-11 audit logging | Persistent and complete decision records | Retain. Require deployed durability, access control, retention, backup, and recovery evidence before production. | Validation reconciled 80 source/evaluated/terminal/logged records and achieved 100% decision-log coverage. SQLite production durability remains unmeasured. | Required: name the accountable owner and retention/recovery policy. |
| FR-12 evaluation | Unattended automated metrics | Retain arbitrary-size unattended evaluation and explicit evidence classes. Human and operational metrics must never be inferred from automated results. | Evaluation harness, frozen manifests, validation reports, fairness analysis, and human-review artifacts exist. | Required: approve final interpretation; no new run is required for Stage 24. |
| NFR operational readiness | Latency, availability, security, testability, and local operation | Separate locally demonstrated controls from production evidence. Monitoring, governance, CI configuration, and clean-checkout work are complete locally; production availability, load, alerts, access control, recovery, and hosted CI remain gaps. | Stage 19–23 governance, monitoring, traceability, and clean-checkout evidence. | Required: decide which gaps block a pilot versus full production. |

## Assumptions reconciled

| Version 1 assumption | Evidence outcome | Revision |
|---|---|---|
| Documentation answerability would translate into useful automation. | Did not hold for V1 validation: 0% automation and 100% escalation. | Treat answerability, routing safety, and response usefulness as separate gates. |
| Intent confidence was sufficiently calibrated for routing. | Did not hold: V1 ECE was 42.3% on validation. | Require explicit calibration evidence and preserve fail-closed routing. |
| Urgency performance would be adequate alongside intent performance. | Did not hold: validation urgency accuracy was 42.5% and macro F1 was 41.4%. | Make urgency remediation a named product-quality gap. |
| Strong automated citation checks would establish response quality. | Did not hold as a complete claim. Semantic citation support required human review; usefulness averaged 2.87/5. | Keep automated and human evidence distinct and report denominators. |
| The fairness target could be evaluated on supplied data. | Did not hold. Validation enterprise n=8 and non-fluent n=19 were below the registered n=20 minimum; cross-group human quality was not measured. | Require a new, appropriately powered governed dataset and stratified human review. |
| Calibration repair would enable safe non-zero automation. | Partly held for calibration, not routing safety. Development-only isotonic V2 ECE improved from 63.48% to 3.34%, but the selected candidate had 18 false automatic responses. | Reject V2; do not validate or promote it. |
| Local implementation evidence was equivalent to production readiness. | Did not hold. Monitoring, governance, and clean-checkout controls exist, but deployed operational outcomes remain unmeasured. | Add explicit production-entry gaps and owner gates. |

## Deliberately unchanged

- Frozen V1 code, configuration, validation outputs, and fingerprint are unchanged.
- The validation rerun and its disclosed first failed attempt remain preserved.
- V2 remains development-only and rejected; it was not run on validation.
- Historical source workbooks remain source evidence even where their claims are superseded here.

## Evidence references

- `evaluation/results/validation-technical-rerun.md`
- `evaluation/results/stage18-fairness.md`
- `evaluation/results/stage18-human-evaluation.md`
- `evaluation/results/stage20-v2-development.json`
- `docs/governance.md`
- `docs/requirements_traceability.md`
- `docs/evidence_register.md`
- `docs/evidence_gaps.md`

## Owner approval fields

Evidence not available for owner conclusions. Complete the owner interpretation and
reflection worksheets before changing this record to approved. Record the owner's name,
date, decisions, and any wording they reject or override.
