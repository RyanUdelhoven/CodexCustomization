---
name: coulson-ready
description: Prepare, register, troubleshoot, and verify a local web application for Coulson bookmark-triggered startup on macOS. Supports existing Docker Compose and native managed apps; use dockerize-app when container packaging is requested or missing from a requested Docker workflow.
---

# Make an application Coulson ready

Deliver a verified local browser URL that starts the managed app when visited. Coulson integration does not require Docker. Use existing suitable packaging; if Docker is requested, let dockerize-app own Dockerfiles, Compose services, readiness, and persistence. Reuse its checks and resolve only integration-specific gaps here.

## Discover the installed environment

Read repository instructions and existing app configuration. Check coulson --version and command-specific --help before constructing commands. This skill was researched against installed Coulson 0.4.2 on macOS; online master documentation includes newer commands and may have stale examples. Verify configuration keys, provider selection, and Docker port discovery against the installed release's documentation or source when uncertain. Do not invent flags or upgrade Coulson to make an example work.

Inspect existing registrations, daemon health, effective apps root, domain suffix, listening ports, forwarding, and certificate trust. Prefer bounded diagnostics such as coulson ls and coulson doctor; avoid dumping resolved environments or secret files. Keep existing working system settings. Coulson and, for containers, the Docker engine must already run for bookmark startup; an app URL does not launch a stopped Docker desktop engine or Coulson daemon.

## Configure the managed app

Choose a unique, readable name, preserving an existing name when suitable. Determine whether the app should use Docker Compose, another supported managed provider, or static hosting. A manually registered port proxy cannot start its target server. Native startup must work from the daemon's environment, without relying on a terminal's current directory, aliases, or activated environment.

For Compose, establish which compose file and web service the installed version detects. Inspect mixed repositories containing package.json, Procfiles, and Compose files for provider ambiguity. Use explicit kind = "docker" only when supported and needed. Ensure Coulson owns the full Compose lifecycle rather than wrapping detached Compose commands in a managed shell process. Verify the daemon can find Docker and reach its engine.

Keep container listening port, host-published port, Coulson upstream, and public gateway port distinct. Verify the selected upstream is the web entrypoint, especially with multiple published services. Inspect actual installed port-discovery behavior before choosing fixed versus dynamic mappings; do not assume Coulson's PORT variable automatically changes the application's listener or Compose mapping. Keep per-project ports collision-free and normally publish to loopback.

For fixed host ports, use local-port-manager to import or allocate the project/service assignment and reuse assignments from dockerize-app. Reconcile the registry with actual Compose and upstream settings before startup. Preserve verified dynamic allocation; never assume different domain names eliminate fixed-port collisions.

Add only necessary per-app configuration. Configure exact allowed hostnames, origin/CSRF settings, redirects, callback URLs, WebSockets, and frontend API URLs for the chosen domain. Avoid wildcard trust or globally disabled host checks. Preserve development hot reload when applicable. Avoid duplicating manual reverse proxies when Coulson can provide the required routes.

Register a managed directory using installed-version-supported mechanics. The documented directory pattern is a symlink from the effective apps root to the absolute project directory. Inspect an existing destination before writing; reuse a matching link and never overwrite a different app. Scan and inspect warnings, registered provider, and process state. Do not mistake successful registration for successful startup.

Use the observed suffix, scheme, and gateway port to construct the bookmark URL. Default HTTP often needs :18080 without forwarding, but discover actual settings. HTTPS requires working local certificate trust. Configure privileged forwarding or trust only when needed for the requested URL and within permissions. Keep local-only requests local; public tunnels and LAN exposure require their own user request.

## Prove bookmark startup

1. Confirm the target is managed and can stop safely; avoid disrupting active jobs or user sessions.
2. Stop only this app through Coulson. Verify its managed process or containers have stopped.
3. Visit the actual domain URL without manually starting the app. Allow bounded cold-start time, including builds.
4. Verify the app becomes ready and a meaningful page/API journey works through that URL.
5. Repeat stop/visit once to check reproducibility and persistent test data when applicable.

Poll only as needed for readiness; requests themselves may reset idle timers. Distinguish the gateway's loading page from the application's response. Check logs on failure without disclosing secrets. Test browser DNS and HTTPS directly: a forged Host header alone does not prove a bookmark works. Reuse react-browser-verification for React journeys, and code-change-verification for outstanding repository gates.

Verify idle shutdown with the effective timeout if practical without changing shared settings. Otherwise report automatic idle shutdown as untested; manual stop/visit verifies cold startup only. Do not claim background workers remain alive if Coulson stops their stack. Preserve volumes; never use down -v or delete data during lifecycle tests.

Update concise project instructions with the bookmark URL, prerequisites, normal commands, and persistent-data location. Report registration/provider, files changed, checks performed, and any remaining blocker. Provide precise rollback for this app's link and configuration without uninstalling Coulson or removing volumes. If registration writes need permissions, finish reviewable project files first and request only the necessary action.

Reference: [Coulson repository and release documentation](https://github.com/ratazzi/coulson), [v0.4.2 changes](https://github.com/ratazzi/coulson/releases/tag/v0.4.2). Use installed help as the CLI authority.

## Scope with other workflows

For an existing Sites project, preserve its source and hosting conventions. Local Docker or Coulson work does not request a new hosted Site or publication; use Sites only for separately requested Sites operations. Ordinary packaging does not require an architecture review, refactor, or documentation audit. Update directly relevant run instructions and reuse existing verification evidence.
