# Select relevant security boundaries

Use the application's exposure and data flows to select areas. Missing controls become findings only when supported by a concrete security consequence.

| Area | Questions to trace |
| --- | --- |
| Identity and access | Do authentication, recovery, token validation, and session invalidation preserve identity? Are object, role, and tenant permissions enforced server-side, including alternate routes? |
| Input and output | Can untrusted input reach SQL, commands, templates, HTML, deserialization, or filesystem operations? Check context-specific handling and path containment. |
| Network and browser | Can URLs bypass outbound restrictions through redirects or address resolution? Check cookies, CSRF, origins, redirects, and uploads against actual usage. |
| Data and cryptography | Can secrets or sensitive data escape through logs, errors, exports, caches, or artifacts? Check key handling and cryptographic choices against current stack guidance. |
| Business rules | Can replay, races, resource exhaustion, or alternate sequences bypass limits or protected transitions? |
| Build and deployment | Can untrusted contributions execute with privileged tokens? Inspect permissions, dependency provenance, install scripts, container exposure, and configuration precedence. |
| Agent integrations | Can retrieved text control tools or cross data boundaries? Trace tool authorization and untrusted input independently of prompt wording. |

## Evidence sources

Consult relevant sections when a control or version-specific claim needs clarification. These sources guide review; they do not mandate compliance certification or tooling.

- [OWASP secure code review](https://owasp.github.io/DevSecOpsGuideline/2-Process/2-2-Develop/2-2-3-Secure-Code-Review/) supports risk-based review, surrounding-code traces, and manual assessment alongside automation.
- [OWASP ASVS](https://asvs.owasp.org/) supplies verifiable web security requirements. Verify the current applicable release; include version-qualified identifiers when citing requirements.

Sources inspected November 10, 2026. Recheck changing recommendations and advisories rather than treating this date as freshness evidence.
