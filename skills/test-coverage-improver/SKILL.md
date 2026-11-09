---
name: test-coverage-improver
description: Audit measured test coverage gaps or address a coverage regression. Use react-component-testing for React component or hook test design when addressing those gaps.
---

# Test Coverage Improver

Use the repository’s coverage command and configuration. Record scope and baseline; inspect branch or line details alongside source and existing tests. Rank gaps by impact and likelihood, focusing on distinct behavior such as failure paths, boundaries, and regressions. Explain what each proposed test would catch. Treat generated code, exclusions, and unreachable branches according to project policy; do not game the metric.

For an audit, report the prioritized gaps. When asked to improve coverage, add focused tests at the appropriate boundary and assert observable outcomes. Where practical verify that a meaningful behavior change would fail the test. Remeasure with the same configuration. Reuse passing test results from the coverage run when they satisfy the applicable checks. Report comparable changes and remaining gaps; coverage alone does not establish test quality.
