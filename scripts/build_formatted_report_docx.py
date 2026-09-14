"""Augment the approved formatted DOCX with reconciled report evidence.

The retained template is copied; its styles, cover, headers, footers, existing
tables, callouts, and appendix traceability table remain intact.
"""
from copy import deepcopy
from pathlib import Path
import json
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets/report_templates/MimohNaik_Capstone_Report_Formatted.docx"
OUTPUT = ROOT / "output/docx/MimohNaik_Capstone_Report_Formatted.docx"
MATRIX = ROOT / "evaluation/results/validation-confusion-matrices.json"


def no_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    tr_pr.append(el)


def repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def move_before(element, anchor):
    anchor._p.addprevious(element)


def add_before(doc, anchor, text, style=None):
    p = doc.add_paragraph(text, style=style)
    move_before(p._p, anchor)
    return p


def clone_table_format(source, target):
    target._tbl.tblPr.clear()
    target._tbl.tblPr.extend(deepcopy(source._tbl.tblPr))


def add_matrix(doc, anchor, source_table, heading_style, title, rows, cols, values, support):
    add_before(doc, anchor, title, style=heading_style)
    t = doc.add_table(rows=len(rows) + 1, cols=len(cols) + 2)
    clone_table_format(source_table, t)
    headers = ["Actual / Predicted", *cols, "Support"]
    for j, value in enumerate(headers):
        t.cell(0, j).text = value
    repeat_header(t.rows[0])
    no_split(t.rows[0])
    for i, label in enumerate(rows):
        t.cell(i + 1, 0).text = label
        for j, col in enumerate(cols):
            t.cell(i + 1, j + 1).text = str(values[i][j])
        t.cell(i + 1, len(cols) + 1).text = str(support[i])
        no_split(t.rows[i + 1])
    move_before(t._tbl, anchor)


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document(TEMPLATE)
    # Existing Appendix A is the stable insertion anchor; preserve it and
    # Appendix B unchanged after the new preserved-evidence matrices.
    anchor = next(p for p in doc.paragraphs if p.text.startswith("Appendix A"))
    normal = None
    for p in doc.paragraphs:
        if p.text.startswith("The supplied discovery materials"):
            normal = p.style
            break
    normal = normal or doc.paragraphs[8].style
    heading_1 = next(p.style for p in doc.paragraphs if p.text.startswith("1. Executive") and p.style is not None)
    heading_2 = next(p.style for p in doc.paragraphs if p.text.startswith("Discovery Evidence") and p.style is not None)

    additions = [
        ("Rationale for Stack Departures from the Reference Architecture", heading_2),
        ("The Setup Guide provided LangChain/LangGraph, Chroma, BM25, MiniLM, provider access, FastAPI, SQLite, and Pytest as a reference baseline rather than a mandatory frozen stack. Frozen V1 retains FastAPI, SQLite, Pytest, MiniLM embeddings, provider-neutral generation, and monitoring/governance assets. It replaces LangChain/LangGraph with explicit Python orchestration and Chroma/BM25 with NumPy exact-cosine retrieval over section-aware chunks. These departures reduce dependency and operating complexity while retaining inspectable stages, source identifiers, deterministic routing, and the required no-result outcome.", normal),
        ("The selection record compares MiniLM with BGE-small and E5-small on development retrieval checks. MiniLM was retained because it had the strongest recorded Recall@3 selection result with lower experiment latency and parameter footprint. This development selection does not replace the authoritative validation retrieval evidence: Recall@1/@3/@5 76.4%/87.7%/88.7%, Precision@1/@3/@5 90.6%/36.8%/25.6%, and MRR 92.8% on the 53 eligible validation tickets.", normal),
        ("Evaluation Integrity and Evidence Boundaries", heading_1),
        ("The first validation attempt is preserved as an embedding-cache/token-path infrastructure failure. Infrastructure-only remediation retained the frozen V1 fingerprint and did not tune behaviour. The owner authorized one disclosed 80-ticket technical rerun, which is the authoritative usable validation evidence. The harness accepts arbitrary input sizes; it hard-codes neither 80 nor 120.", normal),
        ("Evaluation integrity is maintained through population boundaries and preserved artifacts. Development data was permitted for design, component comparison, segmented analysis, and the separate human-development review. The supplied validation data was not used to tune frozen V1; it is used here only through the authorized technical rerun. The hidden assessment was not accessed or reconstructed, and the evaluation harness is dataset-size agnostic rather than keyed to 80 or 120 tickets.", normal),
        ("The rerun retains machine-readable and human-readable reconciliation records. Classification metrics include precision, recall, F1, and preserved confusion matrices; retrieval uses eligible-ticket denominators; routing, automation, escalation, failures, latency, decision logging, and calibration are recorded separately. A retrieval score is not a customer-resolution rate, local sequential latency is not first-response time, and a CI result is not availability evidence.", normal),
        ("PRD Revision and Evidence-Led Change", heading_1),
        ("The revision record preserves the original requirement intent while correcting assumptions contradicted by implementation and evidence. Earlier wording that treated Chroma, BM25, or LangGraph as frozen implementation was withdrawn. The final PRD records the actual MiniLM-plus-NumPy retrieval and explicit Python orchestration as justified departures from baseline options, while retaining outcome requirements for identifiable authoritative passages, measured retrieval quality, deterministic routing, blocking safety controls, and auditable logging.", normal),
        ("The revision also records the evidence that changed deployment interpretation. Strong retrieval and development citation evidence did not establish useful responses; development usefulness remained 2.87/5. Development calibration improvement did not demonstrate safe automation; V2 remained rejected. Validation showed weak urgency, poor calibration, 0% automation, and 100% escalation. These facts update release posture without rewriting discovery as though later results were known at the outset.", normal),
        ("Supervised-Pilot Evidence Boundary", heading_1),
        ("The proposed pilot is an evidence-gathering deployment boundary, not a relabelling of the technical rerun. The rerun did not observe customers, operator workload, first-response time, resolution, CSAT, FCR, availability, recovery, alert delivery, or customer-group response quality. Those measures retain their current NOT MEASURED or NOT PROVEN classifications until a separately defined pilot population produces them.", normal),
        ("Within a limited supervised setting, the fail-closed route, escalation context, decision log, and kill switch are implementation controls that keep human reviewers responsible for customer-impacting outcomes. Each terminal action must remain reviewable; escalation is a safety decision, not evidence that an issue was resolved. The owner recommendation preserves a distinction between supervised evidence gathering and authorizing an autonomous support service.", normal),
        ("Weak urgency performance, high calibration error, zero observed V1 automation, and low development usefulness are reasons to monitor and constrain use, not values to tune retrospectively against held-out validation evidence. Functional private-data blocking tests and preliminary segmentation are useful safeguards and signals for review, but they do not demonstrate a released-response privacy outcome or a passed fairness gate.", normal),
    ]
    for text, style in additions:
        add_before(doc, anchor, text, style=style)

    payload = json.loads(MATRIX.read_text(encoding="utf-8"))
    labels = payload["intent"]["labels"]
    matrix = payload["intent"]["matrix"]
    support = [payload["intent"]["per_class"][label]["support"] for label in labels]
    # Preserve all 22 actual/predicted classes using four readable blocks.
    for actual_start, pred_start in ((0,0),(0,11),(11,0),(11,11)):
        actual = labels[actual_start:actual_start+11]
        predicted = labels[pred_start:pred_start+11]
        values = [matrix[labels.index(a)][pred_start:pred_start+11] for a in actual]
        supports = [support[labels.index(a)] for a in actual]
        add_matrix(doc, anchor, doc.tables[35], heading_2,
                   f"A.1 Intent confusion matrix - actual {actual[0]}-{actual[-1]}; predicted {predicted[0]}-{predicted[-1]}",
                   actual, predicted, values, supports)
    add_before(doc, anchor, "All 80 intent predictions are on the diagonal. Each represented class has precision, recall, and F1 of 1.000; derived macro precision is 100.0%.", style=normal)

    for table in doc.tables:
        for row in table.rows:
            no_split(row)
    doc.save(OUTPUT)


if __name__ == '__main__':
    main()
