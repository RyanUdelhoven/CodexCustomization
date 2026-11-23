# Technical Constraints

Inspect manifests, integrations, schemas, deployment configuration, and project instructions relevant to the task. Ask users about requirements and capabilities the repository cannot establish. Separate hard constraints, preferences, measured limits, and unknowns.

Probe data sources and ownership, authentication/roles, compatibility, hosting/local operation, offline needs, volume/latency expectations, retention, migration, and operating responsibility only as relevant. Do not ask nontechnical users to invent a stack or precise throughput target when business examples suffice.

Useful probes: “Which system remains authoritative if these disagree?” “Must this work without a network connection?” “What existing clients must continue working?” Avoid collecting credentials.

Close with constraints, verified evidence, assumptions, and decisive feasibility gaps. Research uncertain external capabilities with the appropriate research workflow; use software-design-review for requested architecture assessment. Do not turn interviewing into dependency selection, purchases, or infrastructure changes.
