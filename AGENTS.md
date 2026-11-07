# Custom skills maintenance

## Skill review

Apply `skill-deconfliction/SKILL.md` before finalizing custom skill creation or changes. That skill owns compatibility review, coordinated corrections, and review reporting.

## GitHub synchronization

After creating or changing any custom skill, or completing a deconfliction pass, commit the finalized task changes in this repository and push to `origin` (`git@github.com:Arkmer/codex_skills.git`). This is standing user authorization; required execution approvals still apply. One push after a coordinated task is sufficient.

After validation and installation/finalization, review the diff and stage only finalized task changes, including relevant repository instructions. Preserve unrelated working-tree and staged changes; exclude them from the commit. Use a descriptive commit message. This policy applies to this custom skills repository, not application repositories or plugin-managed artifacts.

For a review with no changes, push the existing branch without creating an empty commit. Verify the push result and report the commit or that no new commit was needed. If authentication, permissions, remote changes, or conflicts block synchronization, retain local work and report the blocker. Do not force-push, rewrite history, or repeat deconfliction merely because synchronization changes Git metadata. Follow explicit user overrides.
