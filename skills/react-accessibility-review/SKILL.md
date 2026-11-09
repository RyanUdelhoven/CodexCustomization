---
name: react-accessibility-review
description: Review a React interface for accessibility when requested, especially keyboard interaction, focus, semantics, and accessible names.
---

# React Accessibility Review

- Identify the affected flow and inspect rendered semantics. Start with native control behavior and compare custom widgets against their expected keyboard and focus behavior.
- Walk the flow with a keyboard. Check focus order and visibility, focus placement and restoration, names and states, and announcement of errors or dynamic status where relevant.
- Use the repo's automated accessibility checks when available. Identify which interactions were verified manually and which depended on static inspection or automated checks.
- Report each finding with the affected control, reproduction, user impact, and a focused fix. Apply fixes when the request includes remediation.
