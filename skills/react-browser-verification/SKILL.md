---
name: react-browser-verification
description: Verify or reproduce a React user journey in a running app with browser automation. Use code-change-verification to determine outstanding repository-wide gates.
---

# React Browser Verification

- Use the repo's configured browser runner, app URL, and test data. For a specialized hosting environment, follow its supported preview and browser-control requirements; do not substitute a runner or install a browser when that workflow disallows it. Report an unavailable required journey as unverified. Identify the initial state and a user-visible success condition. Keep mutations within authorized test data.
- Follow the journey through the real UI. Prefer accessible locators and waits tied to observable state. Check reload or navigation only when the flow depends on them.
- On failure, capture the smallest useful evidence, such as a trace, screenshot, or relevant console or network error. Keep secrets and personal data out of evidence.
- Report flows and environments actually exercised. Use component testing when the requested output is an isolated test.

## Working with other skills

When code-change-verification also applies, carry forward the browser command, scope, environment, and result. Reuse the run if it satisfies a gate and the relevant inputs still match. If an accessibility review is in scope, share the browser session and evidence.

Before reporting browser-facing changes complete, use code-change-verification to establish the user's actual URL, serving process, and served build freshness. Passing a journey on an isolated test server does not establish availability in the user's browser; label that environment explicitly and carry forward any checks already performed against the actual URL.
