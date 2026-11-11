---
name: code-change-verification
description: Run outstanding repository-defined final gates and verify browser-facing changes reach the app the user opens, or perform explicitly requested change verification. Use react-browser-verification for React journeys and reuse eligible results.
---

# Code Change Verification

Determine scope from the actual diff, including relevant untracked files. Find the check commands and requirements in applicable repository guidance, manifests, and CI; use project tooling and documented order. Run checks suited to the change and every required gate. Reuse an observed check result when the command, scope, relevant environment, and inputs still match and project policy permits it. Run outstanding final gates against the final contents. If an auto-fix changes files, review the resulting diff and rerun checks affected by the change.

Distinguish failures caused by the change, known baseline failures, environmental blockers, and checks not run. Report partial runs as partial; when applicability of an earlier result is uncertain, rerun the affected check. Fix in-scope failures when authorized, and report commands and outcomes compactly. A prose-only change does not need the code stack unless project rules require it.

## Verify the app the user opens

Before reporting browser-facing work complete, identify the user's actual app URL and trace it to the serving process: for example, a native server, Docker Compose service, or managed proxy upstream. Use session context, project configuration, and observed runtime state; an isolated test server or preview URL does not establish what the user's browser receives. If discovery cannot resolve the intended URL or process, ask for the missing information and report availability as unverified.

Compare the running app with the changed checkout and build. Switching Git branches, building local files, and passing isolated browser tests do not update an existing container image or another process's build output. When necessary and within the authorized task, rebuild or restart the actual serving process using the project's existing lifecycle. For Compose, confirm the checkout/build context, project identity, compose files, and target service before using an appropriate command such as `docker compose up -d --build`; avoid starting a second stack in place of updating the user's stack. Preserve databases, uploads, volumes, bind mounts, and existing configuration. Never delete persistent data or reset volumes as routine verification. Follow existing Docker or Coulson workflows when relevant; a local refresh does not authorize unrelated publication or production deployment.

After updating the process, check readiness and request the actual app URL. Verify that it serves the changed build using concrete evidence, such as a served JavaScript asset matching the new build, an exposed build identifier, or the changed behavior through that URL. Container health or an HTTP success alone does not prove freshness. Account for browser caches or service workers when they can retain an older build. Reuse applicable React browser verification evidence and exercise any remaining journey through the user's URL as needed.

Report repository/build checks, isolated browser results, and availability at the user's URL as distinct outcomes. Name the URL and serving process, any rebuild/restart performed, and the evidence connecting the served app to the change. State whether the user's open tab needs a refresh, hard refresh, or another verified update step. If runtime access, authorization, or freshness evidence is missing, state that limit instead of reporting browser-facing completion.
