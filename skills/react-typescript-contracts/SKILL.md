---
name: react-typescript-contracts
description: Design or repair TypeScript contracts at React component and API boundaries when type shape or runtime validation is the main task.
---

# React Typescript Contracts

- Identify producers, consumers, and the source of truth. Inspect compiler settings and generated types before editing shared contracts.
- Encode valid combinations with discriminated unions where they prevent impossible states. Preserve inference and compatibility expected by callers. Update generated contracts through the existing generation path.
- Treat external input as unknown until parsed or validated using the existing boundary. Keep optionality and nullability aligned with the actual wire format. Resolve errors through narrowing or contract changes.
- Run the repo's type check and verify boundary behavior when validation changes. Ordinary local prop typing belongs in component implementation.

## Working with other skills

For forms, this skill owns shared producer/consumer types and external payload validation; react-form-workflows owns editable-field validation timing, feedback, and submission behavior. Reuse the existing schema when it serves both boundaries, and verify the mapping together rather than introducing competing validators.
