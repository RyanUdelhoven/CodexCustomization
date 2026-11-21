---
name: code-change-verification
description: Run outstanding repository-defined final gates and verify browser-facing changes reach the app the user opens, or perform explicitly requested change verification. Use react-browser-verification for React journeys and reuse eligible results.
---

# Code Change Verification

## Check at critical points

Consolidate broad validation at task completion or an explicit ready-for-review handoff, and before merge/push when required evidence is missing or invalidated. Do not run full suites, repeat live browser journeys, or rebuild/restart the user's app after every edit, skill handoff, progress update, or intermediate user message.

During development, run the smallest useful check when it informs the next decision: reproducing a reported defect, confirming its fix, crossing a consequential boundary such as persistence, authentication, or a shared API contract, or investigating an observed failure. Batch routine edits before checking. An explicitly requested check or repository-required checkpoint still runs when required; this timing policy does not waive gates.

At completion, run the applicable outstanding checks together against the final contents, including live-app verification for browser-facing changes. At merge/push, reuse that evidence and run only outstanding or invalidated checks. Later edits invalidate only evidence whose inputs or behavior they affect; a new commit, skill activation, or chat turn alone does not invalidate a result. After a failure, fix the cause and rerun the affected check, broadening only when the evidence warrants it. Stop when applicable checks pass and no relevant uncertainty remains.

Code-change-verification owns this timing policy; specialist skills own check selection and execution. Reuse their evidence without starting a second validation cycle. A progress report is not a completion claim; accurately label work awaiting final validation.

Determine scope from the actual diff, including relevant untracked files. Find the check commands and requirements in applicable repository guidance, manifests, and CI; use project tooling and documented order. Run checks suited to the change and every required gate. Reuse an observed check result when the command, scope, relevant environment, and inputs still match and project policy permits it. Run outstanding final gates against the final contents. If an auto-fix changes files, review the resulting diff and rerun checks affected by the change.

Distinguish failures caused by the change, known baseline failures, environmental blockers, and checks not run. Report partial runs as partial; when applicability of an earlier result is uncertain, rerun the affected check. Fix in-scope failures when authorized, and report commands and outcomes compactly. A prose-only change does not need the code stack unless project rules require it.

## Handoff to the mp hook

For an mp preparation request, complete final task review and outstanding required checks, reusing eligible results. Exact mp authorizes reviewing and committing all pending project changes on their owning branches from the frozen local-and-remote-branch plan. Keep branches separate, preserve other projects and branches outside that plan, and use normal commit hooks. After each prior PR advances main, normally merge verified main into the next branch and run affected checks on its resulting contents. Do not reuse checks from a different branch merely because its name or tip appears similar. Register the chat if needed, then invoke the supplied protected `codex-git complete` executable directly with actual successful check commands. Do not wrap it in workspace Python or a shell: child processes inherit that caller's sandbox. Each handoff records readiness and publishes only that branch. Continue the frozen project plan using its returned remaining list without another user commit or mp command; route merge conflicts to post-merge-cleanup for investigation and user choices. Validate the resolved contents and affected behavior after answers, then hand off under a valid publication request. Stop on failed checks, active worktrees, partial publication, or unresolved scope.

Outside an explicit publication request, do not automatically commit or publish. A new-repository request under [repository-bootstrap](../repository-bootstrap/SKILL.md) authorizes its initial local commit; affirmative GitHub setup consent separately authorizes its first baseline push. Optional `--prepare` can record already-reviewed clean commits, but it does not run checks or establish user publication intent. Follow [merge/push execution](../../rules/merge-push.md#preparation-within-mp). Never invent verification evidence.

## Verify the app the user opens

Before reporting browser-facing work complete, identify the user's actual app URL and trace it to the serving process: for example, a native server, Docker Compose service, or managed proxy upstream. Use session context, project configuration, and observed runtime state; an isolated test server or preview URL does not establish what the user's browser receives. If discovery cannot resolve the intended URL or process, ask for the missing information and report availability as unverified.

Compare the running app with the changed checkout and build. Switching Git branches, building local files, and passing isolated browser tests do not update an existing container image or another process's build output. When necessary and within the authorized task, rebuild or restart the actual serving process using the project's existing lifecycle. For Compose, confirm the checkout/build context, project identity, compose files, and target service before using an appropriate command such as `docker compose up -d --build`; avoid starting a second stack in place of updating the user's stack. Preserve databases, uploads, volumes, bind mounts, and existing configuration. Never delete persistent data or reset volumes as routine verification. Follow existing Docker or Coulson workflows when relevant; a local refresh does not authorize unrelated publication or production deployment.

After updating the process, check readiness and request the actual app URL. Verify that it serves the changed build using concrete evidence, such as a served JavaScript asset matching the new build, an exposed build identifier, or the changed behavior through that URL. Container health or an HTTP success alone does not prove freshness. Account for browser caches or service workers when they can retain an older build. Reuse applicable React browser verification evidence and exercise any remaining journey through the user's URL as needed.

Report repository/build checks, isolated browser results, and availability at the user's URL as distinct outcomes. Name the URL and serving process, any rebuild/restart performed, and the evidence connecting the served app to the change. State whether the user's open tab needs a refresh, hard refresh, or another verified update step. If runtime access, authorization, or freshness evidence is missing, state that limit instead of reporting browser-facing completion.
