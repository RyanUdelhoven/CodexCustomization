---
name: task-research
description: Find how others solved a practical task and present evidence-backed options ranked by free use, existing capabilities, automation, and maintenance preferences. Use for task-solution discovery and ranked approach comparisons, rather than routine execution, simple lookups, or skill authoring itself.
---

# Research practical task solutions

Find demonstrated ways to achieve the user's outcome, adapt them to their environment, and return ranked options before implementation. Research-only requests authorize research and comparison, not setup or execution. Continue authorized implementation when the user explicitly requests both.

## Scope and priorities

Identify the outcome, success criteria, operating environment, existing capabilities, and explicit constraints. Use available context before asking questions. Ask only when missing information materially changes feasibility; otherwise state assumptions. Do not access private accounts just to establish whether the user has them.

Apply these ordered preferences to feasible approaches. Explicit user requirements override defaults. Compare the first meaningful difference before later criteria; do not invent weighted scores. Exclude approaches that cannot achieve the outcome. Describe substantial tradeoffs even when the ordering favors a weaker approach.

| Rank | Preference | Interpretation |
|---|---|---|
| 1 | Free | No new subscriptions, usage charges, purchases, or paid upgrades; disclose existing costs and limits. |
| 2 | Existing capabilities only | No additional installations, external services, or added libraries. Built-in tools and their standard libraries qualify. |
| 3 | Fully automated | Prefer unattended ongoing operation after initial setup; disclose every recurring human step. |
| 4 | Reliable | Consistent outcomes, predictable failures, and practical recovery. |
| 5 | Low maintenance | Little ongoing repair, supervision, or dependency upkeep. |
| 6 | Private | Minimal data sharing and narrowly scoped access. |
| 7 | Proven | Credible implementations addressing a closely matching task. |
| 8 | Simple | Few setup steps, moving parts, and configuration requirements. |
| 9 | Reversible | Easy rollback, removal, and data export. |
| 10 | Transparent | Inspectable actions, outputs, and failures. |

Existing services and accounts directly involved in the task can qualify, such as the user's bank. Confirm relevant availability from context or ask when necessary; never assume account ownership or access authorization. A newly introduced service remains a compromise even if the user already has an unrelated account there. Added libraries remain compromises even when free. Existing installed software can qualify; disclose dependencies rather than silently introducing tools.

These preferences govern proposed solutions, not the available browsing tools used to research them. Search using public, non-sensitive task descriptions. Do not upload private task data to research services.

## Find and assess demonstrated approaches

Use research-backed-skill-builder for source selection, freshness checks, and evidence synthesis. Reuse existing findings rather than repeating a survey. Seek firsthand implementations, reproducible examples, maintainer discussions, and documented failures; verify capabilities against current official documentation. Distinguish demonstrated success, documented possibility, and your proposed adaptation. Never imply another person implemented an invented combination.

Start with built-in functionality and existing tools or account features. Explore materially different approaches rather than listing interchangeable products. Verify the target platform, version, prerequisites, costs, and automation limits. Distinguish one-time setup from recurring work, including authentication, approvals, recovery, device availability, and triggering. Unknown capability or price remains unknown, not a favorable score.

If nothing meets all preferences, identify the closest feasible approaches and their exact compromises. Do not quietly relax explicit requirements. Avoid padding the shortlist with unsuitable options. Stop when evidence supports the meaningful choices; disclose inaccessible evidence and remaining uncertainty.

## Deliver the comparison

Lead with the recommended approach and its main compromise. Usually present up to three distinct options; use fewer when evidence supports fewer. Include a compact comparison covering cost, additions or services, setup, recurring manual work, reliability, maintenance, privacy, evidence, simplicity, reversibility, and transparency. Group criteria when that improves readability.

Link evidence near each option and explain what transfers to this user's task. State why the ranking follows the ordered priorities, identify the first meaningful differentiator, and explain what would change the recommendation. Include a practical next step and any decisive unknown. Report research dates or relevant versions for changing capabilities. Do not claim a solution was tested unless it was executed and verified.

## Coordinate ownership

This skill owns task framing, preference ordering, and the ranked task-options deliverable. Research-backed-skill-builder owns shared research methods and skill-build research. Cost-aware-options-review owns detailed pricing checks and its cost pause when third-party choices are researched; finish the comparison before that pause and reuse all findings. Merely finding paid alternatives does not block delivering this research report. Honor its pause before subsequent selection or implementation unless the user already authorized that choice.

Specialized skills own implementation and artifacts after approach selection. Plugin-management owns plugin discovery when genuinely needed; this workflow's preference for existing capabilities does not authorize installations or connections. OpenAI-specific questions retain openai-docs source routing. Do not turn ordinary execution into a survey or create another skill unless requested.
