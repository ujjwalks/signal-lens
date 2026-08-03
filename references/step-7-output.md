# Step 7 — Output

Output a **CSV**, one row per signal, with exactly these columns:

```
signal,what_you_see,where,channel,why_it_matters,who_the_lead_is,strength,false_positive,detection
```

| Column | |
|---|---|
| `signal` | short name — *accounting job change*, *renewal quote received* |
| `what_you_see` | the observable, in the buyer's own words where it is a post. Draw the words from `artifacts.vocabulary.buyer_language`, never from the seller's register |
| `where` | the form: post · comment · profile change · job listing · public record · review · thread over time |
| `channel` | the **surface**, not the platform. `r/accounting`, a named LinkedIn newsletter, a specific issue tracker, a county permit register, a vendor status page. "LinkedIn" alone is not a channel — it does not tell anyone where to look |
| `why_it_matters` | the reasoning, so a human can disagree — *a new controller inherits a process they did not build and has ninety days to change it* |
| `who_the_lead_is` | often not the poster. `none` is a valid answer |
| `strength` | strong · medium · weak |
| `false_positive` | the doppelgänger from step 4 |
| `detection` | what catching it would take — keyword match, profile compared to earlier state, register poll, date arriving, thread watched |

**Every signal type you walked in step 3 gets a row.** If one does not apply to this
seller, it still gets a row with `n/a` in `what_you_see` and the business reason in
`why_it_matters`. A type that silently vanishes is indistinguishable from one you
forgot, and the person filtering later cannot tell which.

A row per *variant*, not per family: "job change" and "promotion into a new budget"
are two rows, because they are detected differently and mean different things.
Expect several dozen rows for most sellers.

Put the CSV first. Then **do not use**, then the phrases. Prose commentary goes
after the CSV, never instead of rows.

## Quote every cell that contains a comma

Not most of them. Every one.

This is the rule that actually broke. A real 43-row plan passed every check it was
given and **29 of its rows were structurally wrong**: `what_you_see` and `channel`
were quoted, `why_it_matters` and `false_positive` were not, and those two are the
most comma-heavy cells there are. *"budget approved, pain proven, and no appetite for
another big system"* became three fields, and every column after it shifted by two —
so `detection` ended up holding the `strength` value and `false_positive` held the
lead. Nothing in the output looked wrong to a reader.

So: wrap any cell containing a comma, a quote, or a newline in `"`, and double any
internal quote. When in doubt, quote it — quoting a cell that did not need it costs
nothing, and not quoting one that did corrupts every column to its right.

`scripts/check_output.py` counts fields per row now and will refuse the plan. Run it.

## Check it before anyone sees it

Write the drafted plan to a file and run, from the skill directory:

```
python3 scripts/check_output.py <that-file>
```

Do this every time, before presenting anything. Exit 0 means present the plan;
non-zero means fix what it names and run it again.

This step exists because the alternative did not work. The row floor used to be a
sentence asking you to count your own output, and the answer that shipped to a real
user had six signals where step 3 lists about twenty types — compression that felt
like editing at the time. You cannot reliably audit your own enumeration from inside
the same pass that produced it; a row count either is or is not twenty. The script
also catches the failures that recur: a column left empty, a channel naming a
platform rather than a surface, an `n/a` with no reason, wording that reads as legal
clearance. It needs no network and no model.

If it cannot be run in this environment, say so in the reply and state that the plan
is unverified — do not silently skip it.
