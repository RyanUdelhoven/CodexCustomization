---
name: react-component-builder
description: Implement or extend React and TypeScript components when UI construction or composition is the main task.
---

# React Component Builder

- Inspect neighboring components, design primitives, and real callers before choosing the prop shape. Match the project's styling and rendering boundaries for scoped edits. For new styling decisions, prefer separate CSS files, including CSS Modules when local selector scope helps. Use React's inline style prop when an element needs a per-instance value computed at runtime. Follow explicit user styling requests.
- Build from semantic elements and existing primitives. Model supported variants explicitly and keep state with its closest owner. Derive values during render when they follow directly from inputs.
- Preserve existing callers when extending a component. Check the supported variants and the interaction the change introduces using the project's normal verification commands.
- Use the form or data workflow when submission or server-state behavior drives the task. Use component refactoring for behavior-preserving restructuring.

## Working with other skills

Apply react-color-theming when the task defines or changes shared color tokens or themes.

When the task also changes an API contract, form submission, or server-state lifecycle, apply the matching React skill to that part. Share the same component context and verification evidence.
