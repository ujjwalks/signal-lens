# Step 8 — Specify what has to be detected, and rank

Phase 1 enumerates. This step says, per signal, exactly what must be detected, and
ranks the set. Output is `./signal-lens/<domain>.signals.json`, defined by
`scripts/signals_schema.json`.

Read the CSV first — if it fails `scripts/check_output.py`, fix that, because a ragged
row puts one column's text in another's field and you will specify the wrong thing.

**Nothing is dropped.** A signal with no known detection method keeps its entry with
`method: "none_known"` and a stated reason. A high-value undetectable signal is the
argument for what to build next; deleting it loses the argument.

## Per signal

One entry per CSV row. `surface` must be resolvable — `r/Accounting`,
`g2.com/products/{competitor}/reviews`, a named register — never a bare platform.
`query` terms come from `artifacts.vocabulary.buyer_language` and names from
`artifacts.competitors`, never from the seller's own site.

Most of it is a join: `query.near` is the competitor set, `must_also_have` is the
three gates, `disqualifiers` are the step 4 twins. If a field has nothing to draw on,
that is a gap in the profile — go back rather than inventing one.

## Two scores

Detectability and value answer different questions, so they are reported separately.

**Detectability**, out of 13 — `evidence_density` ×3 + `separability` ×2, minus 2 if
a baseline is required, **zero** if no method exists.

| | |
|---|---|
| `evidence_density` 0–3 | how many of `numeric_pattern`, `date_pattern`, `query.near` the spec **enforces**. A pattern counts only if it can match a digit |
| `separability` 0–2 | whether the twin can be expressed as a rule (2), partly (1), or needs a human (0) |

**Value**, out of 14 — `stage` ×2 + `contestedness` ×2 + `reach` ×1.

| | |
|---|---|
| `stage` 0–4 | problem-unaware · problem-aware · solution-aware · vendor-aware · in-negotiation |
| `contestedness` 0–2 | how little competition already fishes it. Score it **as if the signal were detectable** |
| `reach` 0–2 | one entity · a recurring stream · a cohort stranded at once |

```
python3 scripts/validate_signals.py ./signal-lens/<domain>.signals.json --profile ./signal-lens/<domain>.json
python3 scripts/validate_signals.py ./signal-lens/<domain>.signals.json --ranked
```

## What to tell the seller

The order is not a forecast. Detectability has some corroboration; **value has none**,
and only their own closed-won data can supply it — the last fifty won deals, labelled
with which signal would have caught them.

Report the undetectable ones as a shortlist of what to build, not as failures.
