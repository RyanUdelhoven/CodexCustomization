---
name: focused-refactor
description: 'Restructure a bounded area of code while preserving observable behavior and public contracts. For React component-only work, use react-component-refactor.'
---

# Focused Refactor

Identify the target, the structural problem, and the contracts that must survive, including error behavior, side effects, and compatibility where relevant. Establish the affected tests’ baseline. If an important behavior lacks protection, add a targeted characterization test when useful or identify another concrete verification method.

Make small coherent changes around the named problem and run focused checks at meaningful boundaries. Preserve unrelated edits and avoid opportunistic rewrites. If a step requires changing behavior, separate it from the refactor and surface the decision. Check the final diff and run outstanding final gates, reusing equivalent evidence for unchanged inputs where project policy allows; report preserved behavior, checks, and material gaps. A bug fix or feature request alone does not call for this skill.
