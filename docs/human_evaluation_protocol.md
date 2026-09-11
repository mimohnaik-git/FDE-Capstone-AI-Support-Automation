# Human Development Evaluation Protocol

This package is labelled **HUMAN DEVELOPMENT EVALUATION**. It does not measure
validation auto-response performance and contains no completed human ratings.

## Review design

Two distinct reviewers independently assess every response in the supplied sample.
Reviewers must not discuss ratings until both forms are complete. Each reviewer sets
their own `reviewer_id`, sets `independent_review_confirmed` to `true`, and completes
every field without changing sample IDs.

For each response, reviewers inspect the customer request, response candidate,
citations, and retrieved passages:

- `unsupported_claim_present`: `true` when any factual or policy claim lacks support
  in the supplied authoritative passages; otherwise `false`.
- `citation_supports_claim`: `true` when the cited passage semantically supports the
  claim, `false` when it does not, or `not_applicable` only when no claim-citation pair
  exists.
- `response_correctness_score`: integer 1–5, where 1 is materially incorrect and 5
  is fully correct given the supplied evidence.
- `response_usefulness_score`: integer 1–5, where 1 is not actionable/useful and 5
  directly and safely helps address the request.
- `reviewer_notes`: optional concise justification; do not include personal data.

## Formal aggregation

Both forms must cover at least 50 identical sample IDs. The aggregation utility
rejects blank ratings, duplicate reviewer identities, missing independence
confirmation, or fewer than 50 shared reviews. It reports raw inter-reviewer
agreement for the hallucination judgement, hallucination rate, semantic citation
accuracy, and mean correctness/usefulness scores. Any disagreement marks a response
as hallucinated conservatively; a citation is counted supported only when both
reviewers agree it is supported.

Human interpretation and business conclusions remain the project owner's work.
Keep a record of AI assistance used to prepare this protocol for the final AI-use
declaration.
