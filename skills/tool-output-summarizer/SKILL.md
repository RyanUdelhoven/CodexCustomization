---
name: tool-output-summarizer
description: Extract actionable diagnostics from long, noisy, or truncated command output and point to the full log when available.
---

# Tool Output Summarizer

Use an existing complete log when available. For a command yet to run, capture stdout and stderr in an appropriate local log and preserve the command’s actual exit status. Do not rerun a side-effecting command solely to recover omitted output. If output was already truncated, say so.

Read the summary and relevant failure blocks in bounded slices. Group repeats by underlying failure; distinguish root-cause candidates from cascades. Preserve exact diagnostic codes, relevant paths and lines, failed test names, and counts when known. Report the command, status, actionable findings, and log location. Avoid quoting secrets; prefer temporary storage unless the user wants a durable log. A short diagnostic needs no special workflow.
