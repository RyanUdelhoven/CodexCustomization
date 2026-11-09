---
name: react-component-testing
description: Design, write, or repair tests for React components and hooks. Use test-coverage-improver to prioritize and measure coverage gaps.
---

# React Component Testing

- Find the existing render helper, providers, fixtures, and async utilities. Reuse their setup and keep mocks at stable boundaries such as network requests.
- Exercise behavior through user-visible roles, names, and interactions where possible. Assert observable results and include only states or transitions relevant to the requested change.
- Control async responses for timing-sensitive cases and await observable changes. Prefer a regression that reproduces the failure with the original behavior when feasible.
- Run the targeted suite and report actual results. Use browser verification for full-app navigation or browser-specific behavior.

## Working with other skills

For a measured coverage task, test-coverage-improver owns gap selection and remeasurement. Use this skill for tests at the React component or hook boundary and reuse qualifying test results.
