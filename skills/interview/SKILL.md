---
name: interview
description: Conduct adaptive user interviews to clarify app features, domain language, problems, workflows, bugs, experience design, technical constraints, or priorities. Recommend a curated questioning path before interviewing. Proactively offer for new features, components, and behavior-changing code requests with meaningful unanswered requirements; also use when the user requests an interview or requirements discovery. Excludes fully specified mechanical edits, direct factual answers, and routine checks.
---

# Interview to guide the work

Own the questioning process and an actionable brief. Use the current prompt, earlier answers, and narrowly relevant project evidence to find useful unanswered questions. Do not make users repeat known information or answer facts the repository can establish. Interview before implementation that depends on those answers; continue independent inspection while waiting.

## Decide whether questions are useful

Assess coverage before showing a path menu. When the request and available context cover the material decisions, skip both the menu and interview questions. Briefly say, “The requirements are covered, so I’ll skip questions and proceed.” This is a progress note, not a confirmation request. Do not create an interview brief for an interview that did not occur.

For code affecting the visual UI, roughly 90% clarity is sufficient to proceed: prefer a reviewable implementation and iteration over questioning about the remaining subjective styling details. Treat this as a practical sufficiency judgment, not a calculated confidence score. Ask only when the remaining gap materially changes behavior, scope, data, accessibility, integration, or another consequential requirement. Do not apply the visual threshold to unrelated backend or domain uncertainties in a mixed task.

Honor an explicit request to interview even when requirements seem covered, and an explicit choice to skip optional questions. Required authorization or specialized decisions retain their own rules.

## Choose the questioning path first

Before substantive interview questions, use the available structured user-question tool to ask which path to use. Recommend the best fit first, mark it Recommended, and explain its relevance in one sentence grounded in the request. Usually offer two or three plausible paths rather than the entire catalog; offer fewer when only one fits. Include an explicit “Skip questions and proceed” choice in the selection prompt. Keep space for it by shortening the curated path list when tool limits require it. Let the user request any other path or a combination through free text or a supported extra option. If the tool is unavailable, use a concise text menu following the environment's question notification rules.

Wait for the user's choice; a preselected recommendation or silence is not an answer. Do not mix interview questions into the selection batch. An explicitly named path or combination already selects it: acknowledge and begin without asking again. If the user requests the full menu, show all eight paths. Reuse the selection for the current task; do not reopen the menu on every follow-up. Offer a different path when new uncertainty warrants it, rather than silently changing interview scope.

Keep questions answerable in normal chat as well as the structured tool. When yielding for a path choice, include the actual selection question and offered paths in the final response, including the recommendation and “Skip questions and proceed” option. Apply the same rule to every pending substantive question batch: restate each question and its relevant choices concisely, with consistent recommendations and material tradeoffs, and allow free text. Do not end with only a summary or a reference to the question UI; commentary alone does not preserve pending questions at turn completion. Omit answered or withdrawn questions. Continue using the structured tool and its existing notification behavior; repeating the text does not require another tool call or sound alert.

| Path | Recommend when | Read after selection |
|---|---|---|
| App Features | New or changed functionality, components, behavioral requirements | [App Features](references/app-features.md) |
| Domain Language / DDD | Terms conflict, concepts are ambiguous, prompts and code disagree | [Domain Language](references/domain-language.md) |
| Problem Discovery | Proposed solution precedes a clear problem or outcome | [Problem Discovery](references/problem-discovery.md) |
| Workflow and User Journey | Roles, steps, handoffs, exceptions need definition | [Workflow](references/workflow.md) |
| Bug Investigation | Expected and observed behavior diverge | [Bug Investigation](references/bug-investigation.md) |
| Design and Experience | Usability, information priority, interaction or visual intent is unclear | [Design and Experience](references/design-experience.md) |
| Technical Constraints | Integration, data, compatibility or operating limits affect feasibility | [Technical Constraints](references/technical-constraints.md) |
| Prioritization and Scope | Competing outcomes require sequencing or tradeoffs | [Prioritization](references/prioritization.md) |

Do not force every code task through an interview. For feature requests, actively look for overlooked decisions and offer the path when they matter, even when the user has not asked for questions. Fully specified edits and explicit requests to proceed without interviewing should continue directly. Explicit interview requests still apply to otherwise simple tasks. Never manufacture uncertainty to justify a questionnaire.

## Conduct an adaptive interview

Read only the selected path references. For combinations, agree on an order suited to the dependency: clarify the problem before selecting features, or terms before specifying domain rules. Keep one shared set of known facts and decisions.

Ask small batches, typically one to three focused questions. Select questions by how much the answer changes implementation, meaning, or success; question banks are prompts, not mandatory checklists. Tailor wording to the user's domain. Explain consequential tradeoffs briefly and provide plausible choices where helpful, including a reasoned recommendation when evidence supports one. Allow free text and uncertainty; do not invent an informed recommendation or steer toward a preferred implementation without evidence.

Adapt subsequent questions to answers, seeking concrete examples and counterexamples when abstract wording hides ambiguity. Separate confirmed facts, repository observations, user preferences, assumptions, and unresolved decisions. Surface contradictions neutrally and resolve only the material disagreement. Reuse previous answers and specialized skills' settled decisions. Avoid a fixed question quota or repeating optional questions after the user says enough. Remind the user once when substantive questioning begins that they can say “skip” at any point; honor that without another confirmation.

Stop when the requested outcome, selected path's material decisions, and observable success criteria are clear enough for the next authorized step, or when the user stops the interview. If an unresolved choice blocks that step and the interview remains active, ask that focused question; proceed with independent work. When the user skips or ends questioning, use reasonable reversible assumptions, label material assumptions and actual blockers, and continue authorized work. Do not reopen optional questions; do not invent consent for actions requiring authorization.

## Close with a usable brief

Summarize the outcome, decisions, relevant acceptance examples, scope boundaries, and unresolved assumptions concisely in chat. Include the selected path's useful output, such as terminology mappings or a reproduction scenario. Do not impose every field on every interview. A brief is a record of answers, not a new approval gate: continue already-authorized implementation when sufficiently specified. Interview-only requests end with the brief. Creating project documents, changing code terminology, or recording persistent defaults requires the relevant task authorization.

## Coordinate with existing workflows

This skill owns path selection, interview sequencing, answer reuse, and the brief. Specialized skills own implementation, research, verification, and their mandatory decisions. Combine compatible questions into interview batches after path selection; preserve required wording and never replace a specialized approval with a generic answer.

- `task-research` owns research and ranked solution options; use the brief as input, not a reason to repeat framing questions.
- `component-library-reuse` owns inspecting candidates and deciding reuse. Ask with actual candidate evidence during a suitable batch.
- `vantage-component-handoff` owns the Vantage question and constraints; do not infer its answer from a design preference.
- `software-design-review` owns architecture assessment; technical interviews establish constraints without claiming a design review.
- React and other implementation skills consume the brief; their triggers and checks remain applicable.
- Project instructions retain questions such as Coulson registration, photo ignoring, and publication conflict choices. An interview cannot waive them.
- Skill creation and integration do not automatically trigger this interview. If the user requests discovery for those tasks, adapt Workflow, Technical Constraints, or Prioritization to clarify triggers, inputs, outputs, ownership, and handoffs; do not force app-specific questions or add another path. `skill-creator` owns authoring and validation.
- `skill-deconfliction` owns capability amendment choices; `package-skill` owns transfer prompts. Do not turn ordinary requirements discovery into skill creation.

An interview does not authorize purchases, external actions, publication, or unrelated files. Do not introduce new documentation or implementation solely because a questioning path mentions it.
