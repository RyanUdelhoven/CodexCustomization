---
name: react-state-debugger
description: Diagnose incorrect React client state, effect loops, stale closures, and out-of-order updates from a reproducible symptom.
---

# React State Debugger

- Record the user action, expected result, and observed update sequence. Identify the state owner and trace event handlers, render inputs, effects, and async completions.
- Check identity and keys for unexpected remounts. Trace effect dependencies and cleanup for duplicate work. Reproduce stale writes by controlling completion order where relevant.
- Fix the source of the state inconsistency. Remove duplicated derived state when it causes divergence. Keep dependencies accurate and handle obsolete async results where ownership requires it.
- Replay the failing sequence and a nearby working path. Use performance profiling when state is correct and the concern is speed.

## Working with other skills

If repository-navigation is needed to locate the behavior, carry its verified caller and runtime trace into the state investigation.

For mixed client and server-state failures, this skill owns local state, effects, and component identity; react-data-fetching owns shared query caches, invalidation, and request reconciliation. Share the reproduction and verify the combined sequence without adding a competing cache or request lifecycle.
