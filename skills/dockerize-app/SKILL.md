---
name: dockerize-app
description: Containerize an existing web application with Docker and Compose for reliable local browser use. Use for adding or repairing container packaging; use coulson-ready for Coulson registration and URL lifecycle verification.
---

# Dockerize an application

Produce working local container packaging for the application's actual stack. Support any suitable web stack; do not assume React or Node. Preserve existing Docker conventions and user-selected development or built-app behavior. Default bookmark-driven personal use to a built app when appropriate; preserve hot reload when requested or already central to the workflow.

Ordinary application corrections preserve working packaging. Rebuild the existing service when needed to deliver the change; do not repeat packaging discovery, port allocation, or persistence tests unless their inputs change.

## Inspect and implement

Identify entrypoints, lockfiles, runtime versions, build output, frontend/backend boundaries, required services, environment variables, migrations, writable paths, and existing container files. Desktop-only applications require a web interface before this workflow applies. Avoid rewriting app architecture to force containerization.

Check Docker CLI, Compose, daemon availability, and host architecture. On Apple Silicon prefer supported native images; use emulation only for demonstrated compatibility needs. Missing Docker tooling does not prevent preparing files; distinguish preparation from execution.

Create or minimally amend Dockerfile, .dockerignore, Compose configuration, and concise run instructions. Prefer a Coulson-recognizable compose.yml when creating new packaging for that workflow; preserve an existing filename unless compatibility requires a scoped change.

For requested Coulson integration, hand the existing Compose packaging and port assignments to coulson-ready; that skill owns provider selection and bookmark startup.

Use compatible maintained base images, lockfile-based installs, cache-friendly dependency layers, and multi-stage builds when they reduce runtime contents. Run as a non-root user where the stack permits, use signal-correct startup commands, and provide writable-path ownership. Never copy host node_modules or virtual environments into the image. Exclude credentials, local environment files, VCS data, and irrelevant artifacts without excluding required build inputs. Pass build credentials through supported secret mounts, not image layers.

Keep runtime secrets outside committed files and images; provide variable names and safe example values. Distinguish build-time frontend variables from runtime configuration. A browser cannot resolve Compose service names: use browser-accessible API URLs or same-origin routing; service names are for container-to-container traffic.

Bind the server to 0.0.0.0 inside its container. Publish only required entrypoints, normally on host loopback for local use. Keep databases internal unless host access is needed. Avoid fixed container names and global resources that collide across projects. Add readiness checks with tools actually present in the image; dependency ordering alone does not prove readiness.

Use local-port-manager for fixed host-port assignments: import existing mappings, reuse or allocate a registry assignment, then apply it to Compose. Preserve verified dynamic mappings. Pass the assignment to coulson-ready instead of allocating again. The registry coordinates stopped projects but does not reserve sockets.

Store databases, uploads, and other durable state in named volumes or deliberate bind mounts. Do not migrate existing user data silently or use destructive reset commands. Scope startup migrations to safe, repeatable operations. Avoid restart policies that undermine a requested on-demand lifecycle.

## Verify and hand off

Validate Compose without exposing interpolated secrets in output. Build and start the scoped project, inspect health/logs, and request an actual app route. Exercise one meaningful browser journey when available, including an API interaction for split applications. Check persistence across a normal stop/start using authorized test data. Clean up only resources created for verification; never delete volumes as routine cleanup.

Use code-change-verification for applicable repository gates and reuse results. For React journeys, use react-browser-verification; other stacks use their existing runner. Do not add unrelated tests, CI, registry publication, or deployment.

Report changed files, startup/shutdown commands, entrypoint/service, container and published ports, configuration needs, persistent storage, and checks actually run. If Coulson setup is requested, continue with coulson-ready using this evidence. Containerization alone does not register an app or establish bookmark-triggered startup.

Consult current official guidance for uncertain version-specific behavior:
- [Docker build guidance](https://docs.docker.com/build/building/best-practices/)
- [Compose readiness](https://docs.docker.com/compose/how-tos/startup-order/)

## Scope with other workflows

For an existing Sites project, preserve its source and hosting conventions. Local Docker or Coulson work does not request a new hosted Site or publication; use Sites only for separately requested Sites operations. Ordinary packaging does not require an architecture review, refactor, or documentation audit. Update directly relevant run instructions and reuse existing verification evidence.
