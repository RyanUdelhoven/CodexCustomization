---
name: repository-navigation
description: Answer where code lives or trace a specific behavior, including when substantial discovery is needed before an edit.
---

# Repository Navigation

Find the smallest verified slice of the current checkout that answers the task. Apply relevant repository instructions. Navigation is read-only; if the user also requested a change, continue that work once the relevant code is located.

- **Start from a clue.** Search exact identifiers, error text, routes, or config keys with `rg -n -F`. For filename clues use `rg --files`. For a concept without an exact clue, use the relevant repository map, manifest, or package entry point to narrow the search. Treat docs and indexes as leads and check against the current source.
- **Read around promising matches.** Start with filenames or bounded results for noisy searches. Read the definition and enough surrounding code to explain its role. Use available symbol references or implementations to resolve ambiguous names; use text search for registration, configuration, and string-based dispatch. If expected files are missing, check search scope and ignore rules before claiming absence.
- **Trace only the needed edges.** Follow the relevant caller, registration, implementation, and test as the question requires. Check wiring such as route mounts, dependency injection, feature flags, or platform variants when it changes which implementation runs. A matching name or import alone does not establish a runtime path. Treat tests as evidence of intended behavior unless actually run.
- **Stop when the evidence supports the answer.** Give the direct answer with verified file and line links or file and symbol references. For a trace, show the key hops in order and the relevant test if found. State material uncertainty and the next check that could resolve it. When navigation supports a larger task, carry the findings into that work without a separate report.

Reuse installed search tools or existing indexes if useful; do not install tooling, build an index, or generate a repository map just to navigate. A known-file edit or a request to maintain architecture documentation does not by itself call for this skill.
