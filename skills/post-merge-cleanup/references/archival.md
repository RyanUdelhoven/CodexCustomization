# Explicit chat archival only

Never archive a chat because work finished, a merge/push succeeded, or a branch lifecycle closed. `mp` publishes through its hook and leaves chats open; `mpa` is retired. Neither requests archival.

A separate direct user request to archive a specific chat authorizes only that chat. Verify its identity, honor any stated prerequisites, and use the app archival tool. Do not require exclusive branch ownership, scan other chats, repair old tracking, or recreate deleted branches. Publishing and archiving remain independent operations.

Inspect the tool result and report only confirmed success. Keep the chat open if the tool is unavailable or fails. Do not substitute deletion, bulk archival, or scheduled automation. Preserve participation history; closing a branch record never closes the chat.
