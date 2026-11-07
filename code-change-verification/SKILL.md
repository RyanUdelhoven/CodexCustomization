---
name: code-change-verification
description: Run outstanding repository-defined final gates for eligible changes, or perform explicitly requested change verification. Use react-browser-verification for React user journeys and reuse eligible browser results for final gates.
---

# Code Change Verification

Determine scope from the actual diff, including relevant untracked files. Find the check commands and requirements in applicable repository guidance, manifests, and CI; use project tooling and documented order. Run checks suited to the change and every required gate. Reuse an observed check result when the command, scope, relevant environment, and inputs still match and project policy permits it. Run outstanding final gates against the final contents. If an auto-fix changes files, review the resulting diff and rerun checks affected by the change.

Distinguish failures caused by the change, known baseline failures, environmental blockers, and checks not run. Report partial runs as partial; when applicability of an earlier result is uncertain, rerun the affected check. Fix in-scope failures when authorized, and report commands and outcomes compactly. A prose-only change does not need the code stack unless project rules require it.
