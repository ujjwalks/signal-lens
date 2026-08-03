# Disclaimer

> **Scope note.** signal-lens derives which public conversations suggest someone is about
> to buy. It does not collect data, identify anyone, or contact anyone — it produces a list
> for a human to act on. The verdicts and disclosure rules below govern that list.

## This is not legal advice

signal-lens says when a signal should not be collected or acted on. That is **model
output following a written rule set**, not a legal opinion, and not a substitute for
advice from a qualified lawyer in the relevant jurisdiction.

It deliberately never says a signal is *permitted*, *allowed* or *safe*. Its verdicts are
non-adjudicative:

| Verdict | Means |
|---|---|
| flagged as prohibited | A documented prohibition matched. Do not proceed without counsel. |
| flagged for review | A lawful basis or consent mechanism is likely required. Review before building. |
| nothing flagged | **The checks found no match.** This is the absence of a finding, not a clearance. The checks are incomplete by construction. |

"Nothing flagged" must never be read as "this is legal." It means only that nothing in a
2026-vintage rule set fired, applied by a model rather than by a lawyer.

## The prohibitions go stale

The prohibitions in `references/prohibitions.md` were written in 2026. Privacy law moved
substantially in the 24 months before that and will keep moving; platform terms move
faster still. Treat both as a starting point that needs re-checking, not a current
compliance position.

## What the report is and is not

- It is an **inventory** of candidate signals with, for each, what you would see, where,
  and what detecting it would take. It is not a scoring model, a routing plan, or a
  campaign, and it is not filtered by what you can actually build.
- **Relevance is not availability.** A signal being valuable does not mean it is
  obtainable, lawful, or worth its collection cost.
- **A signal plan is not a conversion forecast.** Every strength, reliability and
  coverage figure is a prior until backtested against your own closed-won data.
- Strength ratings are judgements, not measurements. Any figure in a generated plan
  should carry "(assumed)" and the check that would replace it.

## Your responsibility

You are responsible for what you collect, from whom, on what basis, and how you use it.
Running this tool does not transfer any part of that responsibility to its authors.
Prohibited classes are named **so they can be excluded**; no implementation path for them
ships with this skill.

Provided "as is", without warranty of any kind. See `LICENSE` and `LICENSE-DATA`.
