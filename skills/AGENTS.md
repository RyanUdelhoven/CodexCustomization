# Custom skills maintenance

## Skill review

Apply `~/.codex/skills/skill-deconfliction/SKILL.md` before finalizing custom skill creation or changes. That skill owns compatibility review, coordinated corrections, and review reporting.

For the bundled skill validator, prefer the reviewed installed executable
`~/.local/share/codex-publish/codex-skill-validate /path/to/skill` when available.
It runs the same validator with a protected YAML dependency. Otherwise use the
bundled `quick_validate.py` under normal execution permissions.

## GitHub synchronization

After creating or changing any custom skill, or completing a deconfliction pass with changes, commit the finalized task changes, merge the task branch into the verified primary branch, push that primary branch to `origin` (`https://github.com/RyanUdelhoven/CodexCustomization.git`), and clean up the completed local and remote feature branches. This is standing user authorization for that complete lifecycle after validation; required execution approvals still apply. Use the protected `codex-git publish customization` workflow in `../rules/merge-push.md`. One coordinated publication is sufficient; do not push the feature branch merely to satisfy synchronization.

After validation and installation/finalization, review the diff and stage only finalized task changes, including relevant repository instructions. Preserve unrelated working-tree and staged changes; exclude them from the commit. Use a descriptive commit message. This policy applies to the CodexCustomization repository, not application repositories or plugin-managed artifacts.

For a review with no changes, report that no new commit or publication was needed. Do not publish unrelated pending work. Verify publication and cleanup from the protected helper's receipt. Apply post-merge-cleanup's separate chat-archival eligibility checks; merge authorization does not establish exclusive chat ownership. If authentication, permissions, remote changes, or conflicts block synchronization, retain local work and report the blocker. Do not force-push, rewrite history, or repeat deconfliction merely because synchronization changes Git metadata. Follow explicit user overrides.
