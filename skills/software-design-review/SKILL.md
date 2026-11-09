---
name: software-design-review
description: Review a software design, architecture proposal, or existing implementation for responsibilities, coupling, duplication, abstractions, and composability. Use for requested design assessment; ordinary implementation and defect-only code reviews do not require this skill.
---

# Software Design Review

Assess whether the design serves the stated requirements and remains understandable and economical to change. Review proposals and existing code; distinguish intended architecture from observed behavior. A review alone authorizes analysis, not implementation or persistent architecture documents. Continue into changes when the user also requests them.

## Establish evidence

Identify the target, constraints, important contracts, and concrete changes the system must support. Respect existing architecture and explicit choices. Inspect relevant callers, dependencies, data ownership, and tests when code exists. For proposals, identify missing details without inventing implementation facts. Use repository-navigation for substantial tracing and reuse its evidence.

Keep the review bounded to the requested area and necessary dependencies. For diffs, distinguish introduced issues from existing limitations. Assess requirements actually stated or evidenced; label assumptions and uncertainties.

## Evaluate relevant design pressures

Apply these lenses where they affect the target; do not force a finding under every principle.

- **DRY:** Identify duplicated rules or knowledge requiring coordinated updates. Similar syntax alone does not justify consolidation. Check independent evolution, generated sources, and existing authoritative representations before recommending extraction.
- **Responsibilities:** Examine cohesion, dependency direction, and ownership of state, policy, and side effects. Locate boundaries that hide decisions and limit unrelated changes.
- **UNIX composition:** Favor focused responsibilities and explicit inputs, outputs, and failures. Check whether pieces compose without hidden ordering or ambient state. Smallness alone does not justify splitting modules or services; account for coordination and operational costs.
- **Contracts:** Examine invariants, compatibility, validation ownership, and failure propagation at relevant boundaries. Include lifecycle, concurrency, and cleanup when the design depends on them.
- **Abstractions:** Compare indirection and configuration costs with concrete reuse or variation needs. Prefer the simplest adequate design; retaining duplication or a cohesive monolith may be appropriate.

Use a concrete change or failure scenario to assess each concern. Do not claim performance improvements without measurements; route performance investigations to the relevant profiling skill.

## Return actionable judgment

Lead with the assessment. Prioritize material findings; identify the location or proposal passage, evidence, affected scenario, consequence, and smallest useful remedy. Explain meaningful costs and benefits, including leaving the design unchanged. Separate demonstrated defects from design tradeoffs and optional improvements. Avoid numeric principle scores and speculative future requirements. Say when no material changes are warranted.

State review scope and material evidence gaps. Distinguish static inspection from executed checks. Suggest targeted validation for unresolved claims rather than running unrelated gates.

## Coordinate ownership

This skill owns design assessment. focused-refactor owns broader behavior-preserving restructuring; react-component-refactor owns component-only restructuring. React contract skills own specialized type implementation. Reuse findings when continuing authorized changes.

architecture-mapper owns durable navigation maps; decision-recorder owns requested decision records. Neither artifact follows automatically from a review. code-change-verification owns required final gates for implementation. When combined with defect-only review instructions, preserve their finding threshold and format; provide broader design advice only when requested.
