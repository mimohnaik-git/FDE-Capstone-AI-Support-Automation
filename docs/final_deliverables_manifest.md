# Final Deliverables Manifest

Audit date: 12 September 2026. This is an inventory, not a claim that the submission
archive has been assembled. The required top-level submission folders do not currently
exist. `scripts/create_submission_package.py` now uses the correct fourth folder name,
but it has not been run because required final deliverables are missing and the archive
must use the project owner's enrolment name.

Status terms: **READY** means evidence content exists; **PARTIAL** means content exists
but is stale, incomplete, or in the wrong format; **MISSING** means the required final
artifact does not exist; **OWNER ACTION** means the project owner must supply or approve
the final judgement/output.

## Required archive contract

The final archive must be named `FirstnameLastname_Capstone_Submission.zip`, with the
project owner's exact enrolment name, no spaces, dates, or version suffixes. It must not
contain a wrapper directory and must have exactly:

```text
01_Video/
02_Report/
03_Workbooks/
04_Source_Code/
```

Current status: **MISSING**. None of these four top-level submission directories exists
at repository root, and no compliant enrolment-name archive exists.

## Content audit

| Deliverable | Current evidence/input | Required final destination | Status | Audit finding/action |
|---|---|---|---|---|
| Discovery artifacts | `docs/stage_1_discovery_workbook.md`; stakeholder and dataset source files in `capstone_pack/05_Datasets/` | Workbook/report appendices | READY | Owner review is complete; reconcile remaining workbook-template gaps before export. |
| PRD v1 | `docs/stage_2_prd_template.md` | Report/workbook evidence | PARTIAL | Completed Markdown content exists, but it still names Chroma/BM25 and other superseded design assumptions. Reconcile before export. |
| Prompt/specification artifacts | `docs/stage_3_prompt_library.md`; `prompts/`; Build Specification in `capstone_pack/01_Read_First/` | Report appendices and `04_Source_Code/` | READY | Preserve versions; verify the report distinguishes reference prompts from frozen production prompt. |
| Requirements traceability | `docs/requirements_traceability.md` | `04_Source_Code/docs/` and report appendix | READY | Current implementation statuses and operational NOT MEASURED boundary are recorded. |
| Architecture documentation | `docs/architecture.md`; `docs/architecture_decisions.md`; `docs/technical_defense_qa.md` | `04_Source_Code/docs/` and report | READY | Current MiniLM/NumPy/direct-Python design is documented. |
| Evaluation evidence | Stage 9–16 JSON/Markdown and freeze manifests under `evaluation/results/` | `04_Source_Code/evaluation/` and report appendix | READY | Preserve Stage 13 and Stage 16 artifacts and disclose the rerun. Decision SQLite files are ignored runtime evidence and require an explicit packaging decision. |
| Fairness evidence | `evaluation/results/stage18-fairness.json` and `.md` | `04_Source_Code/evaluation/` and report | READY | Underpowered groups remain NOT MEASURED. |
| Human-review evidence | `evaluation/results/stage18-human-evaluation.json` and `.md`; sample/reviewer files under `human-development-evaluation/` | `04_Source_Code/evaluation/` and report | READY | State 2% hallucination and 98% semantic citation accuracy as HUMAN DEVELOPMENT EVALUATION only. Preserve raw completed reviews. |
| Governance | `docs/governance.md`; monitoring configuration; kill-switch implementation/tests | `04_Source_Code/` and report | READY | Operational performance remains NOT MEASURED. |
| PRD revision / PRD v2 | `docs/stage_5_prd_revision_log.md`; `docs/prd_v2.md` | Workbook/report requirements-revision section | READY FOR EXPORT | The revision log reconciles frozen V1, the authorized 80-ticket rerun, rejected V2, owner approval, and latest hosted CI. No new V2 implementation is authorized. Export remains outstanding. |
| Workbook 1 | `docs/stage_1_discovery_workbook.md` plus blank/source DOCX template | `03_Workbooks/` | PARTIAL | Filled Markdown exists; submission-ready completed workbook file has not been produced. |
| Workbook 2 | `docs/stage_2_prd_template.md` plus blank/source DOCX template | `03_Workbooks/` | PARTIAL | Filled Markdown exists but contains stale architecture claims; no final completed export. |
| Workbook 3 | `docs/stage_3_prompt_library.md` plus blank/source DOCX template | `03_Workbooks/` | PARTIAL | Filled Markdown exists; no final completed export. |
| Workbook 4 | `docs/stage_4_sprint_plan.md` plus blank/source DOCX template | `03_Workbooks/` | PARTIAL | Filled Markdown exists; no final completed export. |
| Workbook 5 | `docs/stage_5_prd_revision_log.md` plus blank/source DOCX template | `03_Workbooks/` | PARTIAL | Reconciled Markdown is export-ready; final completed workbook export is outstanding. |
| Effort log | `docs/effort_log.md`; source template `capstone_pack/04_Submission/Effort_Log.docx` | `03_Workbooks/FirstnameLastname_Effort_Log.pdf` | PARTIAL | Owner-approved 42.0-hour reconstructed estimate is documented with its evidence boundary. The required PDF export is outstanding. |
| AI-use declaration | `docs/ai_use_declaration.md` | Report and/or workbook evidence | READY | Confirmed tools, corrections/overrides, owner responsibility, name, and date are recorded. Include it in the report/package. |
| Final report input | `docs/final_capstone_report.md`; claim/evidence registers | `02_Report/FirstnameLastname_Capstone_Report.pdf` | PARTIAL | Owner review/sign-off is complete and claims are reconciled. The required single 20–30 page PDF must still be produced and inspected. |
| Video/demo input | `docs/video_presentation_script.md`; README/API/evidence artifacts | `01_Video/FirstnameLastname_Capstone_Video.mp4` or link text file | PARTIAL | Current evidence-aware script exists; no recording/link exists. Required 18–22 minute, 1080p video must include presenter visibility and >=7 minutes of live demonstration. |
| Complete source repository | Repository root, `.github/workflows/ci.yml`, README, source/tests/evaluation/docs/data | `04_Source_Code/` | PARTIAL | Local clean-clone proof exists. GitHub Actions CI run `34683618597` succeeded on `main` commit `1186641c253b5d6531f8dc0e739a015970e9dc37`, including checkout, Python 3.12 setup, dependency installation, `pip check`, offline clean-checkout smoke, and pytest. This is CI evidence, not availability evidence. The packaging script does not include `.git` history; decide how assessors will receive reviewable history. |
| Final archive | None | `FirstnameLastname_Capstone_Submission.zip` | MISSING | Requires owner name and all final files above. Do not create until contents are final and reviewed. |

## Frozen evidence preservation baseline

These files were hashed during this audit and must not be overwritten:

| Artifact | SHA-256 |
|---|---|
| `validation-final.json` | `ae2e2037139e55b6ea0a8180ceb3b0299dce850e052505d69232a2328050758f` |
| `validation-final.md` | `ebafde60f216bacfdc0dc9da361a3fecfad8a68b8bf94299d835fac4da03ab07` |
| Stage 13 decision database | `262ddc6b4aa993971ed630b751fcea8b9cbe11f06c8925ec03fe7426478c049f` |
| `validation-technical-rerun.json` | `e4d2ac41588df8fadc985190c86da3412eb66ad9442ddb57b1f8772ddacd7725` |
| `validation-technical-rerun.md` | `0ff2a2000f0ca42f2771eda2995dcd41b490e2be3720e2c500c34569fda97691` |
| Stage 16 decision database | `fd5a7479c3d5db5dc99777c9bc9e071d64d087b3759a217f4f7d3d9362cb9d1f` |
| `stage18-human-evaluation.json` | `e42124b0eef095fc7d8c02361c5858abceaf4bcba1ae160bab4599469537fd45` |
| `stage18-human-evaluation.md` | `6602255e86983b86e7ff6b9b695e63ac64e3fe4825498f85a21a445f6983c8e5` |
| `stage20-v2-development.json` | `11e49ba834e7b8e6a9f5ad3eafbe21d3915db38167c4c3e7ac5ff6c044df86ae` |

## Packaging blockers

1. Final MP4 or video-link text file is missing.
2. Final 20–30 page PDF report is missing.
3. Five completed, reconciled submission-format workbooks are missing.
4. The required updated effort-log PDF is missing.
5. PRD v1 and Stages 1–4 workbook content require reconciliation before final workbook
   exports; the Stage 5 revision log is reconciled.
6. The project owner's exact enrolment-name formatting for required filenames/archive
   name cannot be generated without inventing identity data.
7. The final four-folder archive has not been assembled or inspected.
8. A deliberate decision is required on including ignored SQLite decision databases as
    frozen evaluation evidence without treating other runtime DBs as source artifacts.
9. The current package script does not include `.git`; submission packaging therefore
    does not yet provide reviewable commit history.

## Final audit procedure

After the owner resolves the blockers, run the packaging script, then inspect the ZIP
without executing evaluation. Confirm exactly four top-level folders, required filenames,
no wrapper directory, no cache/runtime/secrets, readable PDF/video, five completed
workbooks plus effort log, full repository contents, and preserved evidence hashes.
