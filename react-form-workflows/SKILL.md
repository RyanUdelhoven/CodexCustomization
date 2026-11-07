---
name: react-form-workflows
description: Build or fix typed React form flows involving validation, submission, and field or form feedback.
---

# React Form Workflows

- Reuse the project's form and validation conventions. Trace the mapping from initial values and editable input to the submitted payload. Preserve user input across recoverable failures.
- Define when validation runs and where each error appears. Connect field errors to controls and surface server or form-wide failures through the existing feedback pattern.
- Prevent duplicate submission when concurrent requests would duplicate writes. Define success behavior and keep reset or navigation aligned with it.
- Verify invalid input, the successful path, and relevant submission failures. Use the data workflow when shared cache behavior is the main change.

## Working with other skills

If submission also changes shared server state, use react-data-fetching for cache and mutation behavior. Keep validation, submission feedback, and reset behavior in the form workflow.

When shared payload types or external runtime validation change, use react-typescript-contracts for that boundary. Keep field-validation timing and feedback here, reuse applicable schemas, and check input-to-payload mapping together.
