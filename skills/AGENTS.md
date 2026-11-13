# Custom skills maintenance

## Skill review

Apply `~/.codex/skills/skill-deconfliction/SKILL.md` before finalizing custom skill creation or changes. That skill owns compatibility review, coordinated corrections, and review reporting.

For the bundled skill validator, prefer the reviewed installed executable
`~/.local/share/codex-publish/codex-skill-validate /path/to/skill` when available.
It runs the same validator with a protected YAML dependency. Otherwise use the
bundled `quick_validate.py` under normal execution permissions.

## Publication is explicit

After skill changes, validate and report the finished work on its feature branch. Do not automatically commit, merge, push, clean up that branch, or archive its chat. The former standing publication authorization is revoked. Wait for an explicit request covering publication. Standalone `mp` explicitly authorizes final review, outstanding checks, task-only staging/committing, preparation, and protected publication; `mpa` has no workflow meaning.

For an mp preparation request from the hook, complete required review/checks, commit only reviewed task files, and call the supplied `--complete` handoff in the same turn. No separate user commit/preparation command is needed. Follow [merge/push execution](../rules/merge-push.md), preserve unrelated work, and report genuine blockers. Outside an explicit publication request, leave work on its feature branch. Publication never authorizes archival.

For a review with no changes, report the findings without publication. When publication is requested, verify it and branch cleanup from the protected receipt. Retain local work and report blockers; never force-push or repeat deconfliction merely because Git metadata changed. Keep chats open unless the user separately requests archival.
