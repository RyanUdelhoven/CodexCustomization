# Workspace protocol

All commands below run from the installed skill directory using `.runtime/venv/bin/python`. Otherwise use absolute paths for both interpreter and helper. `RUN` means the absolute path returned by `start`; it is data, not a command. Keep JSON input files within that directory and quote paths. Use structured file writes or quoted heredocs; never interpolate transcript text into shell commands.

```sh
.runtime/venv/bin/python scripts/workflow.py start 'YOUTUBE_URL'
.runtime/venv/bin/python scripts/workflow.py read 'RUN' raw --offset 0 --limit 60
.runtime/venv/bin/python scripts/workflow.py read 'RUN' sponsorblock
```

Advance `--offset` by the number of returned segments until `complete: true`. If output truncates, retry a smaller page before proceeding. Segment IDs are stable zero-based integers assigned at retrieval, distinct from page offsets. Raw/clean timestamps remain original video times. Only emit bounded speech pages to tools; never echo ads to the user.

## Exclusion decision

Write `decision.json` inside RUN. Example schema (illustrative IDs, not defaults):

```json
{
  "sponsors": ["Example Company", "example.com"],
  "exclusions": [
    {"segment_ids": [12, 13, 14], "reason": "paid promotional passage including segue"},
    {"segment_ids": [90], "reason": "subscription prompt"}
  ]
}
```

Use empty lists when no sponsors/promotions exist. All lists require actual contextual review. `sponsors` contains confirmed names and aliases; the helper additionally excludes every segment mentioning them with case-insensitive word boundaries. It does not identify sponsors itself. Include ad segments that do not name the company. Keep reasons short and internal. SponsorBlock's suggested categories are `sponsor`, `selfpromo`, and `interaction`; other categories such as intros/outros are not automatically discarded.

```sh
.runtime/venv/bin/python scripts/workflow.py clean 'RUN' --input decision.json
.runtime/venv/bin/python scripts/workflow.py read 'RUN' clean --offset 0 --limit 60
```

Inspect all retained speech and promotion boundaries. Reapplying `clean` rebuilds from raw and invalidates sections and notes, allowing automatic corrections without damaging the original. Never edit `raw.json` or generated `clean.json` directly.

## Section outline

Write `outline.json` inside RUN:

```json
[
  {"id": "s1", "title": "The core problem", "segment_ids": [0, 1, 2]},
  {"id": "s2", "title": "Proposed solution", "segment_ids": [5, 6, 7]}
]
```

Use only retained IDs. Their concatenation must match the cleaned transcript exactly in order: no omissions, duplication, or reordering. An all-promotional transcript uses an empty outline and empty notes.

```sh
.runtime/venv/bin/python scripts/workflow.py sections 'RUN' --input outline.json
.runtime/venv/bin/python scripts/workflow.py read 'RUN' clean --section s1 --offset 0 --limit 60
```

Read all pages of each section. Section-specific offsets count within that section. Reapplying an outline invalidates imported section notes.

## Section notes and final checks

Write `notes-input.json` inside RUN, updating it as sections are analyzed:

```json
[
  {
    "section_id": "s1",
    "analysis": "The speaker defines the problem and supports it with an example. Describe the actual claims, evidence, qualifications, and relevance here.",
    "evidence_ids": [0, 2]
  },
  {
    "section_id": "s2",
    "analysis": "Describe the proposed solution and how it addresses the earlier problem, including assumptions and gaps.",
    "evidence_ids": [5, 7]
  }
]
```

Notes must occur in outline order, cite at least one ID from their section, and contain substantive analysis. Extra structured fields are allowed. These mechanical checks cannot prove analytical quality; Codex must review accuracy, ad removal, and synthesis. Do not repeat removed sponsor names in notes or final output.

```sh
.runtime/venv/bin/python scripts/workflow.py notes 'RUN' --input notes-input.json
.runtime/venv/bin/python scripts/workflow.py verify 'RUN'
```

Compose the answer, check original timestamps and cross-section connections, then delete the workspace immediately before replying:

```sh
.runtime/venv/bin/python scripts/workflow.py finish 'RUN'
```

For terminal errors or cancellation, `abort 'RUN'` removes it without requiring completed analysis. Validation errors are recoverable: fix the decision, outline, or notes and rerun the relevant command. If abandoning the run, always abort. If a network-restricted invocation needs the usual execution approval, that is separate from ad-removal review; never ask the user to validate ads.

`prune` can also run explicitly. Workspaces live under Python's system temporary directory in `codex-youtube-runs/run-<uuid>/`, with directory permissions 0700 and JSON permissions 0600. The manifest marks ownership and its modification time tracks activity; command locks protect active work from pruning. No transcript, title, or company appears in directory names. All decisions and input files disappear with the run. Expiry is 24 hours of inactivity, evaluated on the next invocation.
