---
name: skill-deconfliction
description: Deconflict the skill set whenever creating or updating a Codex skill, before installation or finalizing an update. Also use for requested skill-set audits. Review set-wide triggers, ownership, handoffs, precedence, shared dependencies, and duplicated workflows; align affected writable skills rather than reviewing only the current target.
---

# Deconflict the skill set

Treat the installed and session-available skills as an interacting system. A creation or update starts the review; it does not define the review boundary. Apply this workflow to instruction, reference, metadata, or invocation-policy changes that can affect skill behavior, including changes to this skill itself.

## Review creation, updates, and the existing set

1. **Establish the change and inventory.** Identify the user's requirements, defaults, exceptions, and intended triggers. Stage new skills outside installed roots; for updates, preserve the current contents and prepare a reviewable diff before finalizing. For tool-managed template packages, review planned instructions and interactions before the owning workflow writes them, then validate the generated package; do not bypass that workflow by copying or hand-authoring its managed files. Inventory names, descriptions, locations, and available invocation policies for the whole session-available set, including custom, system, project, and plugin skills. Inspect discoverable local skills as relevant; distinguish installed but unavailable skills. Record material access gaps.
2. **Map interactions across the set.** Use the inventory to identify shared triggers, terminology, deliverables, dependencies, and workflow chains. Read full instructions and relevant references for plausible overlaps. For a set-wide audit, inspect every custom entrypoint and every overlapping group, even when unrelated to the initiating change. For an individual update, inspect affected neighbors and follow changed handoffs transitively until no material unresolved interaction remains. Use each skill's declared access mechanism; do not load unrelated references merely to complete an inventory.
3. **Compare realistic requests.** Check each skill alone, shared triggers, mixed tasks, explicit overrides, and existing-project exceptions. Check scope, defaults, ownership, handoffs, ordering, report formats, repeated research or verification, and side effects. Distinguish complementary work from contradictory requirements. An overlap is not inherently a defect; avoid adding exclusions that prevent legitimate combined work.
4. **Assign scoped ownership.** Follow higher-priority instructions and explicit user requests. Treat skill defaults as scoped preferences. Identify which skill owns each decision or action and what evidence another skill reuses. Avoid blanket priority among peer skills. Preserve existing-project conventions and user choices where applicable. Deconfliction owns skill interactions; skill-creator owns general packaging guidance and authoring validation; specialized template workflows own their managed packages; research owns evidence gathering when its research triggers apply; specialized workflows own their artifacts or implementation. A context-efficiency audit remains a separate task unless requested.
5. **Align affected writable skills.** Make the smallest coordinated edits needed across the set, including reciprocal handoffs when one-sided wording leaves ambiguity. Preserve unrelated behavior and invocation settings. Treat system and plugin skills as comparison inputs; resolve conflicts through writable custom skills or report constraints that cannot be fixed there. Do not rename, remove, merge, or disable skills merely because triggers overlap. If a material conflict requires an unresolved user preference, finish independent work and ask about that specific choice before finalizing dependent changes.
6. **Validate and finalize once.** Walk representative requests against the final combined wording. Validate frontmatter, references, and invocation settings for every changed skill. Use the skill-creator validator when available and report dependency or execution limits accurately. Review the complete change set, then install or finalize the coordinated updates. Include edits produced by deconfliction in this same cycle; do not recursively start another cycle for each corrective edit. Reopen affected checks only when a later change introduces a new interaction.
7. **Report coverage and outcomes.** Name the inventory scope, skills read in depth, changes made across the set, material conflicts left unresolved, representative walkthrough results, and validation limits. Distinguish metadata inventory, static walkthroughs, and executed behavior tests. Do not claim set-wide deconfliction after reviewing only the initiating skill or checking file structure.

For an explicitly requested review without edits, report findings and proposed wording rather than applying changes. Honor an explicitly restricted edit scope while still identifying interactions outside it; report those external issues without changing them.

## Sync the custom skills repository

The user authorizes a GitHub push after every completed deconfliction pass. After validation and installation/finalization, review the diff in `~/.codex/skills`, stage only the finalized skill changes from this task, commit them with a descriptive message, and push to `origin` (`git@github.com:Arkmer/codex_skills.git`). Preserve unrelated working-tree and staged changes; do not include them in the commit. This synchronization applies to this custom skills repository, not repositories containing applications or plugin-managed artifacts.

For a review with no skill changes, push the existing branch without creating an empty commit; preserve the read-only review scope. Verify the push result and report the commit or that no new commit was needed. If authentication, permissions, remote changes, or conflicts block synchronization, retain the local work and report the blocker. Do not force-push, rewrite history, or repeat deconfliction merely because synchronization changes Git metadata. Follow explicit user overrides and required execution approvals.

## Completion report for skill creation or updates

Give the user a small report after building or updating skills. For each created or updated skill, provide:

- A clickable link to its installed SKILL.md file.
- Its purpose in no more than 30 words.
- The conditions that trigger it, with no more than 15 words per trigger.

Provide one shared deconfliction report for the complete coordinated change set, not a repeated report per skill or a second summary elsewhere. State how many existing skills changed, distinguish newly created skills, and name each changed skill with the cause of its change. Keep each cause to no more than 20 words. Distinguish the requested changes from additional changes required by deconfliction; explicitly state when no additional skills needed changes.

Keep coverage and validation concise, preserving material unresolved conflicts and limitations from step 7. If detailed review evidence already exists, link it instead of duplicating it. This reporting convention applies to skill creation and update deliverables; audit-only requests retain their requested findings format. Skill-creator still owns packaging and validation, research owns supporting evidence, and this workflow owns the single combined deconfliction report.
