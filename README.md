# signal-lens

**Point it at a company website. Get back the purchase-intent signals that company
should actually monitor — and, for every one of them, how to get it.**

signal-lens is an [Agent Skill](https://agentskills.io): a folder of instructions, a
signal catalogue, and deterministic scripts that an agent loads on demand. It runs on
Claude Code and OpenAI Codex from the same `SKILL.md`.

> **Status: in development.** The catalogue contract and its validator are in place;
> the catalogue, scripts and skill body are being built. **Not yet installable** —
> install instructions land when there is something worth installing. Watch the repo
> or read [PLAN.md](PLAN.md), which is the full evidence-based design.

## Why this exists

Ask a capable model "what buying signals should we track?" and it does well on the part
you notice and badly on the part you don't.

We measured it: 7 realistic prompts across 5 business shapes (B2B SaaS, D2C ecommerce,
local services, regulated D2C health, generic), answered with no skill installed, each
output independently graded. **109 observed failures.** The pattern:

| Measured, unaided | Result |
|---|---|
| Signals named per run | **40.5 average** — recall is not the problem |
| Buying-journey families covered | **8.9 of 15** — and the misses are the same six every time |
| Runs that conflated *relevant* with *obtainable* | **7 of 7** |
| Runs that assigned an identity level to any signal | **0 of 7** |
| Runs that produced a do-not-collect bucket | **0 of 7** |
| Signals carrying the data fields needed to detect them | best case **8 of ~50** |

So the model names plenty of signals. It just doesn't know — or doesn't say — how to
get any of them, who they attach to, or whether you're allowed to collect them.

Worse, it holds the right knowledge and leaves it uncoupled. Three of seven runs
contradicted themselves inside a single answer: one cited the FTC's actions against
health apps and warned that shared-device retargeting is "a real harm, not a
theoretical one" — then recommended cross-device household linkage of
reproductive-health browsing. The closing essay was right and gated nothing.

**signal-lens is an adjacency enforcer.** Its value is a column on every row, not an
essay at the end.

## What a signal looks like here

Every catalogue entry is an *acquisition row*, not a name. A name is free; knowing how
to obtain the thing is not.

| Field group | Contents |
|---|---|
| What it is | id · family · definition · question answered · intent dimensions |
| How to observe it | required raw fields · optional fields · identity level · data class |
| **How to get it** | source class · collection method · **capability ladder** (what you can do today → the upgrade) · minimum data thresholds · access conditions |
| Whether you may | availability · **permission requirement** (kept orthogonal to cost) · terms constraints · legal facets · sensitivity |
| How much to trust it | strength · reliability · coverage · latency · half-life · **evidence with independence flags** |
| What breaks it | false positives · confirmation signals · activation direction |

The catalogue covers all 15 master signal families and the 92 signals the source
taxonomy enumerates. It is **data, not prose** — `scripts/filter_signals.py` filters and
ranks it, so the agent only ever sees the shortlist. The other ~77 entries cost nothing.

## Design commitments

- **Relevance is not availability.** They are separate columns and the report says so.
- **Availability is not permission.** A source being free does not make it lawful.
  `public_cost_free` is named that way so it can never be read as clearance.
- **The legal gate runs before scoring, not after.** A subtractive privacy penalty can
  be outvoted by a large relevance boost; a boolean gate cannot.
- **No verdict says "permitted."** Output is
  `blocked_by_policy` / `requires_consent_review` / `no_known_restriction_identified`,
  and the last one means the rule table found nothing, not that you are clear.
  See [DISCLAIMER.md](DISCLAIMER.md).
- **Prohibited signal classes ship as prohibitions, never as recipes.** A `restricted`
  entry that carries a build path is a **hard validation failure** — you cannot print
  "excluded: inferred health status" by shipping instructions for it.
- **Unevidenced numbers don't get to look measured.** Facets without a cited source
  clamp to the neutral midpoint, and vendor-published evidence is flagged as such —
  much of the public benchmark data comes from vendors selling the thing measured.
- **No vendor names in the catalogue.** They rot in months. Source *classes* are stable;
  concrete vendors live in a dated, explicitly perishable appendix.

## Development

```bash
python3 scripts/validate_catalogue.py          # contract + safety rules
python3 -m unittest discover -s tests -v       # stdlib only, no dependencies
```

The catalogue is JSON rather than YAML on purpose: PyYAML is not in the standard
library, and a skill whose scripts die with `ModuleNotFoundError` on a stranger's
machine is not portable.

## Licence

Code, skill text and references: **MIT** ([LICENSE](LICENSE)).
Legal, permission and sourcing data: **CC0** ([LICENSE-DATA](LICENSE-DATA)) — a stale
2026 rule table should not carry anyone's name into 2028.

## Credit

Signal taxonomy from the *Purchase Intent Signal Discovery and Activation* spec.
Skill design follows *The Art of Writing Skills* — the same field guide behind
[skill-doctor](https://github.com/ujjwalks/skill-doctor) and
[buyer-lens](https://github.com/ujjwalks/buyer-lens).

**Not signal-lens?** If you want to know how buyers would *react* to a page or concept —
personas, panels, objections — use [buyer-lens](https://github.com/ujjwalks/buyer-lens).
signal-lens tells you what to watch for and whether you can collect it.
