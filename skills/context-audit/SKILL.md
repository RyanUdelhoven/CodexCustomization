---
name: context-audit
description: Audit agent context and session usage to identify unnecessary token consumption. Use when asked to investigate token overhead, inefficient coding workflows, or context-loading problems.
---

# Context Audit

Find actionable causes of unnecessary token consumption while preserving task correctness
and project requirements.

Default to a read-only audit. Apply changes when requested.
Use the named target; otherwise audit the current repository.

## Establish scope

Read applicable instructions and the named target first. Consult the root README, skill metadata, or configuration only when they affect the question.

Use authorized session records when available. Obtain explicit authorization before
reading private histories, transcripts, or memory outside the supplied task context.

When explicit skill-run measurements exist in the approval-review tracker, reuse its interval and per-attempt evidence before collecting transcripts or building another recorder. Approval-review owns measurement capture and presentation; this skill owns requested efficiency analysis. Shared runs are not additive, and workflow totals do not establish causal skill overhead or savings. Routine skill markers and passive model hooks do not activate this audit.

If records are unavailable, perform a static audit and state its limits.
Do not install tools or change configuration merely to collect measurements.

Read [session accounting](references/session-accounting.md) only when analyzing usage records. Read [effectiveness evaluation](references/effectiveness-evaluation.md) only when planning or running a comparison.

## Audit context sources

Use `rg --files` and targeted searches before reading whole documents.
Exclude dependencies, generated output, and unrelated material unless evidence points there.

Inventory relevant instructions, skills, references, documentation, and loading configuration.
Record path, purpose, scope, size, and loading behavior.
Distinguish automatic, conditional, ordinary reference, and unknown loading.

Look for:

- Duplicate or conflicting guidance with overlapping applicability.
- Broad skill triggers and irrelevant mandatory reading.
- Large entrypoints containing narrowly applicable details.
- Broken references, stale commands, and documentation inconsistent with code.
- Missing routes to implementation, constraints, and useful verification.

Size alone does not establish waste.
Preserve acceptance criteria, compatibility constraints, useful commands, and domain knowledge.

## Recommend targeted changes

Prioritize observed expensive behavior over cosmetic document cleanup.

Keep broadly applicable requirements discoverable.
Move specialized detail behind clear task-specific pointers.
Use existing documentation conventions and update inbound references when relocating content.

When traces show unnecessary work, propose concrete scope or stopping rules.
Preserve required verification; do not equate fewer checks with better efficiency.

Classify changes as shorten, relocate, consolidate, correct, remove, or adjust workflow.
For each, explain the evidence, expected benefit, and information that must remain available.

## Verify navigation and outcomes

For navigation or workflow changes, walk one or two representative tasks through the affected paths. A wording-only review needs no unrelated repository trace.
Record dead ends and unnecessary reads.
Label static walkthroughs accurately; do not claim execution.

## Report and apply

Match the requested output. For a narrow static review, report the assessment, concrete examples, smallest remedies, and evidence limits; omit empty projection tables. For a measured usage audit or savings comparison, read [measurement reporting](references/measurement-report.md).

When applying requested changes, preserve unrelated edits and verify links,
retained requirements, and affected navigation. Report measured savings only
when comparable reruns establish them.
