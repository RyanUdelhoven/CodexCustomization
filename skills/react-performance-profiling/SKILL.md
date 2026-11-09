---
name: react-performance-profiling
description: Measure and improve React performance when the task targets slow renders, interactions, bundles, or request waterfalls.
---

# React Performance Profiling

- For a React-only investigation, define the scenario and metric. Capture a baseline with the same build mode, inputs, and environment intended for follow-up.
- Choose evidence that matches the symptom. Use React profiling for render cost, browser traces for interaction or network timing, and build reports for bundle composition.
- Change the measured bottleneck. Check whether the change affects correctness and repeat the same measurement, accounting for run-to-run variation.
- Report baseline, result, and test conditions. If profiling is unavailable, distinguish hypotheses from measured findings.

## Working with other skills

This skill leads React UI performance investigations. For a cross-layer bottleneck, performance-optimizer owns the workload, baseline, and comparison. Use the React profiling methods above for the UI segment and contribute those measurements to the shared comparison.
