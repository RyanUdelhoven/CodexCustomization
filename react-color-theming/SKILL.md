---
name: react-color-theming
description: Define and distribute CSS color tokens and light and dark themes when building or updating a React app's palette, shared color styles, or theme controls.
---

# React color theming

## Color definition and distribution

- Preserve the existing app’s styling architecture for scoped edits and follow explicit user choices. For new styling decisions without an established convention, keep color styles in separate CSS files, outside JavaScript and TypeScript, by default. Apply the default directly without presenting implementation alternatives unprompted.
- Define app-wide semantic tokens such as `--color-surface`, `--color-text`, and `--color-action` on `:root` in the global stylesheet. Reuse the app's existing global CSS entry point. Define component-private tokens at component scope.
- Store complete CSS colors. Prefer OKLCH for new palette values and preserve exact supplied colors in their original format when practical. Give roles separate tokens when they need to change independently.
- Reference tokens with `var()` in CSS classes. Put hover, focus, and other style states in CSS. Let React select classes for finite variants. Use React's inline style prop for per-instance values that need runtime control. When CSS also owns hover or focus behavior, pass the value as a scoped custom property and consume it in the class.
- Derive variants from complete tokens using relative CSS colors when the target browsers support them. For example, `oklch(from var(--color-action) l c h / 40%)` sets alpha to 40%. Use the base token directly when its value needs no adjustment.

## Themes

- Support both light and dark. For new theme implementations, use dark on first load unless the user specifies a different default. Apply the dark defaults on `:root` and override the same tokens with a light theme selector such as `:root[data-theme="light"]`. Set the corresponding `color-scheme` so native controls match.
- Provide an accessible way to choose either theme. Reuse existing theme controls and preference storage. In a new implementation, persist the explicit choice and restore it on load. An existing saved choice takes precedence over the default.
- Keep components on the same semantic tokens in both themes. Check text, interactive states, and focus indicators against their actual backgrounds in each theme.
- When editing an existing app, integrate with its theme mechanism. Keep unrelated migrations outside the task.
