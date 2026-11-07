---
name: react-component-refactor
description: Restructure existing React components while preserving public props, interaction behavior, and state lifetime.
---

# React Component Refactor

- Map callers and baseline the relevant interactions. Identify state ownership, identity and keys, provider boundaries, refs, and effects before moving code.
- Keep extraction tied to a specific responsibility. Preserve mount behavior, controlled and uncontrolled semantics, and public contracts. Check rendering boundaries when moving code across modules.
- Review the diff for behavior drift. Run existing checks and exercise the interactions most likely to change when components move.
- Use component building when the request changes functionality. Use profiling when performance improvement is the primary objective.

## Working with other skills

This skill leads component-only refactors. For broader restructuring, focused-refactor owns sequencing and the overall verification plan. Apply the React identity and state checks to affected components and carry their results into that plan.
