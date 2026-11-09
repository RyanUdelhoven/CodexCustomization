---
name: react-data-fetching
description: Implement or repair React server-state workflows involving queries, mutations, cache keys, invalidation, and request lifecycle.
---

# React Data Fetching

- Find the app's data layer and rendering boundary. Reuse established query keys, request clients, and error handling. Include inputs that distinguish cached responses and respect account or tenant boundaries.
- Cover pending, empty, error, and success states that the UI exposes. Handle stale responses through the existing data layer when requests can overlap.
- Tie mutations to the appropriate cache update or invalidation. If using optimistic updates, preserve rollback and reconciliation when writes fail or overlap.
- Verify the affected lifecycle, including failure or invalidation when relevant. Use TypeScript contracts when the primary change is the payload shape.

## Working with other skills

When payload shape changes too, use react-typescript-contracts for the producer and consumer contract. Share fixtures and verify the changed boundary and request lifecycle together.

For a failure spanning local component state and shared server state, use react-state-debugger for effects, local state, and identity. Keep query-cache consistency and request reconciliation here and reuse the same reproduction.
