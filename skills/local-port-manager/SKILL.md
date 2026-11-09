---
name: local-port-manager
description: Manage persistent local host-port assignments across projects, allocate or import fixed ports, diagnose collisions, and update affected project configuration. Use directly for local port management or alongside Docker and Coulson setup when fixed host ports need coordination. Leave verified dynamic allocation in place.
---

# Manage local project ports

Own cross-project fixed host-port bookkeeping. Keep one machine-local registry at `~/.codex/local-ports/ports.sqlite3`; use the bundled Python 3 helper rather than editing the database by hand. Registry assignments survive stopped applications. They are bookkeeping, not operating-system reservations or a background daemon. Other programs can still bind assigned ports; verify actual startup.

## Inspect before allocating

Identify the absolute project root, named service, transport (default TCP), host bindings, internal container ports, existing assignments, and configuration sources. Canonical project paths distinguish same-named projects; worktrees get separate identities by default. For moved projects, explicitly migrate assignments after verifying the old location and ownership; do not silently duplicate or discard them.

Inspect relevant existing Compose/Coulson registrations and project configuration. Import known fixed assignments before allocating new ones. Registry coverage is limited to imported projects; checking listeners cannot reveal unregistered stopped apps. Do not claim a complete machine inventory without actually identifying the projects in scope. Do not scan unrelated private directories by default.

Preserve working verified dynamic allocation, including native apps accepting Coulson's PORT. Docker container-internal ports may repeat; coordinate only published host ports. Avoid publishing private databases merely to assign them ports. Default new local bindings to loopback, preserving deliberate existing access requirements.

## Use the registry

Set the helper path to this skill's `scripts/ports.py`. Global --registry precedes the subcommand; omit it for the canonical machine registry. For tests, use an isolated temporary registry, never a fallback production registry. Request native filesystem approval when the canonical location requires it; do not create competing registries to evade permissions.

```sh
python3 /absolute/skill/path/scripts/ports.py list
python3 /absolute/skill/path/scripts/ports.py allocate --project /absolute/project --service web
python3 /absolute/skill/path/scripts/ports.py allocate --project /absolute/project --service api --port 3201
python3 /absolute/skill/path/scripts/ports.py check
python3 /absolute/skill/path/scripts/ports.py release --project /absolute/project --service api
```

Allocation reuses an existing assignment, otherwise selects a port from 3000–9999 unless a different range or exact port is requested. SQLite transactions serialize cooperating allocations, including separate Codex chats. Reservations are conservative across host addresses for each transport. TCP and UDP have separate assignments; reserve both explicitly when necessary. The helper probes IPv4 and supported IPv6 wildcard binds but cannot hold the socket until the application starts.

An occupied requested port is rejected. Use `--adopt-occupied --port NUMBER` only after verifying that its listener/container belongs to this exact project and service. Never use adoption to bypass another registry assignment. A reused occupied assignment remains unchanged: `bind_available: false` may indicate the correct running app, not a conflict. Identify ownership through scoped listener/process or Docker inspection before deciding. Inspection reports availability, not process ownership or application health.

## Apply and verify

Update the project's effective configuration using the allocated host port, preserving existing conventions and unrelated values. Trace environment precedence, Compose interpolation, frontend API URLs, proxy targets, and callback URLs as needed. Keep local machine values in ignored configuration when appropriate; retain portable defaults/examples. Avoid revealing secrets in resolved configuration output.

For Docker work, dockerize-app owns container packaging and service lifecycle. For Coulson work, coulson-ready owns registration and URL lifecycle testing. Pass service, protocol, host port, internal port, and evidence between workflows; do not allocate twice. These skills call this skill for assignment bookkeeping, then resume their own tasks. Port management alone does not request Docker conversion, Coulson registration, Sites publication, or a general refactor.

Verify the final configuration and start the scoped service when authorized. If its port is occupied by unrelated software, do not kill that software. For a new unverified assignment, release it and retry allocation at most twice, updating dependent config together. Changing an established assignment requires tracing its consumers first; report a concrete blocker if safe migration needs user input. After that bounded retry, stop guessing and report the owner or observed failure.

Never release assignments merely because apps stop. Release on requested retirement or confirmed migration; ensure old configuration no longer claims the port. Release changes the registry only, never processes or files. If preparation fails, report any retained reservations and partial config changes; undo only new reservations/config created by this task when safe. Keep old assignments until their consumers have migrated.

Use applicable repository gates through code-change-verification and reuse browser/lifecycle evidence from the owning skill. Report assignments, registry location, modified files, actual checks, unimported-project coverage gaps, and any blocker. No new registry is created until an assignment mutation is requested.

Sources: [Compose ports](https://docs.docker.com/reference/compose-file/services/#ports) describes host/container mappings; [Python SQLite transactions](https://docs.python.org/3/library/sqlite3.html#transaction-control) informs serialized bookkeeping. Actual binds remain the authority for runtime availability.
