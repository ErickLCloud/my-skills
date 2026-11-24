# Reference (stable facts) — the durable-facts sink

> Purpose: Durable technical/contextual facts and locked decisions that rarely change. This is
>   the HOME for durable facts — so progress.md can stay ephemeral.
> Update when: a stable fact changes, or a decision locks (rare). Not a log.
> Focus: things expensive to re-derive — environment, key file locations, conventions, specs,
>   locked architecture, pointers to the latest deliverable versions.
> FORMAT (for retrieval): prefer one fact/decision per line with a stable ID + status, so a cold
>   session can GREP instead of reading the whole file, e.g.  `D3 | output dir = OUT/<branch> | LOCKED`.
> BUDGET: ~250 lines, read on demand (not at session start). When it grows past that, SPLIT the cold parts to
>   on-demand/reference-archive.md and leave a one-line pointer here.

-
