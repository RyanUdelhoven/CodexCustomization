# Custom Codex skills

Personal skills installed directly in `~/.codex/skills/`. Each skill has a root `SKILL.md`; supporting scripts, references, tests, and agent metadata live alongside it.

Codex-managed `.system/` skills and generated local files are excluded from version control.

## Updating skills

Edit the installed skill, follow applicable skill-authoring and deconfliction instructions, then review and commit the changes:

```sh
git status
git diff
git add <skill-name>
git commit -m "Describe the skill change"
```
