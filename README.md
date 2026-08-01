# signal-lens

**Point it at a seller's website. Get back the public conversations that mean someone
is about to buy from them — in the buyer's words, not the seller's.**

signal-lens is an [Agent Skill](https://agentskills.io): instructions plus reference
material that an agent loads on demand. It is the derivation engine behind
[findonline.ai](https://findonline.ai).

> **Status: v0.1.** Measured once — see [Measured](#measured). Not yet packaged for install.

## The problem it solves

A seller writes *"automated multi-entity consolidation."*

Their buyer writes *"I paste the trial balance into a master workbook and the mapping tab
broke again."*

**Nothing on the website contains the second sentence**, and the second sentence is what
you have to search for. Every keyword list built from a seller's own marketing copy
searches for words only the seller uses.

## The reframe

Most attempts at this look for **pain**. Pain is the ambient condition of every market —
everyone in r/accounting hates closing the books. Ranking on it surfaces students and
venters first, because they write the most vivid posts, and it orders the market backwards:
the most emotionally intense posts come from the smallest accounts.

What discriminates is **the structural failure of the workaround**. The person who
maintained the spreadsheet leaves. The vendor announces an EOL date. The renewal arrives
with an uplift. The bottle runs out.

So the highest-yield signals are about **the arrangement as an object** — running out, out
of stock, price rose, licence changed, brand died, warranty ended, maintainer left. Those
are dated, checkable, cohort-forming, and safe to act on.

## How it works

1. **Profile the seller**, then derive five artifacts before writing any signal: the
   workaround inventory (artifact-first), the competitor set in three tiers, the countable
   severity noun, the vocabulary split, and the prohibited bridge.
2. **Derive the signals** against the library, extending it wherever this seller has one it
   does not contain.
3. **Three gates** on every signal — a **count** of the right noun, a **clock** extracted
   from the text rather than the crawl, and the poster's **side and role**.
4. **A doppelgänger** for each: the post that looks identical and means the opposite.
5. **Name the lead**, which is often not the poster — and "no lead" is a valid answer.
6. **Prohibitions pass**, then output the three signals to start with.

## What it will not do

- **Join a pseudonymous handle to a real identity.** Not by post history, writing style,
  timezone, or a window in a photo.
- **Score distress.** Crisis, bereavement, insolvency and job loss are excluded *before*
  scoring, not filtered after — in several markets they are the highest-intent strings in
  the corpus, which is exactly why a naive relevance model ranks them first.
- **Pivot to a third party the poster exposed.** The employer they complained about, the
  client in their screenshot. If the outreach only makes sense by revealing where the
  information came from, it must not be sent.
- **Treat "publicly joinable" as "public."** Nothing behind a login, a membership, or a
  platform's terms.

See [references/prohibitions.md](references/prohibitions.md).

## How this was built

The signal library is not a taxonomy someone wrote down. It is what survived running the
derivation across **ten unrelated businesses** — B2B software, agencies, a local trade, DTC
consumables and durables, a law firm, telehealth, education — and keeping only what
recurred.

That process deleted as much as it kept. *"Has the problem"* was cut for ~100% recall and
~1% precision. *Funding rounds* were cut for being maximally contested and lagging the need
by two to three quarters. *Promotion into authority* was cut because internal promotion is
the cheap option — the budget conversation already went the wrong way.

And it surfaced the highest-scoring signal in the set, which no draft contained:
**second-opinion / pre-commitment validation** — someone with one quote in hand asking
strangers to talk them out of it.

## Measured

Paired evaluation via [skill-doctor](https://github.com/ujjwalks/skill-doctor)'s harness
(`examples/eval-signal-lens.json`; claude-sonnet-4-6, 3 runs per prompt):

**Trigger rate — 18/18 positives fired (100%), 0/9 negatives false-fired (0%).**
Including `"our outbound is dead, where are our buyers actually talking?"`, which an earlier
description missed entirely. Decoys included buyer-lens and seo-sxo, which carries both
"signal" and "intent"; it correctly declined `"review my pricing page and tell me if my
customers would buy"`, the live buyer-lens seam.

**Pass rate — +37 and +20 points over baseline** on two prompts (89% vs 52%, 100% vs 80%).

That pass number required fixing the harness twice, and the failures are worth recording:

1. skill-doctor's dry harness disallows `Read` — correctly, so the baseline cannot quietly
   load the installed skill — and injects only `SKILL.md`. A thin router pointing at three
   unreachable files scored **−33** on one prompt. A dry harness structurally cannot
   measure a router.
2. Re-running it with file access restored contaminated the other arm instead: **3 of 4
   baseline agents read the repo and one invoked the Skill tool.** That run is void.
3. The number above comes from flattening the references into the injected body so both
   arms stay blocked. The flattened layout is a *measurement artifact*, not what ships.

**The 53-point swing on the HVAC prompt — −33 with references unreachable, +20 with them
inlined — is the most useful thing the eval produced.** It says the body alone is not
self-sufficient, which for a router is by design, but it means the skill is fragile to any
runtime that fails to load references.

Small-n and dry by design: two prompts, three runs, one grader. One run used the word
"permitted", which the skill explicitly forbids — a real one-in-three violation.

## Install

Not yet packaged. To try it:

```bash
git clone https://github.com/ujjwalks/signal-lens ~/.claude/skills/signal-lens
```

Then, in any session: *"what buying signals should I be watching for
[yoursite.com]?"*

## Repository layout

```
SKILL.md                  the derivation
references/
  translation.md          seller language → buyer language, and its four failure modes
  signal-library.md       the types that recurred across ten businesses
  prohibitions.md         what must never be a signal
data/families/            PARKED — a 92-entry first-party intent catalogue (see below)
evals/                    gold-standard cases and a scorer, from the earlier direction
```

### About the parked catalogue

`data/families/` holds a 92-entry catalogue of first-party purchase-intent signals — the
kind you detect in your own CRM and order tables. It is not used by this skill. It was
built for an earlier direction, and **88 of its 92 rows require a first-party data source**,
which a tool reading public conversations does not have.

It is kept rather than deleted because those signals become relevant as channels are added.
Its 16 prohibition classes fed directly into `references/prohibitions.md`.

## Licence

Code and skill text: **MIT** ([LICENSE](LICENSE)).
Legal and sourcing data under `data/`: **CC0** ([LICENSE-DATA](LICENSE-DATA)).
