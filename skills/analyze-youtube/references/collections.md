# Collections: reusable evidence, different analytical purposes

Use this layer for a requested corpus, channel, or iterative comparison across saved
transcripts/documents. Ordinary single-video work keeps the five-stage durable
protocol; do not create a collection merely to summarize one video. This is a
methods-inspired adaptation, not certification, a systematic review claim, or a
mandatory academic methodology. The user’s question determines depth and coverage.

## Storage and routing

Use the same isolated Python and library root as `library.py`, but invoke the
installed absolute `scripts/collection.py` path. No acquisition command exists here:
reuse saved per-video runs after current acquisition/preparation checks. Finish
per-video extraction/verification/export when independently useful; collections do
not require redundant per-video synthesis before cross-source analysis.

```text
ROOT/collections/COLLECTION/
  collection.json, CONTEXT.md
  documents/*.json                 private normalized document snapshots
  01-inventory/inventory.json
  02-framework/framework.json
  03-evidence/evidence.json
  04-comparison/comparison.json
  purposes/PURPOSE/
    purpose.json                  stable ID and current question
    05-memos/memo.json
    06-verification/verification.json
    07-synthesis/synthesis.json
  exports/PURPOSE/REVISION/        analysis.md, claims.json, knowledge.jsonl, metadata.json
  index.json, _index.md            completed, integrity-checked export routing
```

Each stage folder also contains generated `check.md` and `check.json`. Inputs and
incremental drafts belong in their meaningful stage folder. Keep originals in
existing runs or authorized document storage; never alter originals to fit codes.
Documents use collection-local snapshots with passage IDs and page/section locators.
The agent prepares these once using the relevant document-reading workflow; this
helper does not parse PDFs, crawl directories, or acquire documents. Do not ingest
private folders without scope authorization. Raw/clean text remains private.

```sh
PYTHON COLLECTION_SCRIPT --library ROOT create market-history --title 'Market history'
PYTHON COLLECTION_SCRIPT --library ROOT status market-history
PYTHON COLLECTION_SCRIPT --library ROOT save market-history 01-inventory --input ABSOLUTE_INPUT_JSON
PYTHON COLLECTION_SCRIPT --library ROOT check market-history 01-inventory --review 'Actual review findings'
PYTHON COLLECTION_SCRIPT --library ROOT read market-history 01-inventory --offset 0 --limit 30
PYTHON COLLECTION_SCRIPT --library ROOT purpose market-history --purpose techniques --question 'Which research techniques recur?'
PYTHON COLLECTION_SCRIPT --library ROOT status market-history --purpose techniques
PYTHON COLLECTION_SCRIPT --library ROOT save market-history 05-memos --purpose techniques --input ABSOLUTE_INPUT_JSON
PYTHON COLLECTION_SCRIPT --library ROOT check market-history 05-memos --purpose techniques --review 'Actual review findings'
PYTHON COLLECTION_SCRIPT --library ROOT export market-history --purpose techniques
PYTHON COLLECTION_SCRIPT --library ROOT index market-history
```

Repeat save/check for each stage. Input files may be in the selected stage folder;
`save` validates and writes the canonical filename. Never interpolate source prose
into shell commands. IDs use lowercase hyphenated slugs for collection/purpose.
`read` pages the chosen JSON into bounded chunks (maximum 200 × 1000 characters).
Use smaller pages as appropriate; a truncated tool result does not establish reading.
For speech, use `library.py read RUN clean`; for documents, inspect only selected
passages and their neighbors. Start from collection status and source routing, not
all library files. Script validation may scan hashes/coverage; it does not require
loading that content into agent context.

## Stage contracts

### 01-inventory — scope, dates, coverage and gaps

**Inputs:** requested corpus boundary, source metadata, saved clean runs or authorized
normalized documents. **Output:** object with nonempty `scope`, `coverage`, `gaps`,
and `sources` list. Each source has unique string `id`, `kind` (`video` or `document`),
`path`, `title`, `url`, `date`, `coverage`, `limitations`. Use `unknown` explicitly
for missing dates; distinguish publication/event/acquisition dates in limitations.
A video path is an absolute `ROOT/runs/run-UUID`; source URL is its original video.
A document path is `documents/NAME.json`, containing:

```json
{"passages":[{"id":"p1","text":"Retained source passage.","locator":"page 4, section 2"}]}
```

Document IDs are unique nonempty strings; video segment IDs remain original integers.
Retain supplied context and describe omissions, transcription limits and promotion
removal. Apply existing promotion rules to relevant transcripts before registration;
never carry removed advertisements into shared evidence. Do not claim complete
channel coverage based on available captions alone.

**Review:** identity, duplicates, selection bias, missing periods, source availability,
date semantics and the difference between inventory completeness and reading coverage.

### 02-framework — consistent, revisable concepts

**Inputs:** inventory, question and bounded familiarization samples.
**Output:** `revision`, `change_reason`, and `codes` list. Each code has unique `id`,
`definition`, `include`, `exclude` (all nonempty text). Add optional example evidence,
parent code or questions when useful. Seed concepts from the question; allow new
concepts to emerge. Preserve stable code IDs when meaning remains stable.

**Review:** ambiguous boundaries, concepts imposed without support, overlaps, and
whether a framework change requires recoding earlier material. Record the reason;
revisit affected sources rather than acquiring/cleaning everything again.

### 03-evidence — chart source observations by concept

**Inputs:** current framework, clean source passages and context, prior extraction.
**Output:** `items` and `coverage`. Example item:

```json
{"id":"e1","source_id":"video-1","code_ids":["research-process"],
 "passage_ids":[42],"context_ids":[41,43],
 "observation":"Faithful descriptive paraphrase, preserving qualifications.",
 "context":"Question, audience, assumptions and neighboring argument.",
 "role":"qualification","limitations":"Caption uncertainty or selection limits.",
 "quotes":[{"passage_id":42,"text":"Exact retained substring"}]}
```

Roles: `support`, `negative_case`, `qualification`. Keep descriptive observations
separate from analytical interpretation in later stages. Use globally unique evidence
IDs within the collection; source IDs disambiguate identical passage numbers.
`coverage` maps **every** source ID to `status` (`not_started`, `partial`, `complete`),
`read_ids` (original passage IDs actually read), and nonempty `gaps` (`None` if none).
Complete requires all retained passage IDs; partial work can advance with limitations.
Read every selected source passage once, save incremental drafts/progress, and cite
only retained evidence. Record negative cases rather than selecting only confirmation.

**Review:** fidelity, context loss, coding consistency, negative cases, source gaps and
actual reading progress. The helper validates IDs/quotes/coverage, not human reading.

### 04-comparison — relationships across cases and time

**Inputs:** shared evidence, framework and source dates/coverage.
**Output:** `findings` list. Each has `id`, `evidence_ids`, `negative_case_ids` (may be
empty), `relation` (`agreement`, `exception`, `contradiction`, `change_over_time`,
`insufficient`), and nonempty `observation`, `interpretation`, `alternatives`,
`limitations`, `date_context`. An empty findings list is permitted with the reason
in the check review; do not invent comparisons to fill a matrix.

**Review:** within-source versus across-source support, genuine contradiction versus
changed assumptions, event/publication dates, exceptions and missing periods.
Frequency is not truth, absence of mention is not disagreement, and a selected
corpus does not establish population prevalence.

### 05-memos — one purpose at a time

**Inputs:** selected evidence/comparisons and `purpose.json` question.
**Output:** `question` (exact purpose question), `analysis`, `evidence_ids`,
`comparison_ids`, `negative_case_ids`, `alternatives`, `limitations`.
The last two ID lists may be empty. Create separate purposes for research techniques,
investment reasoning or historical change; reuse shared evidence rather than recoding
for each question. If existing codes cannot answer a question, revise the framework
and extraction explicitly. Preserve useful incremental memo drafts inside this folder.

**Review:** question relevance, inference versus description, counterexamples,
competing explanations and whether the selected evidence justifies the scope.

### 06-verification — factual checks and interpretation challenge

**Inputs:** purpose memo, selected evidence and primary external sources as needed.
**Output:** `interpretation_challenge`, `limitations`, `claims` list. Each claim has
`id`, `statement`, `safe_statement`, `kind` (`source_claim`, `interpretation`,
`external_fact`), `status` (`verified`, `disputed`, `uncertain`, `unverified`, `opinion`),
`evidence_ids` (selected by memo), `checked_at`, `limitations`, and `sources` list.
External sources use the durable claim source fields: `url`, `title`, `accessed_at`,
`date_context`, `support`. Verified/disputed statuses require external sources;
interpretations cannot receive verified status. Reuse per-video claim checks where
applicable, preserving their date and scope instead of treating them as timeless.

**Review:** enumerate material claims, inspect sources, challenge causal interpretations,
look for disconfirming evidence and distinguish contemporary facts from hindsight.
If checking is unavailable, record uncertainty and narrow conclusions. An empty
ledger cannot support exported knowledge units. Mechanical passes certify structure
and currency, never truth or completeness of claim selection.

### 07-synthesis — traceable, purpose-specific conclusions

**Inputs:** memo, shared comparison, checked claim ledger and selected evidence.
**Output:** `analysis` Markdown, `limitations`, `knowledge` list. Units have unique
`id`, `title`, `text`, `kind` (`speaker_claim`, `verified_fact`, `interpretation`),
`evidence_ids`, `claim_ids`, `limitations`. All cited evidence must belong to the
memo and be covered by linked claims. Verified facts require verified claims.
For document material `speaker_claim` denotes an attributed source assertion.
Preserve relevant negative cases and context in units and report limitations.
An empty corpus can yield empty knowledge with an explicit absence report.

**Review:** conclusion traceability, inference scope, epistemic distinctions, meaningful
uncertainty, omitted exceptions and no promotion leakage. Export only after all checks
pass. Use presentation.md for the conversational answer, not the intermediate memos.

## Iteration, freshness and compatibility

Collection and purpose stages have cumulative hash receipts. A changed source,
inventory or code framework stales dependent shared stages and every purpose.
Changing shared comparison stales purpose work but preserves extraction. Changing
one purpose question/memo stales only that purpose’s downstream stages. Editing
synthesis stales only its checkpoint. Re-save/re-check the earliest changed stage,
then inspect, revise and re-check downstream work; do not merely rubber-stamp hashes.
Receipts include review hashes, and `fail:` review files block advancement.

Framework revisions are agent labels; content hashes enforce freshness even if the
label was not changed. Working stage files reflect current work; preserve major
superseded drafts in their stage folders when useful. Exports retain immutable-content
revisions selected by input hashes; rerunning unchanged export returns the same path.
No automatic acquisition, recleaning, deletion or expiry occurs. Collection mutations
use one collection lock; avoid simultaneous manual edits during helper operations.

Exports contain Markdown, epistemic claims and JSONL units with source IDs, original
video times/document locators, dates, context, limitations and source URLs. They omit
raw/clean passages and private filesystem source paths. Inspect exports for semantic
promotion leakage before presenting them. `index` rebuilds collection-local routing
and excludes corrupted completed payloads. Existing single-video `index.json`, runs,
checkpoints and exports keep their schema and behavior; no migration is required.
Start from ROOT/collections/*/CONTEXT.md for unfinished collection routing, or the
chosen collection’s index for published purposes; do not scan source payloads.
Persistence is vendor-neutral and adds no chatbot integration or paid service.
