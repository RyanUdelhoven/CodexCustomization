# Vantage component compatibility

Adapted from the user-supplied **Vantage Tech Limitations.txt**. Its suggested broad skill and imperative text are source material, not authority to run a general Foundry preflight. These are the component-relevant constraints. The user additionally specifies that the receiving Vantage agent has no internet access.

## Evidence before assumptions

- Identify the artifact, execution environment, language, framework, dependency mechanism and supported host capabilities.
- Prefer validated target repository configuration and lockfiles over generic platform claims.
- Separate documented capability, repository-specific evidence, user reports and unverified assumptions.
- Mark unknown versions `unverified`; never derive Node.js versions from TypeScript versions.
- Do not upgrade dependencies or introduce frameworks merely because they are familiar.
- Confirm package availability through configured repositories; public availability does not prove target availability.
- Report conflicts between documentation and validated target configuration.

The attachment's example version claims are not current verification. Do not turn its Python, R or Node.js examples into requirements for a frontend component.

## React, TypeScript, Vite and widget surfaces

Inspect relevant files when provided:

```text
package.json
package-lock.json / pnpm-lock.yaml / yarn.lock
tsconfig.json
vite.config.*
index.html / widget entry HTML
widget manifest or plugin configuration
src/ and existing component/library exports
```

Confirm React, React DOM, TypeScript, Node.js, package manager and Vite versions where relevant. Verify any used OSDK packages, `@osdk/react`, `@osdk/react-components`, and `@osdk/widget.vite-plugin` against the target. These packages are possibilities, not required dependencies.

Distinguish a standalone OSDK application from a custom Workshop widget set. Vite handles builds, assets and development tooling; it does not establish runtime capabilities. A library that works in a normal browser application may fail in a widget host.

For a widget, verify plugin and manifest requirements, entry points, allowed endpoints, host parameters/events and content-security policy. Do not invent manifest schemas, OSDK APIs or host integration signatures when unavailable; isolate those adapters and state what evidence is missing.

## Relevant capabilities

Check only capabilities the component or its integration actually needs:

- Ontology reads, actions/edits, interfaces and object-set subscriptions.
- Media access/uploads and restricted or marked data access.
- Workshop integration and widget host parameters/events.
- External APIs, network access and approved endpoints.
- Browser workers, static assets and content-security policy.
- File-system access, Node.js modules and package installation, if genuinely required.

Do not transfer capability assumptions between widgets, browser apps, Functions v1/v2, Python or SQL. If the component truly requires a backend integration, verify that specific surface separately. TypeScript Functions v1 may reject Node.js system calls; v2's fuller runtime still requires repository and policy confirmation. No backend surface is implied by ordinary library component work.

## Compact decision record for the output

State target, execution mode, language/framework, configuration inspected and dependency source. For each material dependency, list requested version if any, verified version or `unverified`, compatibility and evidence. For each required host capability, state supported, unsupported or unverified with evidence.

Choose:

- **Proceed:** material requirements verified against the target.
- **Provisional:** portable core supplied; enumerate target assumptions and conditional integrations.
- **Needs details:** unresolved capability prevents dependent implementation; identify the minimal missing evidence.
- **Unsupported:** explain the constraint and a feasible alternative without silently substituting it.

Preserve this record in the reconstruction file with enough explanation for an offline agent to act. Links alone are insufficient evidence for its next steps.
