---
name: docs-sync
description: Audit or correct existing documentation claims and omissions against code for a feature, release, or diff.
---

# Docs Sync

Identify the intended topic, diff, or release version. Compare public behavior, defaults, options, examples, and names against implementation, schemas, and relevant tests at that version. Treat current-branch and released behavior separately. Check both missing documentation and obsolete claims; cite the code and doc locations for material mismatches.

Report findings for audit-only requests. When asked to fix them, update the canonical source, such as a docstring or schema for generated references, and follow the project’s regeneration policy. Check relevant examples, links, or docs builds where practical. Report what changed, remaining disagreements, and unverified examples. Use architecture mapping when the goal is to create new repository wayfinding. For an existing map, this skill owns claim accuracy while architecture-mapper owns changes to structure and navigation; share source evidence and link checks.
