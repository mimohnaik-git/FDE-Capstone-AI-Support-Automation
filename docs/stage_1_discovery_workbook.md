# Stage 1 Discovery Workbook — CloudServe Solutions

## Evidence boundary

This workbook records what was available before implementation: five supplied stakeholder
transcripts and the 500-ticket development dataset. Historical ticket fields describe
the supplied dataset, not outcomes caused by this project. Later validation, human
evaluation, and owner-review evidence is referenced only where it tests or contradicts
an earlier hypothesis.

## 1. What the interviews tell us

| Stakeholder | What they said | What they did not know or could not see | Data question or boundary |
|---|---|---|---|
| Marcus Adeyemi, Head of Support | Volume was above 500 tickets per week for six agents. The service agreement called for first response inside two hours, while he reported an eight-to-twelve-hour average. He cared most about first-contact resolution, described it as about 42%, and cited 65% as an industry benchmark. He preferred no answer to a confidently wrong answer. | He could name broad themes but did not know the distribution. He saw aggregate escalation, not the content or avoidability of individual escalations. | Check historical ticket distribution, FCR, escalation, and documentation answerability in development data. |
| Sofia Restrepo, Tier 1 Agent | She ordered the queue by age. Familiar tickets took about four to five minutes; unusual tickets could take about forty minutes and still escalate. Search and rewriting known answers consumed time, and agents used personal answer files. She raised concern about interpreting non-fluent English tickets. | She could not quantify the language-quality difference. Her personal file was not reviewed documentation. | Check explicit fluency metadata and historical outcomes without treating aggregate averages as a quality study. |
| Daniel Okonkwo, Tier 2 Engineer | About half of tickets reaching Tier 2 appeared answerable by Tier 1 if the agent had confidence or found the right page. Escalations often arrived as raw forwards with no summary. Security, billing disputes, account compromise, and data-location questions were risky to automate. | He did not provide a population-wide escalation classification or time study. | Check escalation and answerability fields; retain high-risk handling as a stakeholder safety requirement. |
| Ines Varga, Technical Writer | Twenty-nine reviewed articles covered recurring topics. Exact-term/title search missed symptom phrasing. Private answer files were unreviewed. Feature requests, roadmap/timing questions, and novel incidents might have no article. | She did not claim every ticket was documented or that a new retrieval method would solve every wording problem. | Check labelled documentation answerability. Treat semantic retrieval as a later design hypothesis. |
| Ravi Menon, Customer | Support was slow but helpful once reached. Delay mattered more for deployment failure than a low-risk question. Automated help could be useful if honest, identified as automated, cited sources, and avoided false certainty. He was concerned tier differences should not worsen. | He represented one customer, not a customer-acceptance study or deployment approval. | Treat transparency, citations, urgency, and tier experience as stakeholder needs, not broad customer approval. |

### Accounts that disagreed or created tension

| Tension | Transcript evidence | Dataset evidence | Discovery interpretation |
|---|---|---|---|
| Documentation coverage versus accessibility | Marcus associated poor outcomes with missing answers; Ines and Sofia described documentation that was difficult to find. | 357/500 tickets (71.4%) were labelled answerable from documentation; 219/500 (43.8%) were marked first-contact resolved. | The historical sample supports a coverage/accessibility gap. It does not prove a particular retrieval design will close it. |
| Language concern versus historical outcomes | Sofia reported extra interpretation effort and poor satisfaction for non-fluent tickets. | 120/500 tickets (24.0%) were marked non-fluent. Their historical FCR was 45.8% and CSAT 3.04/5, versus 43.8% and 2.97/5 overall. | The aggregate fields do not confirm the claimed disadvantage, but they do not measure comprehension, handling time, or answer quality. Language remains a question to investigate. |
| What escalations contain | Daniel described avoidable, context-poor escalations; Marcus focused on aggregate cost and FCR. | **DEVELOPMENT-DATASET DESCRIPTIVE FIELD:** 281/500 (56.2%) records in the supplied development dataset were escalated. Enterprise had the highest development-dataset escalation rate, 62.7%. This is not a historical operational baseline, V1 result, or validation result; the brief historical escalation baseline is 58%. The data does not identify avoidable escalations. | Structured escalation is a stakeholder need. Avoidability and Tier 2 effort were NOT MEASURED. |
| Automation value versus risk | Marcus wanted easy tickets handled faster; Sofia and Ravi emphasized harm from wrong answers; Daniel named risky categories. | Labels identify answerability and expected route, but do not prove safe automatic release. | Discovery supports a controlled, transparent, escalation-capable system, not broad autonomous automation. |

### What nobody said

The transcripts do not provide the following. These are open questions, not inferred
findings.

| Missing evidence | Why it matters | Discovery status |
|---|---|---|
| Measured effort by ticket category or agent hours | Volume alone cannot show where workload is concentrated. | NOT MEASURED |
| Timed breakdown of search, drafting, verification, and escalation | Needed to quantify workflow bottlenecks. | NOT MEASURED |
| Representative customer acceptance of automation | One customer described conditions for trust. | NOT MEASURED |
| Availability, provider reliability, load, alerting, backup, or recovery | These are operational/deployment questions outside discovery evidence. | NOT MEASURED |
| Comparable quality across customer groups | Tier and language concerns were raised, but no discovery quality study was supplied. | NOT MEASURED |

## 2. What the development ticket data shows

Dataset: 500 supplied development tickets. These are historical fields, not V1
validation or production outcomes.

| Measure | Historical value | Source field | Observation and boundary |
|---|---:|---|---|
| Tickets in sample | 500 | Dataset rows | A development sample, not the weekly production-volume claim. |
| Channel mix | Email 212 (42.4%); chat 155 (31.0%); documentation comments 78 (15.6%); forum 55 (11.0%) | channel | Email and chat account for 73.4% of the sample. |
| Intent coverage | 22 labelled categories | labels.intent | Data export and data residency were most frequent at 29 each. |
| Urgency mix | Medium 226 (45.2%); high 146 (29.2%); low 128 (25.6%) | labels.urgency | 74.4% were labelled medium or high. |
| First-contact resolution | 219/500 (43.8%) | history.first_contact_resolution | Historical baseline only; not system-attributable FCR. |
| Escalation | 281/500 (56.2%) | history.escalated | **DEVELOPMENT-DATASET DESCRIPTIVE FIELD** only; not a historical operational baseline, V1 result, or validation result. The brief historical escalation baseline is 58%. |
| CSAT | Mean 2.97/5 | history.csat_rating | Historical baseline only; not V1 or pilot CSAT. |
| Repeat contact | 108/500 (21.6%) | history.repeat_contact | Historical baseline only; not a project outcome. |
| Documentation answerability | 357/500 (71.4%) | labels.answerable_from_docs | A label indicating available documentation, not proof retrieval or automation will succeed. |
| Non-fluent marker | 120/500 (24.0%) | language_fluency | Explicit field only; no protected attributes were inferred. |
| Customer tiers | Standard 253; business 164; enterprise 83 | customer_tier | Supports a later analysis question, not a fairness conclusion. |
| Resolution time | Mean 421.7 minutes; median 214 minutes | history.resolution_time_minutes | Historical resolution time is not first-response time. |

## 3. Where time and effort appear to go

### Effort distribution and workload

Exact effort by category, agent, or workflow stage is **NOT MEASURED**. The dataset has
historical outcomes and resolution times but no agent-hours allocation. Assigning
percentage effort shares to categories would be unsupported.

Qualitative evidence is limited to stakeholder reports: Sofia said familiar tickets
could take four to five minutes and unusual tickets about forty minutes before
escalation; she reported time spent finding documentation and writing answers. Daniel
reported rereading escalation threads and re-asking questions. Marcus reported workload
pressure but supplied no agent-hour study.

### Observed manual workflow

| Step | Evidence-supported description | Time evidence | Discovery implication |
|---|---|---|---|
| Queue triage | Sofia opens the queue, sorts by age, and works down the oldest tickets. | No per-step measurement. | Delay pressure is an operational concern. |
| Interpret request | Sofia decides whether the issue is familiar. | Familiar ticket: about 4–5 minutes total; unusual ticket: up to about 40 minutes total before escalation. | Classification may help, but no saving is assumed. |
| Find information | Agents search documentation or use personal files when search is difficult. | NOT MEASURED separately. | Reviewed documentation must remain distinct from unreviewed material. |
| Draft answer or escalate | Tier 1 writes a response or forwards the ticket; Daniel often reconstructs context. | NOT MEASURED separately. | An evidence-linked escalation summary is a stakeholder need. |
| Decide send or escalate | Sofia escalates unknown, low-confidence, and security cases; Daniel named further risky areas. | NOT MEASURED separately. | Escalation is a legitimate outcome. |

## 4. What the client counts as success

### Historical baselines and stakeholder aspirations

| Measure | Baseline or stakeholder statement | Owner of concern | Boundary |
|---|---|---|---|
| First-contact resolution | 43.8% in development data; Marcus described about 42% and cited 65% as an industry benchmark. | Marcus | Historical baseline and aspiration, not V1 performance. |
| Response timing | Marcus reported a two-hour service agreement and eight-to-twelve-hour average. Ravi described some waits until the next day. | Marcus and Ravi | Stakeholder report; the dataset does not measure first response. |
| Resolution time | Mean historical resolution time was 421.7 minutes. | Development data | Not interchangeable with first-response time. |
| Customer satisfaction | Historical mean CSAT was 2.97/5. | Development data and Ravi | Baseline only; not a system outcome. |
| Escalation quality | Daniel wanted a summary, relevant documentation, and explicit uncertainty. | Daniel | Need only; no baseline completeness rate. |
| Trust in automation | Ravi required transparency, citations, and no false certainty. | Ravi | One perspective; no acceptance-rate measurement. |

### Target types and gates

| Category | Target or gate | Status at discovery |
|---|---|---|
| Business direction | Improve historical FCR and response experience without increasing agent work or sending incorrect answers. | Stakeholder goal, not achieved result. |
| Technical targets | Intent precision ≥85%, citation accuracy ≥95%, hallucination ≤5%, and P95 latency <3 seconds are later project evaluation targets. | Targets, not discovery results. |
| Governance/deployment gates | No private-data release, auditable decisions, investigated group quality, and meaningful confidence calibration. | Design/evaluation gates, not discovery results. |
| Later owner conclusion | Limited supervised pilot; V1 is not production-ready; safety takes priority over automation. | Later owner decision, not discovery evidence. |
| Later owner automation target | 30% minimum worthwhile future automation. | **OWNER TARGET, NOT MEASURED RESULT**; not a discovery finding or V1 result. |

### Sentence test

This project would be worth doing if it improved access to reviewed documentation and
gave agents useful, auditable support context without releasing unsupported or unsafe
answers. Discovery evidence does not establish a future automation rate, customer
outcome, or time saving.

It would not be worthwhile if it increased agent rework, amplified stale personal-answer
content, hid uncertainty, or made unsafe commitments.

## 5. Data, constraints, and initial risks

### Data and constraints

| Source | Contents | Limits and constraints |
|---|---|---|
| Development tickets | 500 labelled historical tickets with text, channel, tier, fluency, labels, and outcome fields. | Development-only evidence. Customer-linked and potentially sensitive text/metadata must not become an authoritative answer source. Historical outcomes are not project outcomes. |
| Support documentation | 29 reviewed knowledge-base articles. | Ines identified gaps for feature requests, roadmap/timing questions, and novel incidents. Review does not prove every question is covered. |
| Stakeholder transcripts | Five role-specific accounts. | Qualitative and limited to supplied speakers; not a representative survey or time study. |
| Validation tickets | A separate supplied validation dataset of 80 tickets. | It must remain separate from discovery, training, and tuning. It was not a discovery input. |
| Operational outcomes | Post-deployment FCR, CSAT, repeat contact, first-response timing, availability, load, and recovery. | System-attributable evidence was unavailable at discovery and remains NOT MEASURED for V1. |

### Initial risk register

| Discovery risk | Evidence | Initial prevention direction | Boundary |
|---|---|---|---|
| Confident but incorrect answer | Marcus, Sofia, and Ravi emphasized harm from wrong answers. | Preserve uncertainty and escalate when evidence is insufficient. | Risk, not measured incident rate. |
| Stale or unreviewed personal content influences replies | Sofia described personal files; Daniel and Ines said such material could be outdated or unreviewed. | Use reviewed documentation as authority. | Stakeholder evidence. |
| Unsafe commitments or high-risk handling | Daniel named security/account compromise, billing disputes, and data-location issues. | Keep human escalation for risky or unsupported cases. | Stakeholder requirement. |
| Documentation does not support a request | Ines named feature requests, roadmap/timing questions, and novel incidents. | Support no-result and escalation outcomes. | Stakeholder evidence. |
| Context-free escalation increases rework | Daniel described raw forwards and repeated questions. | Preserve context, relevant sources, and uncertainty. | No baseline completeness metric. |
| Unequal experience by tier or language variation | Ravi raised tier disparity; Sofia raised language interpretation. | Register explicit fields for later evaluation; do not claim a fairness result. | Concern, not proven disparity. |

Later project evidence did not prove the fairness governance target. It remained
preliminary and underpowered; this is a later limitation, not a discovery conclusion.

## 6. Problem statement traceability

| Problem statement element | Evidence trace |
|---|---|
| Workload and delay pressure | Marcus reported more than 500 tickets per week for six agents, a two-hour agreement, and eight-to-twelve-hour average response. Ravi described waits until the next day. |
| Low historical resolution despite documented answers | Development data: 43.8% historical FCR and 71.4% labelled documentation answerability. |
| Difficulty locating reviewed guidance | Sofia and Ines described difficult search and reliance on personal files; Ines supplied a symptom-versus-title example. |
| Need for auditable, structured escalation | Daniel requested context, relevant documentation, and explicit uncertainty; Marcus required explainability. |
| Need for controlled customer communication | Marcus, Sofia, Ravi, and Daniel described harm from wrong answers or unsafe commitments. |

### One-paragraph problem statement

CloudServe's support team faces workload and response-delay pressure: Marcus reported
more than 500 tickets a week for six agents, a two-hour response agreement, and an
eight-to-twelve-hour average response, while Ravi described waits that could extend until
the next day. In the supplied historical development data, only 43.8% of tickets were
marked resolved on first contact even though 71.4% were labelled answerable from reviewed
documentation. Sofia and Ines described a gap between having reviewed knowledge-base
articles and being able to find them, with agents relying on unreviewed personal answer
files; Daniel described escalations that often lacked context. CloudServe therefore needs
a controlled way to help agents locate reviewed information, communicate uncertainty,
and provide structured escalation context while avoiding unsupported, unsafe, or
unaccountable customer communication.

### Semantic retrieval hypothesis

Language variation was an observed concern raised by Sofia. Semantic retrieval was
selected later as a design hypothesis for matching symptom phrasing to reviewed
documentation. Discovery did not prove that it would bridge language gaps or remove the
need for human review. Later fairness and quality evidence remained preliminary and did
not establish the governance fairness target.

## Owner interpretation boundary

The confirmed owner review records a limited supervised pilot recommendation, V1's
not-production-ready status, and safety-first priority. Those are later owner decisions,
not discovery findings. No additional discovery-specific owner wording is available in
the supplied records.
