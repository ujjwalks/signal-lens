# Evaluation

Three arms, deliberately kept apart, because they fail for different reasons and the
fixes are opposite. Reporting them as one number is how a broken description gets
misdiagnosed as a broken body.

| Arm | Question | Broken by | Cost |
|---|---|---|---|
| **Trigger** | Did the skill load at all? | the description | tokens |
| **Pass** | Given that it loaded, was the approach right? | the skill body and references | tokens |
| **Contract** | Does the parked catalogue satisfy its own rules? | a bad entry or a weakened rule | free |

All three arms run. Contract: `python3 -m unittest discover -s tests` (free). Trigger and
pass: `python3 <skill-doctor>/scripts/eval.py examples/eval-signal-lens.json`.

The pass arm runs **dry** — skill-doctor's harness disallows Bash, Read and WebFetch so the
baseline cannot quietly load the installed skill. So it measures what the agent says it
will do and which references it routes to, **not** the plan produced from a real site
fetch. A wet arm against fixture sites is still missing.

## ⚠️ The cases below are STALE

`cases/*.json` were written when signal-lens filtered a 92-row catalogue of
**first-party** purchase-intent signals. The skill now derives signals for **public
conversations** and emits no catalogue ids at all, so these cases would report failure on
a working skill. Do not run them against v0.1 and believe the number.

They are kept because the durable/consumable inverse pair and the regulated-health privacy
case are good tests of a real property, and they should be rewritten for the new direction
rather than discarded.

The live spec for the current skill is `examples/eval-signal-lens.json`.

## Gold-standard cases (stale — see above)

`cases/*.json` — one per business shape, each built against a real, publicly reachable
company website. A case is not a list of nice-to-have signals; it is a trap for a
specific wrong answer.

The fields that carry the weight:

- **`must_exclude_signals`** — the most valuable part of a case. Anyone can list
  plausible signals for a company. A case earns its place by catching an answer that is
  *confidently wrong*: recommending a replenishment cycle to a furniture retailer,
  product-usage telemetry to a company with no self-serve product, review-site intent in
  a category that has no listing. An exclusion nobody would ever suggest catches nothing.
- **`how_obvious`** on each inclusion — `obvious | earned | hard`. The measured baseline
  is that an unaided model already names ~40 signals per run, so recalling an obvious one
  is not evidence of anything. `hard` signals are the off-website and post-sale families
  that were missed in 4–5 of 7 baseline runs. They are weighted 3× against 1× for
  obvious, and the scorer prints the unweighted number alongside so a flattering
  weighting cannot hide a weak answer.
- **`must_flag_restricted`** — prohibition classes the plan must *surface as excluded*.
  A plan that never mentions them has not done the job, and one that recommends them has
  failed outright.

## Scoring

```bash
python3 evals/score_case.py evals/cases/<case>.json <plan> [--json]
```

`<plan>` is either a JSON file of any shape — signal ids are collected from anywhere in
it — or a plain text/markdown report, in which case ids are extracted by pattern. Prose
is supported because early evaluation is realistically "run the skill, save what it
said", and refusing to score that would mean not scoring at all.

Exit codes: `0` pass · `1` a correctness failure (an excluded signal was recommended) ·
`2` unreadable input, including a plan with no signal ids in it — which means the harness
broke and must never be recorded as 0%.

**Exclusion violations are not deductions.** Recommending replenishment to a durable-goods
retailer is not a slightly lower score than missing a signal; it is a wrong answer a
customer would act on. Recall and correctness are reported separately, and a plan can
score 100% recall and still fail.

## Known limitation

The scorer cannot always distinguish a prohibition being *named as excluded* from one
being *recommended*, because in prose both are just the id appearing in the text. Those
are reported for manual review rather than silently passed. A structured plan format
resolves this and lands with the report generator.

## What is not measured here

Whether the prose reads well, whether the priorities suit a particular company, whether
the capability ladders are affordable. Those are judgement calls, and forcing them into
a number produces a metric that is precise, reproducible, and about the wrong thing.
Read the transcripts.
