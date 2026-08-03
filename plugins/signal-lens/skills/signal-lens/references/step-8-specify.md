# Step 8 — Specify what has to be detected, and rank

Phase 1 (steps 1–7) enumerates. This step takes that list and says, for each signal,
**exactly what must be detected** — which surface, which pattern, which qualifiers,
which disqualifiers, how long it stays live, and what you end up holding.

Output is `./signal-lens/<domain>.signals.json`, validated by
`scripts/validate_signals.py`.

## Two rules that shape everything here

**Nothing is dropped.** Not the vague ones, not the ones with no known detection
method. A signal nobody can currently detect keeps its entry with
`method: "none_known"` and a stated reason. That is not bookkeeping: **a high-ranked
undetectable signal is the argument for what to build next.** Delete it and the
argument goes with it.

**The rank is computed, not written.** You state four components; the script derives
the score. A model writing "strong" in a column is unfalsifiable, and every strength
figure in this repo is a prior until it has been backtested against closed-won data.
Stating components means a reader can disagree with one of them instead of with a
feeling.

## Per signal

Every row of the phase 1 CSV becomes one entry. Read the CSV — if it fails
`scripts/check_output.py`, fix that first, because a ragged row puts one column's text
in another column's field and you will specify the wrong thing.

| Field | What it has to be |
|---|---|
| `surface` | **Resolvable locations, not platforms.** `r/Accounting`, `g2.com/products/{competitor}/reviews`, a named register URL. "LinkedIn" is not a surface — it does not tell anyone where to look, and the validator rejects it |
| `observable` | The thing you actually read: post body, comment, review text, a rating field, a listing field, a profile field, a job posting, a public record, a changelog entry, publication cadence |
| `method` | `keyword` · `regex` · `state_diff` · `date_arrival` · `cohort_enumeration` · `none_known` |
| `query` | The pattern. **Terms come from `artifacts.vocabulary.buyer_language` and names from `artifacts.competitors`** — never from the seller's own website, which is the failure the whole skill exists to prevent |
| `must_also_have` | The three gates from step 3, made checkable: a count of the severity noun, a date extracted from the text, demand-side |
| `disqualifiers` | The step 4 doppelgängers, written as exclusions. Empty means nobody stress-tested it, and precision is unknown rather than high |
| `baseline` | Required for anything comparing against an earlier observation. `state_diff` without a baseline is rejected — *"their rating is 3.9"* is a fact, *"it fell from 4.6"* is the signal |
| `freshness_days` | How long it stays live after the observable appears |
| `yields` | The entity you end up holding, and whether it is contactable. `no` is a real answer |

Most of this is a **join, not new thinking**. `query.near` is the competitor set.
`must_also_have.count_of` is the severity noun. `disqualifiers` are the doppelgängers
you already wrote. If a field has nothing to draw on, that is a gap in the profile
rather than a gap here — go back rather than inventing one.

## The rank components

Four numbers, each with a stated meaning. The script applies fixed weights.

| Component | Meaning | Weight |
|---|---|---|
| `stage` 0–4 | How close the observable sits to a decision: problem-unaware · problem-aware · solution-aware · vendor-aware · in-negotiation | ×3 |
| `evidence_density` 0–3 | How many of {a count of the severity noun, an extractable date, a named incumbent} the query **requires**. Not how many it might happen to contain | ×3 |
| `separability` 0–2 | Whether the doppelgänger can be expressed as a rule (2), partly (1), or needs a human (0). Low separability caps precision however good the query is | ×2 |
| `reach` 0–2 | One entity · a recurring stream · a cohort stranded at once, where one detection enumerates many | ×1 |

`evidence_density` is checked against the spec: claim 3 and the validator will look for
three of them in `must_also_have` and `query.near`. **You cannot inflate a component
without the spec showing it**, which is the point.

## What to say to the seller

The ranking is not a forecast. Say plainly that the order comes from four stated
properties with fixed weights, that none of it has been backtested against their own
closed-won data, and what would replace it — their last fifty won deals, labelled with
which signal would have caught them.

Report the undetectable ones as a **shortlist of what to build**, not as failures.
They are the signals where value is high and reach is currently zero, which is exactly
where new tooling pays.
