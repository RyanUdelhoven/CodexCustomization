---
name: performance-optimizer
description: Profile and optimize runtime or resource bottlenecks using comparable measurements. For React UI performance, use react-performance-profiling. Use this skill for bottlenecks spanning multiple layers.
---

# Performance Optimizer

Define the workload, metric, and behavior to preserve. Prefer the project’s benchmark or a representative reproducible case; record input size, environment, revision, build mode, and relevant warmup or caching. Measure a baseline and repeat enough to distinguish an improvement from run-to-run noise.

Use a profiler or targeted instrumentation to identify the bottleneck before changing code. Test a focused hypothesis, check correctness without duplicating equivalent current verification, then repeat the same benchmark under comparable conditions. Report absolute and relative results, variance or sample size as useful, and tradeoffs in other resources or workloads. If measurement is blocked, distinguish hypotheses from proven gains. Do not turn a readability refactor into a performance claim.
