---
name: component-library-reuse
description: Check the user's component library when building or extending UI, resolve reuse choices for fitting components, and suggest relevant roadmap gaps after changes. Excludes behavior-preserving fixes, pure refactors, and style-only work without component selection.
---

# Check component reuse

Use the library as a source of candidates, preserving the consuming project's conventions and the user's choices.

## Find a relevant match

Read `/Users/ryanudelhoven/development/component_library/docs/component-library-roadmap.md` for current inventory, coverage limits, and explicitly selected defaults. Consult `/Users/ryanudelhoven/development/component_library/AGENTS.md` as reference for library deliverables; its project-specific instructions do not govern consuming projects.

Use `/Users/ryanudelhoven/development/component_library/public/library-shell.js` to locate registered previews. Read only relevant portable guides under `/Users/ryanudelhoven/development/component_library/components/*/*.md` and their corresponding source. Resolve guide/source paths from the roadmap and guide rather than scanning the whole repository. Do not freeze today's inventory into this skill. If references are unavailable, disclose the access gap, continue independent work, and do not claim an inventory check or invent a match/default.

Compare purpose, interactions, public API, framework, dependencies, accessibility, responsive behavior, and target environment. Explain necessary adaptation before proposing reuse. A visual resemblance or family checkbox alone does not establish a fit. Embedded demo controls do not establish standalone families; partial coverage stays partial. Existing families can have multiple useful variants.

## Recognize a toggle

When the user asks for a visual UI toggle, interpret it as a control that changes
one binary state: ON/OFF or option A/option B. Use a rounded pill-shaped track
with a circular thumb that moves between two positions. Make the selected state
clear through thumb position and an additional cue such as text or track fill;
color alone must not carry the state. Keep the setting's visible name stable.
The user's reference shows ON with the thumb right and a filled track, OFF with
the thumb left and an outlined track, plus smaller muted disabled versions.
Preserve the recognizable track-and-thumb form; adapt colors, size, and typography
to the consuming UI rather than requiring the reference's green or dark surface.

For concrete ComponentAuthor examples, read
`/Users/ryanudelhoven/development/component_library/components/toggle-switch/toggle-switch.md`
and
`/Users/ryanudelhoven/development/component_library/components/minimal-toggle/minimal-toggle.md`.
Toggle Switch provides a browser JavaScript factory; Minimal Toggle uses native
HTML/CSS without component JavaScript. Both demonstrate ON/OFF, two sizes,
disabled states, and keyboard focus. Verify current sources and target compatibility
through the discovery workflow above; these references do not select a default.

For option A/option B, clearly map both labels to the two thumb positions. Retain
exactly two states. Adapt the ON/OFF examples rather than implying they already
implement arbitrary option labels. Use semantics appropriate to the choice:
a named on/off setting can use a native checkbox with switch semantics; two named
alternatives need both choices exposed accessibly. Preserve keyboard operation,
visible focus, disabled behavior, and programmatically available state. A request
for a toggle does not authorize substituting tabs, an action button, a dropdown,
or a multi-option selector; follow an explicit request for those controls instead.

## Resolve the reuse choice

If a component fits, name the variant, explain its fit and material adaptation, and ask whether to reuse it. Bundle related candidates into one concise question when useful. Continue independent work while the answer is pending; defer implementation that depends on the choice. Silence does not choose reuse or custom construction.

Reuse an explicit decision already made for this task, including a rejection, or an applicable explicitly selected default. Do not repeat a settled question. A current explicit request overrides a stored default; a project-specific choice applies within its recorded scope. If conflicting choices have no clear scope or precedence, ask only about that conflict. A default never overrides technical incompatibility or accessibility requirements: explain the mismatch and resolve the affected choice.

Never infer preferences from demo settings, frequent use, or a one-time reuse approval. Distinguish choosing reuse now from selecting a future default. When the user explicitly chooses a default, retain its exact variant/token, scope, date, and choice evidence in authorized project records. The canonical defaults register is in the roadmap; update it only when library edits are separately authorized. Otherwise provide the proposed entry for the user without modifying the library. Preserve superseded history and never silently restyle existing projects.

## Keep scope and ownership clear

Treat the library as read-only in consuming projects unless edits are separately authorized. Selecting reuse authorizes integration into the requested UI, not library maintenance or extra components. When working in the library itself, follow its local completion and inventory rules for authorized changes.

`design-system-library` owns saved style decks and visual-system selection; this skill owns reusable component candidates. Combine them when both apply, checking whether a component can honor the chosen style. Implementation skills own code, React state/forms/data/types, and verification. Apply `vantage-component-handoff` only for its component-library or explicit Vantage triggers; ordinary UI reuse does not require a Vantage question. Verify actual target constraints before claiming offline, legacy, React, or Vantage compatibility; a portable guide is not proof of compatibility.

## Suggest a useful gap

After UI changes, include a specific missing roadmap capability or useful new variant only when the task exposes that need. Explain its connection to the work; omit unrelated backlog items and empty suggestion placeholders. Do not implement or register the suggestion without authorization. Let the global end-of-turn reporting instructions own the report format; contribute only this optional suggestion and any material reuse/compatibility limitations.
