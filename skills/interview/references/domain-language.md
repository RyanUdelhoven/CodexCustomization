# Domain Language / DDD

Start with real examples of the business activity and who describes it. Ask what each important term means, what makes two instances distinct, how it changes over time, and which business rules must always hold. Identify synonyms, homonyms, and meaningful role-specific distinctions.

Build shared language within bounded contexts, not one forced vocabulary across an organization. Ask whether two names represent the same concept or different responsibilities/lifecycles. A restaurant's order, kitchen preparation ticket, and payment transaction may be related concepts with different rules. Roles alone do not automatically define separate contexts.

Compare confirmed meanings with relevant code symbols, schemas, APIs, and UI text when available. Treat code names as evidence, not authority over domain meaning. Distinguish user-reported meanings from verified code locations. Ask about conflicting mappings rather than silently renaming.

Useful probes: “Can an order exist before payment?” “When staff say completed, what has happened?” “Are these two tickets the same thing or linked things?” Explore identity, relationships, state transitions, ownership, events, and translation boundaries only as needed.

Close with a compact glossary: term, meaning/example, context, known synonyms, code mapping, and unresolved ambiguity where applicable. Include decisive business rules. Mark proposed mappings when code is unavailable. Do not impose DDD architecture, rename symbols, migrate schemas, or create a glossary file without authorization.
