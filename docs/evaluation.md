# Evaluation framework implementation

Stage 10 uses the registry in `evaluation/metrics.py` as the authoritative
inventory of metrics, definitions, eligible populations, documented targets,
measurement types, and status rules. Machine output contains the registry,
denominator-aware measurements, flat status assessments, evidence provenance,
limitations, and reconciliation status. The unattended harness also writes a
Markdown report.

Only `PASS`, `FAIL`, `NOT MEASURED`, `NOT APPLICABLE`, and
`MEASURED — NO FORMAL TARGET` are valid statuses. A missing value or a zero
eligible denominator is `NOT MEASURED`, never `PASS`.

Automated measures include intent and urgency classification metrics,
Recall@1/3/5, Precision@1/3/5, MRR, routing and automation measures, guardrail
coverage, processing failures, decision-log coverage, citation ID validity,
calibration, and P50/P95 pipeline latency. Citation ID validity is an identifier
resolution check and is not semantic citation accuracy.

Hallucination rate, semantic citation accuracy, response correctness, and
response usefulness require real human review. `evaluation/human_review_template.json`
is intentionally blank. FCR, customer first-response time, CSAT, availability,
and repeat contacts require operational evidence and are not inferred from
pipeline timing, routing outcomes, or historical fields in the supplied data.

Run from the repository root:

    python -m evaluation.harness --input <tickets.json> --output evaluation/results/run.json --dataset-role development

Use `validation` or `final` only for a deliberately authorized run of that
evidence class. Development, validation, and final results must remain separate.

## Stage 11 calibration

Stage 11 uses `evaluation/calibration.py` and only the configured development
dataset. A deterministic five-fold stratified group split assigns three folds
to training, one to policy calibration, and one to confirmation. Normalized
duplicate text groups cannot cross populations. Candidate thresholds are
selected on calibration evidence and checked on the untouched development
evaluation fold.

    python -m evaluation.calibration

The command writes `evaluation/results/stage11-calibration.json` and a companion
Markdown report. Production defaults change only when a viable policy has zero
false auto-responses, zero must-not-auto-respond violations, and zero true
high-risk violations on both held-out populations.

## Stage 12 validation freeze

Development tuning is complete. Stage 11 retained classification confidence
`0.80` and retrieval routing `0.30` because no nontrivial policy satisfied all
safety constraints. `evaluation/results/stage12-freeze-manifest.json` records
the frozen production/evaluation configuration and practical fingerprints.

Validation remains untouched. Readiness preflight checks only the validation
path's existence and never reads, parses, counts, or fingerprints its content.
The fingerprint and ticket count are produced only by a later, explicitly
authorized execution. Any post-validation tuning invalidates the validation
claim and requires a newly isolated validation set.

    python -m evaluation.harness --input data/raw/validation_tickets.json --output evaluation/results/validation-final.json --dataset-role validation --preflight

Frozen one-shot command, documented but not executed in Stage 12:

    python -m evaluation.harness --input data/raw/validation_tickets.json --output evaluation/results/validation-final.json --dataset-role validation
