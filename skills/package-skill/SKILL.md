---
name: package-skill
description: Package conversation context into a copyable prompt for building a skill in another project or chat. Use for “package this for a skill,” “turn this conversation into a skill-building prompt,” or equivalent transfer requests. Direct skill creation belongs to skill-creator.
---

# Package a skill-building prompt

Distill the relevant conversation into a self-contained instruction to a receiving agent that will create the skill. Return the prompt in one fenced `text` code block so the user can copy it as a unit. Packaging alone does not create files, install a skill, start another chat, or send the prompt anywhere.

## Select and distill context

Resolve “this” from the user's selected topic or the current conversation. Preserve explicit corrections, final decisions, required defaults, exceptions, and reasons that affect future behavior. Extract the reusable workflow rather than narrating the session or copying its transcript. Include concrete successful examples and failure lessons when they materially guide implementation; distinguish observed results from proposals and unverified assumptions.

Use the relevant conversation already available. Consult named artifacts only when needed to make the prompt usable. Do not scan unrelated history, repositories, or personal material. If essential context is missing, ask one focused question; otherwise package what is known and label remaining unknowns without inventing answers.

## Write the receiving agent's task

Start with a direct instruction to create or update the described skill in the receiving project's environment. Fill in the following content with actual conversation details, including only applicable sections:

- Purpose, intended users, and the recurring problem the skill should solve.
- Suggested skill name, natural-language triggers, and nearby requests outside its scope.
- Required behavior, inputs, outputs, constraints, and meaningful exceptions.
- Decisions and rationale, representative examples, pitfalls, and acceptance criteria.
- Relevant source evidence, necessary resource contents, and unresolved questions.

Make the prompt understandable without access to this chat. Replace incidental source-machine paths and project names with descriptive roles when portability requires it. Preserve exact identifiers only when behavior depends on them. A local file link is not a portable dependency: inline essential material or identify what must be supplied in the destination. Exclude credentials, irrelevant personal information, superseded attempts, and unrelated operational state.

Tell the receiving agent to inspect its project's instructions and existing skills, reuse or extend an appropriate skill when warranted, and adapt implementation details to that environment. Request its available skill-creation, deconfliction, and validation workflows without assuming source-machine skill paths or tools exist there. For artifact-template skills, defer construction to the destination's template workflow. Carry forward relevant research and evidence; identify freshness checks the builder needs rather than researching merely to produce this package.

Preserve the user's chosen scope. Do not generalize a one-time workaround into a universal rule or treat historical permissions as authorization for destination actions. Define observable acceptance examples appropriate to the workflow, including a triggering request and a nearby non-triggering request.

## Output

Return one ready-to-paste prompt in one fenced `text` block, with no essential instructions outside it. Use a fence longer than any contained backtick sequence if quoting code. Avoid empty template headings, unnecessary placeholders, and a second competing version. A brief introduction is optional; do not claim the destination skill has been built or installed.

This skill owns the transfer prompt. Skill-creator owns actual skill construction; handoff-writer owns resumable project-work handoffs. When the user explicitly requests packaging for later creation, finish with the prompt rather than invoking those creation workflows locally. A request simply to “create a skill” does not imply packaging.
