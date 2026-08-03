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

## The two scores

Not one score. Detectability and value answer different questions, and a single
number mixing them answers neither — measured: a combined score correlated with the
library's own hand-assigned /10 judgements at Spearman **0.41**, and the
disagreements were structural rather than noisy. Every signal it under-rated
converts well and is hard to specify; the one it over-rated is easy to specify and
converts less.

**DETECTABILITY — can you catch it, with what exists today.**

| Component | Meaning | Weight |
|---|---|---|
| `evidence_density` 0–3 | how many of {`numeric_pattern`, `date_pattern`, `query.near`} the spec **enforces**. A pattern only counts if it can match a digit — naming a noun in `count_of` is free, a working regex is not | ×3 |
| `separability` 0–2 | whether the doppelgänger can be expressed as a rule (2), partly (1), or needs a human (0). Low separability caps precision however good the query is | ×2 |

Out of 13. A required baseline costs 2, because on day one you can read current state
but not movement, and movement is the signal — that penalty disappears once snapshots
exist, which is worth telling the seller rather than hiding. **`none_known` scores
zero, not a low number**: "cannot be detected" and "detected badly" are different
states, and the first is what phase 3 exists to change.

**VALUE — what a catch is worth, whether or not you can catch it.**

| Component | Meaning | Weight |
|---|---|---|
| `stage` 0–4 | how close the observable sits to a decision: problem-unaware · problem-aware · solution-aware · vendor-aware · in-negotiation | ×2 |
| `contestedness` 0–2 | how little competition is already fishing it. **Score it as if the signal were detectable** — "nobody watches this" because nobody *can* is not an opportunity, and scoring it 2 hands the highest value to the rows nobody can act on | ×2 |
| `reach` 0–2 | one entity · a recurring stream · a cohort stranded at once | ×1 |

Out of 14.

`evidence_density` is checked against the spec: claim 3 and the validator looks for
three enforced things and rejects the entry if they are not there. **You cannot
inflate a component without the spec showing it**, which is the point.

### What the two scores are worth knowing about

Measured against the 13 signals whose library type carries an explicit /10:
**detectability rho +0.60, value rho −0.05.**

Detectability has independent corroboration. **Value has none.** That is stated
rather than tuned away, because the library's /10 is not a clean ground truth for
value — it bundles "converts well" with "reliably spottable", which is why it tracks
the detectability axis. The only thing that can validate the value axis is the
seller's own closed-won data, and until that exists the value column is a structured
opinion rather than a measurement.

## What to say to the seller

The ranking is not a forecast. Say plainly that the order comes from four stated
properties with fixed weights, that none of it has been backtested against their own
closed-won data, and what would replace it — their last fifty won deals, labelled with
which signal would have caught them.

Report the undetectable ones as a **shortlist of what to build**, not as failures.
They are the signals where value is high and reach is currently zero, which is exactly
where new tooling pays.
