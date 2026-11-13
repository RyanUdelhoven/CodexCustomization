# Measured audit report

Use exactly two report sections, in this order. An audit title and read-only or
applied status may appear above them.

### 1. Metrics

Use a Metric | Result table. Include:

- Measurement basis: workload, sample size, unit, and whether input includes cached input.
- Current usage and breakdown: show measured totals and major spending categories when available.
- Potential savings: estimate only defensible, non-overlapping savings for that workload.
- Estimated future usage: use the same basis and units as current usage.
- Measured after changes: show comparable results or “Not yet measured.”

State assumptions and material exclusions alongside projections. With session-level
data, subtract projected savings from each session before aggregating. If only
summary medians exist, label their difference a rough projection, not a measured
breakdown. Mark unavailable metrics rather than extrapolating from file sizes or
static walkthroughs. Keep token usage, cost, and quota separate.

### 2. Issues and Solutions

Use an Issue | Impact | Solution table. Order rows by priority, highest first,
without a priority column. Name each issue in a few words. Bold the concrete
impact and distinguish measured effects, estimates, and walkthrough observations.
Cite session evidence or exact file locations in the relevant cell. Give a
specific fix and name any safeguard it must preserve. If no material issues
were found, say so under this section.
