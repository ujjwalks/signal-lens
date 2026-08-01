# Disclaimer

> **Scope note.** This document describes the behaviour of the finished tool. The
> report generator and scoring pipeline are **not yet built** — today the repository
> ships a signal catalogue and its validator. The verdict vocabulary and the disclosure
> rules below are the contract those components are being written against, not a
> description of code you can run right now. Nothing here is weakened by that: it is
> stated up front so no one reads a specification as a guarantee.

## This is not legal advice

signal-lens emits assessments about whether a purchase-intent signal can lawfully be
collected in a given jurisdiction. Those assessments are **software output generated
from a static rule table**, not a legal opinion, and they are not a substitute for
advice from a qualified lawyer in the relevant jurisdiction.

The tool deliberately never emits the word *permitted*. Its verdicts are
non-adjudicative risk tiers:

| Verdict | Means |
|---|---|
| `blocked_by_policy` | The rule table matched a prohibition. Do not proceed without counsel. |
| `requires_consent_review` | A lawful basis or consent mechanism is likely required. Review before building. |
| `no_known_restriction_identified` | **The rule table found no match.** This is the absence of a finding, not a clearance. The table is incomplete by construction. |

`no_known_restriction_identified` must never be read as "this is legal." It means only
that nothing in a 2026-vintage rule table fired.

## The rule table goes stale

Every generated report embeds the `as_of` date of the rule table that produced it.
Privacy law moved substantially in the 24 months before this table was written and will
keep moving. If the embedded date is more than a few months old, treat every legal
verdict as unverified.

Data-source facts age faster than the law. Access tiers, free tiers, API availability
and vendor identity change on a scale of months — signal-lens downgrades non-first-party
source tiers automatically once a facet's `sourcing_verified_at` is more than 180 days
old, but that mechanism is a hedge, not a guarantee.

## What the report is and is not

- It is a **prioritised inventory** of candidate signals with their data requirements
  and feasibility. It is not a scoring model, a routing plan, or a campaign.
- **Relevance is not availability.** A signal being valuable does not mean it is
  obtainable, lawful, or worth its collection cost.
- **A signal plan is not a conversion forecast.** Every strength, reliability and
  coverage figure is a prior until backtested against your own closed-won data.
- Numeric facets sourced from vendors who sell the product being measured are marked
  `vendor_published`. Unevidenced facets clamp to a neutral midpoint rather than an
  author-chosen value.

## Your responsibility

You are responsible for what you collect, from whom, on what basis, and how you use it.
Running this tool does not transfer any part of that responsibility to its authors.
Signals marked `restricted` in the catalogue are documented **so they can be excluded**;
the catalogue deliberately ships no implementation path for them.

Provided "as is", without warranty of any kind. See `LICENSE` and `LICENSE-DATA`.
