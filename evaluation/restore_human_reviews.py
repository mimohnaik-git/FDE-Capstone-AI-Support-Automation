"""Restore completed reviewer forms from the project-owner supplied transcript."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from evaluation.human_review import REVIEW_FIELDS

ROW = re.compile(
    r"^(HDE-\d{3}) \| (?:A=)?(No|Yes) \| (?:B=)?(Yes|No) \| "
    r"(?:C=)?([1-5]) \| (?:D=)?([1-5]) \| (.+)$"
)


def parse_review_transcript(text: str) -> dict[str, dict]:
    reviewers = {
        "reviewer-1": {"schema_version": "1.0", "evidence_classification": "HUMAN DEVELOPMENT EVALUATION", "reviewer_id": "reviewer-1", "independent_review_confirmed": True, "reviews": []},
        "reviewer-2": {"schema_version": "1.0", "evidence_classification": "HUMAN DEVELOPMENT EVALUATION", "reviewer_id": "reviewer-2", "independent_review_confirmed": True, "reviews": []},
    }
    active = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == "# REVIEWER 1":
            active = "reviewer-1"
            continue
        if line == "# REVIEWER 2":
            active = "reviewer-2"
            continue
        if line.startswith("# VALIDATE COMPLETED FILES"):
            active = None
        match = ROW.fullmatch(line) if active else None
        if not match:
            continue
        sample_id, unsupported, citation, correctness, usefulness, notes = match.groups()
        reviewers[active]["reviews"].append({
            "sample_id": sample_id,
            "unsupported_claim_present": unsupported == "Yes",
            "citation_supports_claim": citation == "Yes",
            "response_correctness_score": int(correctness),
            "response_usefulness_score": int(usefulness),
            "reviewer_notes": notes,
        })
    expected = {f"HDE-{number:03d}" for number in range(1, 51)}
    for reviewer_id, form in reviewers.items():
        ids = [row["sample_id"] for row in form["reviews"]]
        if len(ids) != 50 or len(set(ids)) != 50 or set(ids) != expected:
            raise ValueError(f"{reviewer_id} transcript is incomplete or duplicated")
        if any(any(row.get(field) is None for field in REVIEW_FIELDS) for row in form["reviews"]):
            raise ValueError(f"{reviewer_id} contains a null required judgment")
    return reviewers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("evaluation/results/human-development-evaluation"))
    args = parser.parse_args()
    forms = parse_review_transcript(args.source.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for reviewer_id, form in forms.items():
        path = args.output_dir / f"{reviewer_id}-completed.json"
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite completed evidence: {path}")
        path.write_text(json.dumps(form, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
