# Durable YouTube workflow design review

Reviewed November 14, 2026. Scope: extend the installed analyze-youtube skill, preserving acquisition, promotion removal, coverage validation and presentation behavior. No upstream skill was installed or executed.

## Evidence and choices

- [ICM Architect entrypoint](https://github.com/RinDig/icm-architect/blob/main/SKILL.md) informed checked sequencing and selective input loading. This adaptation uses one agent and file checkpoints; it makes no claim of measured token savings or superiority over other orchestration.
- [Core contracts](https://github.com/RinDig/icm-architect/blob/main/references/core.md) informed explicit stage inputs, outputs and checks. Contracts stay in a maintained reference; each run stores its outputs and check receipts. This avoids copying a large instruction factory into every video record.
- [Source bundles](https://github.com/RinDig/icm-architect/blob/main/references/bundle-from-sources.md) informed separate original speech, claim verdicts, interpretation and cited knowledge units. Exact optional quotes are checked against retained segment text. Paraphrase fidelity still requires agent review.
- [Forms](https://github.com/RinDig/icm-architect/blob/main/references/forms.md) informed a small pipeline within a per-video record library. Generated indexes route to completed exports; raw runs stay outside the retrieval boundary.

The upstream MIT license was inspected. Implementation and wording were authored for this workflow; no upstream scripts, templates or substantial source text were copied. Universal anonymization, mandatory human approval at each slice, broad folder restructuring and a fixed token ceiling were not adopted: they do not fit the requested automatic video-analysis workflow. Bounded reads and deliberate stage selection provide context control without claiming a measured token budget.

Alternatives considered: keep temporary-only processing (loses resumption and future retrieval); store everything in the installed skill (mixes recipe and user knowledge); immediately add a vector database/chatbot (unspecified system and unnecessary dependencies). Chosen approach: standard-library durable storage, portable Markdown/JSONL, and explicit later integration.

## Skill interactions

Reviewed the entire session-available catalog’s names, descriptions and declared scope, plus the target’s UI metadata. Read analyze-youtube, skill-creator, research-backed-skill-builder, skill-deconfliction, feature-branch, task-research and repository-navigation in depth. No additional installed skill inventory or unavailable invocation policies are claimed.

Ownership remains scoped: analyze-youtube owns speech acquisition, automatic promotion removal, staged analysis and knowledge exports. Research-backed-skill-builder owns evidence methods when its trigger applies; findings are reused. Task-research owns uncertain practical approach comparisons, excluding skill authoring. Repository-navigation remains read-only code tracing, not a knowledge library builder. Artifact, website and template skills keep their format/product deliverables. No broad ICM architect trigger was added, and no neighboring skill required a compatibility edit. Existing invocation policy remains unchanged.

Static walkthroughs: a summary request selects durable stages; context loss resumes the first pending/stale stage; an explicit disposable request retains legacy deletion; a bare URL does not trigger acquisition; mixed video/research work reuses fact checking; a future chatbot request requires a named target and separate integration scope. Conversational timestamp suppression no longer conflicts with durable evidence timestamps. No unresolved scope conflict was found.

## Validation and limits

Executed transcript/retrieval tests and durable fixture tests, including export routing, source separation, original timestamps, revision retention, stale-input rejection, exact quotes, epistemic statuses, read coverage, failed verdicts and corruption filtering. The tests mock acquisition/network services; they do not establish live YouTube availability, semantic analysis quality or external source credibility. The protected skill validator checks packaging/frontmatter; it does not establish behavioral quality.

The ordinary system interpreter lacked PyYAML for the bundled validator; the installed protected validator succeeded. No dependency was installed for validation. The user-selected library was initialized separately from customization source, with no video data or chatbot integration. No independent agent evaluation was performed.

## Collection extension — November 21, 2026

The user explicitly selected amendment of analyze-youtube. Reviewed the session
skill catalog and read skill-creator, skill-deconfliction, feature-branch,
research-backed-skill-builder, task-research, repository-navigation and
code-change-verification alongside the existing entrypoint/durable implementation.
Only analyze-youtube needed changes. Task-research excludes skill authoring;
research owns method evidence, artifact skills own document parsing when relevant,
and analyze-youtube owns this transcript-centered collection. Supporting document
snapshots do not add a general document-analysis trigger. No invocation policy changed.

Reopened both original open-access methods papers; no paper text or implementation
was copied. [Gale et al. (2013)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3848812/)
informs the shared coding framework, contextual evidence charting and within/across
case comparison. [Thomas and Harden (2008)](https://link.springer.com/article/10.1186/1471-2288-8-45)
informs separating descriptive observations from analytical interpretations, with
traceable links. These health-research methods inform an adaptation for transcripts;
they do not demonstrate effectiveness for investment analysis or certify this workflow.
The handoff's Cochrane overview was not necessary to settle these design choices;
its reported access restriction remains unresolved, and no claim relies on it.

Chose a separate standard-library collection helper rather than changing the existing
video schema, duplicating cleaned transcripts per question, or building a database.
Shared inventory/framework/evidence/comparison feed independent purpose folders.
Hash receipts conservatively invalidate downstream work; changing one question
preserves other purposes. Content-based export revisions retain prior conclusions.
Working stage documents are current-state artifacts; major draft history is explicitly
agent-maintained, while exported revisions are retained automatically.

Walkthroughs: a normal video summary stays on five stages; channel research reuses
prepared per-video runs; a second analytical purpose reuses evidence; revised codes
stale comparison/purposes; changed source text stales all dependent work; a document
alone does not broaden skill discovery; a chatbot request remains separate. No
unresolved ownership conflict or neighboring skill edit was identified. This is a
targeted interaction review, not an executed audit of the entire installed skill set.

Collection fixture tests cover staged creation, source preparation reuse, promotion
exclusion, original timestamps/document locators, purpose independence, shared and
question invalidation, revision retention, corruption filtering, quote/coverage and
certainty rejection, path boundaries, CLI routing and bounded reads. Existing video
tests remain applicable. Tests use temporary data and mocked acquisition; no private
library, vault, live channel analysis or paid service was used. Mechanical checks do
not evaluate interpretation quality, detect every leaked promotion, or establish
external source credibility. No independent agent evaluation was performed.
