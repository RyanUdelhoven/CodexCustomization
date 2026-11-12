# Skill-run token measurements

The dashboard's **Skill runs** view measures model attempts that start while explicit skill markers are active. It is a workflow interval measurement, not isolated instruction overhead, monetary cost, quota use, or proof of savings. It includes repeated context, other active skills, reasoning, and instrumentation overhead. A controlled comparison belongs to context-audit.

## Record an interval

Prefer the reviewed installed `~/.local/share/codex-publish/codex-skill-usage` directly for `start`, `finish`, and `status`. Its isolated interpreter and protected dependencies avoid a general Python allowance. The source commands below are fallback examples when it is absent and retain normal approval. Hooks remain configured separately; installation alone does not change hook trust or reload the app.

```text
python3 ~/.codex/skills/approval-review/scripts/skill_usage.py start --session VERIFIED_CHAT_ID --skills approval-review context-audit --cwd /absolute/project --task "Verified task title"
python3 ~/.codex/skills/approval-review/scripts/skill_usage.py finish --runs RETURNED_RUN_ID_1 RETURNED_RUN_ID_2
```

Start only the skills actually used, before their substantive workflows; retain IDs and finish each when its workflow ends. Batch simultaneous starts/finishes. A skill already active in the same session/agent scope must be reused or finished first. Finishes are idempotent and validate every supplied ID before changing anything. Interrupted runs remain visibly running; use `finish --runs ID --abandoned` only when the user or observed workflow confirms abandonment. Do not fabricate earlier boundaries or silently close other agents' runs.

The default scope includes all agents reporting the same session ID. Supply `--agent-id VERIFIED_AGENT_ID` to restrict a run to that agent. The UI shows this scope. Never infer chat identity from its title. When exact task titles are unavailable, preserve the session ID and show Unknown. Root AGENTS.md supplies automatic marker guidance for future chats; user instructions may disable it. Instruction-based markers require agent cooperation and are not guaranteed runtime skill-activation events.

## Hook collection and activation

The separate PreModelRequest and PostModelRequest handlers in hooks.json run `skill_usage.py capture`. They record identity, timestamps, request status, active run IDs, and known numeric token fields only. No prompts, responses, transcript contents, or error text are stored. Journals and marker state remain private beside approval evidence. Failures return success with a short diagnostic and no decision/context output.

Codex requires review/trust for new non-managed hook definitions through Settings > Hooks or `/hooks`; never edit trust hashes or bypass review. Reload if the app retains its previous hook configuration. Verify naturally occurring Pre/Post events and non-null usage before claiming live token capture. Unit tests are not live activation evidence. Approval capture and sound remain independent.

Official source checked: [Codex hooks](https://learn.chatgpt.com/docs/hooks), especially PreModelRequest/PostModelRequest and hook trust. PostModelRequest reports per-attempt counts when available; null counts are possible. Missing fields remain unknown. No transcript backfill is performed.

## Accounting and limits

- Input includes cached input; cached tokens are displayed separately, not added again.
- Reasoning is an output subset; do not add it again to output.
- Derive total from input plus output only when both are known.
- Failed/cancelled attempts retain their reported usage and request status.
- Shared requests appear in every active run; unique totals count each request once.
- No observed requests means unmeasured, never a proven zero-token workflow.
- Missing starts, missing ends, ambiguous concurrent attempts, and null usage limit coverage.

Pre/Post pairing uses session, turn, agent, and supplied request identity when available. Without a request identity, pair only a single pending attempt in that scope. Ambiguous attempts remain without attributed counts rather than matching nearest timestamps; quarantine unidentified posts in that scope for the remaining turn to prevent late-post misattribution. Each run's samples expose the original local request identity and shared run IDs. A whole attempt is attributed based on its start marker membership, even if a run finishes before its Post hook; no fractional allocation is invented. Interval overlap does not establish causal usage.

Approval events in the same session and time window link as supporting evidence, not proof of command execution or token causation. Agent-specific runs may still list same-session approval events because PermissionRequest does not reliably expose agent identity. Historical approvals have no run totals without recorded boundaries.

`skill_usage.py status` prints the local run measurements and hook health. Redacted dashboard/CLI exports include numeric measurements, coverage, and run IDs while omitting skills, names, session IDs, paths, sample identities, and task text. The dashboard remains read-only; marker commands own changes.

The protected tracker/usage installation is produced by `scripts/install-tracker-allowances.py` after review. It copies the recorder, both entry points, their fixed local dependencies, and the dashboard HTML. No downloads or runtime imports from the checkout occur. Installing or replacing those copies requires approval. Source updates do not alter installed behavior; re-review and reinstall deliberately. The installer and arbitrary test discovery retain approval.

## Verify

Run `python3 -m unittest discover -s skills/approval-review/scripts -p 'test_*.py'`. Verify exact interval membership, shared unique totals, token subsets, retries, missing/null counts, concurrent ambiguity, abandoned runs, private storage, exports, and HTTP rendering. Verify the **Skill runs** tab through the running app URL after restarting its process. A missing live hook produces an honest unmeasured run.
