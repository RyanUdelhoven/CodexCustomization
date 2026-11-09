# Session accounting

Use existing accounting tools or structured records before building custom analysis.
Check field meanings and whether counters are cumulative before aggregating them.

Separate available usage categories:

- Input, cached input, output, and reasoning tokens.
- Session totals and individual calls or workflow stages.
- Token consumption, monetary cost, and subscription-limit observations.

Do not double-count cached or reasoning tokens included in other totals.
Report unavailable categories rather than inventing them.
Keep credentials and unrelated private content out of reports.

Identify expensive stages and inspect their surrounding traces for:

- Repeated file reads, broad searches, and oversized tool results.
- Long conversations carried through many calls.
- Repeated planning, review, verification, or handoff loops.
- Failed commands, retries, and rediscovery of previously established facts.
- Unrequested refactors, speculative additions, and unnecessary generated artifacts.

Distinguish necessary work from avoidable repetition.
Repeated input can reflect normal conversation processing rather than deliberate file rereading.

Attribute consumption to particular documents or behaviors only when evidence supports it.
Otherwise label the explanation as a hypothesis.
