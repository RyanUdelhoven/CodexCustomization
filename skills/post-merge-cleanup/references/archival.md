# Archive a completed chat

## Explicit archival

`mpa` directly authorizes archiving the verified current chat after successful publication and branch cleanup, provided no unfinished work or pending request remains in that chat. Do not investigate exclusive branch ownership or other chat history for this explicit request. Missing creation records, multiple participants, or a closed tracking lifecycle do not by themselves block it. Never archive other participants' chats. Keep-open instructions override archival; failed publication or incomplete cleanup keeps the chat open.

A standalone direct request to archive a specific chat independently authorizes that operation, even after a lifecycle has closed. Verify the target and finish any explicitly required prerequisites; do not require tracking repairs or another confirmation. This standalone operation does not require new Git publication.

Use the app archival tool with the verified target identity and inspect its result. Report only confirmed success. Close any currently open publication lifecycle after the decision and archive attempt; do not reopen an old lifecycle. Missing tools or failed archival keeps the chat open and must be reported.

## Conditional automatic archival

The ownership and open-lifecycle checks below apply only when archival was not explicitly requested, such as the automatic preference after `mp` or standing skill publication.

Inspect and retain the participation record before deleting branches.

After a verified merge into the repository's primary/default branch and a successful push of that target to `origin`, archive the originating chat only if one verified chat managed the branch from creation through integration. Determine the primary branch from repository guidance or verified remote metadata; do not assume `main`. Merging into another target or pushing only another remote does not trigger archival. A failed push never triggers archival. Explicit instructions to retain the chat override this preference.

Use feature-branch's [participation protocol](../../feature-branch/references/chat-participation.md). Require a complete, open lifecycle, one distinct participant matching the recorded origin, and no evidence of other managing chats or missing history. The current integrating chat must match that origin. Verify that the chat's task is complete and no other active branch, unfinished work, or pending request in that chat would be hidden by archival. When merging multiple branches, assess all of them before any archival; if any participating branch has multiple managing chats, archive nothing for that merge workflow.

Use the local tracker's normalized identities: an omitted Codex host and `local` represent the same local host for the same chat ID. Distinct explicit hosts remain distinct. Duplicate alias records alone do not prove multiple managing chats. A previously closed lifecycle remains ineligible for automatic archival; explain that a direct request to archive this chat can proceed independently, rather than implying Git work remains.

When multiple chats managed a branch, archive none of those chats. After the successful push, report: “Multiple chats managed this branch; no chats were archived.” Name or link verified participants when useful. If evidence is incomplete instead, report that ownership could not be verified and no chats were archived; do not claim multiple chats without evidence. Missing tools or tracking never block authorized merge/push or branch cleanup.

Complete branch cleanup and report the merge, push, cleanup outcome, and archive decision before archiving. A material cleanup blocker or unfinished follow-up keeps the chat open. Use the available `set_thread_archived` tool with `archived: true` and the verified originating chat identity; omit the thread ID only when targeting the verified current chat. Preserve its source and any verified Codex host. Inspect the tool result and report archival success only when confirmed. If it fails or is unavailable, keep the chat open and report the limitation. Do not substitute permanent deletion, worktree archival, bulk archival, or a scheduled automation.

Close the participation lifecycle after the decision and any archive attempt, following that participation protocol. Report the confirmed outcome in the final response. This skill does not authorize bulk stale-branch deletion, unrelated chat archival, or unrelated repository changes.
