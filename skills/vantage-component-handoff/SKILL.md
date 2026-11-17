---
name: vantage-component-handoff
description: Ask whether component-library components are for Vantage at work, then create an offline reconstruction Markdown file only when Vantage is confirmed. Also use for explicit Vantage component reconstruction requests. Excludes general Foundry development and ordinary app UI outside component-library work.
---

# Vantage component handoff

Help the user design or build a library component here so their Vantage agent can rebuild it from a self-contained prompt and example code. The receiving agent has **no internet access**. This skill owns Vantage compatibility and the reconstruction artifact; the applicable implementation skill owns building the component.

## Confirm scope

When building or extending components for a component library, ask: **“Are these components for Vantage at work?”** Ask early, before committing to dependencies or platform integration. Reuse an explicit answer for the same component or clearly identified batch; do not repeat the question when the user already confirmed Vantage.

- If yes, read [Vantage constraints](references/vantage-constraints.md) and apply this workflow.
- If no, continue normal component work without Vantage constraints or this handoff requirement.
- While unanswered, inspect existing components and clarify behavior; defer Vantage-dependent implementation decisions.
- An explicit Vantage reconstruction request establishes yes. Do not expand into transforms, Functions, or unrelated Foundry work.

## Establish a compatible design

Identify the actual target: library component, standalone OSDK app integration, custom Workshop widget, or another specified surface. Ask only for missing details that materially affect compatibility. Inspect supplied target package files, lockfile, compiler configuration, Vite configuration, widget manifest, and existing patterns when available. Distinguish the local prototype environment from evidence about the Vantage target.

Record verified facts, user-reported facts, assumptions, and blockers separately. Never invent versions or assume an installed local dependency exists in Vantage. Prefer existing verified dependencies and a portable implementation using confirmed primitives. With missing target evidence, provide a compatibility-safe core and explicitly conditional adapters; label the handoff provisional. Pause only implementation that depends on an unresolved material capability.

The offline agent cannot browse documentation, follow links, fetch example repositories, or rely on public registries. Embed essential documentation excerpts or explanations, types, assets, and examples. Internet absence for the agent does not establish whether the built component or target runtime has network access; verify those separately. Do not introduce remote fonts, CDN assets, or network requirements without confirmed target support and supplied alternatives.

## Build and capture the component

Use the relevant component workflow when implementing. Capture the resulting behavior and actual code, rather than describing an imagined implementation. If only design or prompt authoring was requested, provide as much usable example code as possible and label unexecuted code honestly. Keep platform access behind explicit host interfaces where feasible, allowing the UI core to use fixture data offline.

Reuse available validation evidence. Distinguish local prototype checks from checks still required inside Vantage. Do not claim Vantage compatibility based solely on a local build.

## Write the Markdown deliverable

Create a real `.md` file in the current project's requested destination or existing artifact convention; otherwise use `artifacts/<component-name>-vantage-handoff.md`. For a batch, include every component and its shared files, using separate files if readability requires it. Link the output in the final response. Never replace the file with a chat-only prompt.

Make the file self-contained: the receiving agent must not need this skill, the original attachment, this chat, local paths, screenshots alone, or linked documentation. Include these sections with concrete details:

1. **Kickoff prompt.** A copyable instruction addressed to the Vantage agent: rebuild the specified component from this file; inspect the target repository first; respect verified constraints; use embedded code; ask about material unknowns; do not browse, upgrade dependencies, or attempt unverified installs. Define the desired finished result and first action.
2. **Target and compatibility.** Artifact and host, verified versions and dependency sources, relevant configuration evidence, capability restrictions, assumptions, blocked adapters, and a proceed/provisional/needs-details/unsupported decision. Include the offline-agent constraint and any runtime network distinction.
3. **Complete component specification.** Purpose and use cases; public props/types, defaults, callbacks and events; data models and fixtures; controlled/uncontrolled ownership; variants, states and transitions; interactions and keyboard behavior; validation, loading, empty, error, disabled and edge states where applicable. Cover semantics, focus and accessible names; layout, dimensions, typography, spacing, colors/tokens, icons/assets, responsive behavior, animation and reduced motion. State non-applicable aspects explicitly when omission would leave ambiguity. Keep layouts within narrow viewports using wrapping or stacking, without horizontal scrolling or clipping content.
4. **File map and code.** Label every code block with its destination relative path and language. Include as much actual source as possible: component, styles, types, helpers, fixtures, icons/assets, export/barrel wiring, usage example, integration adapters, and relevant existing tests. Supply required imports and shared primitives or their full contracts. Include necessary configuration changes as labeled patches or fragments, preserving target versions. Avoid ellipses, “same as above,” and unexplained omitted dependencies. If output limits force omissions, enumerate them and their impact; never call an incomplete reconstruction bundle complete.
5. **Rebuild and integration steps.** Explain file placement, exports, styling, host parameters/events, data boundaries, and available build commands. Mark commands needing target confirmation. Do not prescribe public downloads or overwrite unrelated project configuration.
6. **Acceptance and verification.** Provide observable checks for specified states, interactions, accessibility and responsive behavior. List what was actually run, results, and remaining target checks. Include unresolved questions and version-sensitive adaptation points.

Inspect the written file for missing imports, unavailable assets, unsupported dependencies, contradictory specifications and hidden reliance on external context. Keep uncertainty visible instead of asking the receiving agent to guess.

## Working with other skills

`react-component-builder` owns React implementation and asks the Vantage routing question for library work. This skill owns the confirmed Vantage constraints and Markdown reconstruction bundle, including framework-independent components. Other React skills retain ownership of forms, data, types, theming and verification when those tasks apply; reuse their findings. `handoff-writer` owns general resumable work handoffs; `package-skill` owns prompts to create skills, not component reconstruction. A component bundle alone does not request a new app, hosting, Docker packaging, publication, or deployment; follow those workflows only when the user actually requests an app or those actions.
