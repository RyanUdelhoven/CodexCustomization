---
name: coulson-ready
description: Prepare, register, troubleshoot, and verify a local web application for Coulson bookmark-triggered startup on macOS using managed Docker Compose. Use dockerize-app when container packaging is missing or needs repair.
---

# Make an application Coulson ready

Deliver a verified local browser URL that starts a Coulson-managed Docker Compose app when visited. Docker Compose is required for Coulson onboarding and provider changes, matching the established projects. Reuse suitable existing container packaging; otherwise apply dockerize-app, which owns Dockerfiles, Compose services, readiness, and persistence. Reuse its checks and resolve only integration-specific gaps here. Do not substitute Procfile/native processes, static registrations, or manual port proxies unless the user explicitly overrides this Docker requirement. Missing Docker tooling or incompatibility is a blocker to resolve or report, not permission to fall back. Read-only troubleshooting may inspect legacy providers; convert only the app within the authorized setup or migration scope.

## Discover the installed environment

Read repository instructions and existing app configuration. Check coulson --version and command-specific --help before constructing commands. This skill was researched against installed Coulson 0.4.2 on macOS; online master documentation includes newer commands and may have stale examples. Verify configuration keys, provider selection, and Docker port discovery against the installed release's documentation or source when uncertain. Do not invent flags or upgrade Coulson to make an example work.

Inspect existing registrations, daemon health, effective apps root, domain suffix, listening ports, forwarding, and certificate trust. Prefer bounded diagnostics such as coulson ls and coulson doctor; avoid dumping resolved environments or secret files. Keep existing working system settings. Coulson and, for containers, the Docker engine must already run for bookmark startup; an app URL does not launch a stopped Docker desktop engine or Coulson daemon.

Before onboarding or changing shared daemon settings, record existing apps' providers, URLs, and runtime status. Identify which existing apps depend on Docker versus native executables. Treat these as regression checks: successful startup of the new app alone does not validate shared changes.

For macOS launchd installations, inspect the loaded service's executable and effective PATH, not only the interactive shell. A GUI-installed or regenerated LaunchAgent can lose custom environment settings. If Coulson reports `docker not found in PATH`, check executable discovery before blaming missing containers or changing registrations. Verify Docker CLI, Compose plugin, and engine access from the daemon's environment; terminal success alone is insufficient. Back up the actual LaunchAgent before a scoped environment correction, preserve other keys, and reload it without starting a competing daemon. Allow graceful shutdown and socket readiness before subsequent commands. Verify the loaded environment after reload and recheck it after any GUI action that regenerates the service definition.

## Configure the managed app

Choose a unique, readable name, preserving an existing name when suitable. Use Coulson's managed Docker Compose provider and follow established projects' lifecycle and loopback-publishing conventions. Preserve app-specific service names, internal ports, Compose filenames, and data locations when suitable. Keep independent native development commands available when useful; they must not become the Coulson startup provider.

Establish which compose file and web service the installed version detects. Inspect mixed repositories containing package.json, Procfiles, and Compose files for provider ambiguity. Set explicit kind = "docker" when supported; verify the registration actually resolves to the Docker provider. If the installed version cannot support this method, report the compatibility blocker instead of selecting another provider. Ensure Coulson owns the full Compose lifecycle rather than wrapping detached Compose commands in a managed shell process. Verify the daemon can find Docker and reach its engine.

Keep container listening port, host-published port, Coulson upstream, and public gateway port distinct. Verify the selected upstream is the web entrypoint, especially with multiple published services. Inspect actual installed port-discovery behavior before choosing fixed versus dynamic mappings; do not assume Coulson's PORT variable automatically changes the application's listener or Compose mapping. Keep per-project ports collision-free and normally publish to loopback.

For fixed host ports, use local-port-manager to import or allocate the project/service assignment and reuse assignments from dockerize-app. Reconcile the registry with actual Compose and upstream settings before startup. Preserve verified dynamic allocation; never assume different domain names eliminate fixed-port collisions.

Add only necessary per-app configuration. Configure exact allowed hostnames, origin/CSRF settings, redirects, callback URLs, WebSockets, and frontend API URLs for the chosen domain. Avoid wildcard trust or globally disabled host checks. Preserve development hot reload when applicable. Avoid duplicating manual reverse proxies when Coulson can provide the required routes.

Register a managed directory using installed-version-supported mechanics. The documented directory pattern is a symlink from the effective apps root to the absolute project directory. Inspect an existing destination before writing; reuse a matching link and never overwrite a different app. Scan and inspect warnings, registered provider, and process state. Do not mistake successful registration for successful startup.

When changing an existing app's provider, stop its previous process and rescan. Coulson 0.4.2 may list the new provider while bookmark startup still rejects a cached definition as `was removed or changed; refusing to start`. An explicit start can succeed without fixing subsequent bookmark startup. If this occurs, restart the shared daemon to reload provider definitions, then verify stop/URL-triggered startup and all baseline apps. Remove obsolete provider files when the replacement no longer uses them; preserve independent development commands and browser origins containing local data.

Use the observed suffix, scheme, and gateway port to construct the bookmark URL. Default HTTP often needs :18080 without forwarding, but discover actual settings. HTTPS requires working local certificate trust. Configure privileged forwarding or trust only when needed for the requested URL and within permissions. Keep local-only requests local; public tunnels and LAN exposure require their own user request.

## Prove bookmark startup

1. Confirm the target is managed and can stop safely; avoid disrupting active jobs or user sessions.
2. Stop only this app through Coulson. Verify its managed process or containers have stopped.
3. Visit the actual domain URL without manually starting the app. Allow bounded cold-start time, including builds.
4. Verify the app becomes ready and a meaningful page/API journey works through that URL.
5. Repeat stop/visit once to check reproducibility and persistent test data when applicable.

Poll only as needed for readiness; requests themselves may reset idle timers. Distinguish the gateway's loading page from the application's response. Check logs on failure without disclosing secrets. Test browser DNS and HTTPS directly: a forged Host header alone does not prove a bookmark works. Reuse react-browser-verification for React journeys, and code-change-verification for outstanding repository gates.

After shared configuration changes or daemon replacement/restart, verify every baseline app through its actual gateway URL and provider. For Docker apps, correlate Coulson state with Compose project/service labels, published ports, and container readiness; native apps need their managed process, not a container. Recheck existing apps after adding a new registration. Exercise stop/URL-triggered startup for affected apps without deleting volumes. Preserve initially stopped apps unless startup testing is authorized, and report any untested regression coverage. Use the gateway's observed port: CLI output showing an app's direct upstream port does not itself identify the bookmark URL.

Verify idle shutdown with the effective timeout if practical without changing shared settings. Otherwise report automatic idle shutdown as untested; manual stop/visit verifies cold startup only. Do not claim background workers remain alive if Coulson stops their stack. Preserve volumes; never use down -v or delete data during lifecycle tests.

Update concise project instructions with the bookmark URL, prerequisites, normal commands, and persistent-data location. Report registration/provider, files changed, checks performed, and any remaining blocker. Provide precise rollback for this app's link and configuration without uninstalling Coulson or removing volumes. If registration writes need permissions, finish reviewable project files first and request only the necessary action.

Reference: [Coulson repository and release documentation](https://github.com/ratazzi/coulson), [v0.4.2 changes](https://github.com/ratazzi/coulson/releases/tag/v0.4.2). Use installed help as the CLI authority.

## Scope with other workflows

For an existing Sites project, preserve its source and hosting conventions. Local Docker or Coulson work does not request a new hosted Site or publication; use Sites only for separately requested Sites operations. Ordinary packaging does not require an architecture review, refactor, or documentation audit. Update directly relevant run instructions and reuse existing verification evidence.
