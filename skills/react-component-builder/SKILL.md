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

Apply [component-library-reuse](../component-library-reuse/SKILL.md) when selecting or adding UI components. It owns library candidates and reuse choices; this workflow owns React integration and adaptation. Reuse settled choices and existing project primitives. For toggle requests, follow its [toggle definition and ComponentAuthor references](../component-library-reuse/SKILL.md#recognize-a-toggle): a binary state control with a pill-shaped track and movable circular thumb. This applies when adapting an existing primitive as well as selecting a library candidate.

For component-library work, ask “Are these components for Vantage at work?” before choosing target-dependent dependencies or integrations, unless already answered for this component or batch. On yes, apply [vantage-component-handoff](../vantage-component-handoff/SKILL.md) for target constraints and the offline reconstruction `.md` file. On no, continue this workflow normally. While awaiting an answer, continue independent inspection and behavior design. Keep Vantage-specific guidance in that skill.

Apply react-color-theming when the task defines or changes shared color tokens or themes.

When the task also changes an API contract, form submission, or server-state lifecycle, apply the matching React skill to that part. Share the same component context and verification evidence.
