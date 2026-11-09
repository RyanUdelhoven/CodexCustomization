---
name: architecture-mapper
description: Create or maintain a durable repository map of module boundaries, entry points, and paths to tests.
---

# Architecture Mapper

Follow existing documentation locations and conventions. Identify what readers need to find, then verify module responsibilities, boundaries, entry points, representative flows, and test locations against manifests, registrations, source, and tests. Distinguish current behavior from proposed architecture; mark uncertain edges and avoid inferring ownership from folder names.

Create a short entry point organized by tasks readers need to perform. Link to scoped detail using stable relative paths and symbols, and explain relevant invariants near the module they affect. Reuse canonical docs and update relevant inbound links. Avoid a file inventory or mandatory reading for every edit. Verify local links and walk representative tasks from the entry point to source and tests. A one-off code trace calls for repository navigation instead.

When maintaining a map also requires checking existing claims against code, docs-sync owns that accuracy check; this skill owns map structure and navigation. Reuse the verified source trace and link checks instead of auditing or rewriting the same content twice.
