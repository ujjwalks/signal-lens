# Step 7 — Output

A **CSV**, one row per signal, with exactly these columns:

```
signal,what_you_see,where,channel,why_it_matters,who_the_lead_is,strength,false_positive,detection
```

| Column | |
|---|---|
| `signal` | short name |
| `what_you_see` | the observable, in the buyer's words, drawn from `artifacts.vocabulary.buyer_language` |
| `where` | `post` · `comment` · `profile change` · `job listing` · `public record` · `review` · `thread over time` |
| `channel` | the **surface**, not the platform. `r/accounting`, a named newsletter, a county register. "LinkedIn" is not a channel |
| `why_it_matters` | the reasoning, so a human can disagree |
| `who_the_lead_is` | often not the poster. `none` is valid |
| `strength` | `strong` · `medium` · `weak` · `n/a` |
| `false_positive` | the twin from step 4 |
| `detection` | what catching it would take |

**Every type you walked in step 3 gets a row.** One that does not apply still gets a
row with `n/a` in `what_you_see` and the business reason in `why_it_matters`. A row
per *variant*, not per family.

CSV first, then **do not use**, then the phrases. Prose after the CSV, never instead
of rows.

## Check it before anyone sees it

Write the plan to `./signal-lens/<domain>.plan.md` and run:

```
python3 scripts/check_output.py ./signal-lens/<domain>.plan.md
```

Every time, before presenting anything. Non-zero means fix what it names and run
again. If it cannot run here, say so and state that the plan is unverified.
