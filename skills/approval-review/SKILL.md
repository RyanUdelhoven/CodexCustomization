---
name: approval-review
description: Track approval requests and skill-run token usage, review local evidence, and implement safe permission allowances during requested approval reviews. Honor explicit review-only requests; passive recording does not trigger investigation or rule changes.
---

# Review approval friction

Use local incident capture plus incremental investigation. A request to review recent approval requests or approval friction authorizes finding and implementing suitable permission allowances within that review's scope, subject to execution permissions and the Codex Customization project boundary. Honor explicit requests for findings, suggestions, or review only without making changes. Merely displaying/exporting records, recording events, or discussing the workflow does not authorize a review or rule edits. Never grant permissions merely because a command recurs or was approved once.

## Start with new evidence

For “show skill token usage,” recording skill runs, or comparing observed run totals, use [skill usage](references/skill-usage.md). This owns interval recording and display; context-audit owns requested efficiency analysis and controlled comparisons. Routine markers and model hooks do not invoke an audit. Shared request counts are not additive across runs, and observed workflow usage is not causal skill overhead.

Use installed `codex-approval-tracker` and `codex-skill-usage` directly from `~/.local/share/codex-publish` when available. Do not route them through Python or substitute a writable source copy for the approved executable. Normal source execution is a fallback only when installation is absent. Repeated captured requests identify candidates for review, not proof of successful execution or safety; preserve source provenance and avoid counting script names inside inline code as invocations.

For “show approval requests,” exports, task labels, or review annotations, use [the record commands](references/tracker.md). Reading records does not consume a review batch. For “review approval friction” or “find recurring approval requests,” use grouped evidence alongside the incremental investigation below. This capability uses local files and CLI commands; it has no dashboard or server. The record commands own evidence and annotations; this skill owns investigation and requested rule updates. Existing merge workflows retain publication ownership.

## Choose the requested operation

For recording or displaying approval/token records, follow only the matching reference above and stop after the requested result. Do not prepare review batches, investigate policies, or implement allowances for a display request.

For an actual approval-friction review, read [investigation and implementation](references/investigate.md). Use the prepared batch and existing corrections; retain explicit review-only scope and protected-helper boundaries.
