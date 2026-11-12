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

Start with applicable instructions, the root README, available skill metadata,
and relevant configuration.

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

Trace one or two representative tasks to their implementation, constraints, and verification.
Record dead ends and unnecessary reads.
Label static walkthroughs accurately; do not claim execution.

## Report and apply

Use exactly two report sections, in this order. An audit title and read-only or
applied status may appear above them.

### 1. Metrics

Use a Metric | Result table. Include:

- Measurement basis: workload, sample size, unit, and whether input includes cached input.
- Current usage and breakdown: show measured totals and major spending categories when available.
- Potential savings: estimate only defensible, non-overlapping savings for that workload.
- Estimated future usage: use the same basis and units as current usage.
- Measured after changes: show comparable results or “Not yet measured.”

State assumptions and material exclusions alongside projections. With session-level
data, subtract projected savings from each session before aggregating. If only
summary medians exist, label their difference a rough projection, not a measured
breakdown. Mark unavailable metrics rather than extrapolating from file sizes or
static walkthroughs. Keep token usage, cost, and quota separate.

### 2. Issues and Solutions

Use an Issue | Impact | Solution table. Order rows by priority, highest first,
without a priority column. Name each issue in a few words. Bold the concrete
impact and distinguish measured effects, estimates, and walkthrough observations.
Cite session evidence or exact file locations in the relevant cell. Give a
specific fix and name any safeguard it must preserve. If no material issues
were found, say so under this section.

When applying requested changes, preserve unrelated edits and verify links,
retained requirements, and affected navigation. Report measured savings only
when comparable reruns establish them.
