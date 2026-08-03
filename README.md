# signal-lens

**Point it at a seller's website. Get back the public conversations that mean someone
is about to buy from them — in the buyer's words, not the seller's.**

signal-lens is an [Agent Skill](https://agentskills.io): instructions plus reference
material that an agent loads on demand. It is the derivation engine behind
[findonline.ai](https://findonline.ai).

> **v1.0.1.** Installable on Claude Code and Codex — see [Install](#install). Measured; see [Measured](#measured) for what those numbers do and do not support.

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
2. **Validate the problem — and refuse if it isn't there.** A signal is someone *already
   doing something* about a problem, so if nobody is doing anything yet there is nothing to
   find and any list would be invented. The first three artifacts are the evidence, so this
   costs a paragraph.
3. **Derive the signals** against the library, extending it wherever this seller has one it
   does not contain.
4. **Three gates** on every signal — a **count** of the right noun, a **clock** extracted
   from the text rather than the crawl, and the poster's **side and role**.
5. **A doppelgänger** for each: the post that looks identical and means the opposite.
6. **Name the lead**, which is often not the poster — and "no lead" is a valid answer.
7. **Prohibitions pass**, then output **every** signal found — grouped and ordered by how detectable each is, never shortlisted. Filtering is a later phase, and it can only choose from what was listed.

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

**Pass rate — +54 and +7 points over baseline** with the full skill (92% vs 38%, 100% vs
93%), and **+56 and +20 on the body alone** (89% vs 33%, 100% vs 80%).

Getting that number required fixing the harness twice, and the failures are worth
recording:

1. skill-doctor's dry harness disallows `Read` — correctly, so the baseline cannot quietly
   load the installed skill — and injects only `SKILL.md`. A thin router pointing at three
   unreachable files scored **−33** on one prompt. A dry harness structurally cannot
   measure a router.
2. Re-running it with file access restored contaminated the other arm instead: **3 of 4
   baseline agents read the repo and one invoked the Skill tool.** That run is void.
3. The numbers above keep both arms blocked, and measure two variants: the body alone, and
   the body with its references inlined into the injection.

**That −33 is why the body now carries an inline floor** — the signal type names, the
translation test, and the two hardest prohibitions. With the floor, the same prompt scores
**+20 on the body alone**, a 53-point move. A router should degrade to *adequate* when its
references are unreachable, not to *worse than nothing*.

**Does it enumerate, or summarise?** A real run against topmate.io produced 6 signals
against ~15 types in the body — prose lets a model compress silently. The output is now a
CSV with a required header, a row for every type walked (including `n/a` rows with the
business reason), and a stated floor: *fewer than twenty means you summarised.*

Measured by running it and counting rows, three times: **39, 42, 36.** Header, `n/a` rows,
false-positive column and do-not-use section present in 3/3.

Worth noting how that was measured. skill-doctor's dry harness scored the same change
**62%**, missing the row floor 3/3 — because it instructs the agent to *"produce the exact
commands or steps you would run — DO NOT execute anything."* It describes a plan, so a row
count cannot exist in it. Output-shape properties need a wet run; the dry harness measures
routing and reasoning, not artifacts.

**What the artifact looks like, measured deterministically.** Three real runs on the same
prompt, checked by `scripts/check_output.py` with no model in the loop: **43, 39, 40 rows**,
CSV header 3/3, contract passed 3/3. That is the claim worth making, because it is the one
that reproduces.

**A caution on the pass-rate numbers below.** The dry harness swings hard at n=3 — an
*unchanged* baseline arm moved 44% → 17% between runs, and the skill arm read 96% → 75% →
67% across three runs of a change that a deterministic before/after showed did not regress
the output at all (37.7 rows before, 40.7 after). Treat the deltas as directional. The
trigger numbers are solid and reproduced four times; the pass percentages are not something
to defend to a decimal.

**Does it survive a question asked sideways?** This is the test that matters, and the
earlier ones were too kind. They asked *"what buying signals should we watch for in public
conversations"* — which names the task. A real user asked *"where can I find buyers"* and
got a competent list-building answer: Sales Navigator filters, PE portfolio pages, job
boards. No conversations, no buyer language, no competitor names. The skill had loaded and
was not followed.

Re-measured on prompts phrased the way people actually ask — *"where can I find buyers"*,
*"who should we target and where do they hang out"*:

| | with skill | baseline |
|---|---:|---:|
| finboard.ai (multi-entity consolidation) | **96%** | 46% |
| Premium standing desk, DTC | **94%** | 44% |

**+50 points on both**, after adding an intake instruction that reframes targeting
questions into what those buyers say in public. Note the baseline is also *steadier* here
(46%/44%) than on the friendly prompts (33–93%), so the sideways phrasing is the better
instrument as well as the harder one.

**Does the refusal fire correctly?** Eight sellers, well-evidenced through purely
hypothetical, with each verdict classified blind to ground truth: **0 false refusals, 0
false proceeds.** No real business was turned away, and no invented problem got a clean
signal list.

Scored against my labels it was 6/8 — and both misses were my rubric, not the skill. I had
labelled two pitches "refuse" because their stated problem was solution-shaped. The skill
instead **decomposed** them: it named the framing as solution-shaped, found an *adjacent*
problem with real evidence (named incumbents, real spend, real workarounds), produced
signals for that, and marked everything specific to the unevidenced mechanism as an
unvalidated hypothesis rather than pipeline. That is a better answer than refusing, and a
binary rubric had no way to score it.

The one outright refusal was the only case with no adjacent evidenced market — and it
stayed useful, naming four things that would change the verdict. It caught 3/3
solution-shaped framings and 2/2 unsourced statistics where one was present. Usefulness
ranged 8–9 across all eight, including the refusal.

Honest limits, and one of them matters more than the deltas:

- Two prompts, three runs, one grader, no variance control. Baseline scored 52%, 33% and
  38% on the *same* prompt across runs, so single-arm deltas carry real noise.

**Do the references earn their place?** A separate head-to-head — body alone vs body plus
references, five prompts, both arms given their content inline and verified to have read
nothing else — says **partly**:

| | body | body + references |
|---|---:|---:|
| Assertions only the references can satisfy | **48%** | **85%** |
| Controls (things the body already carries) | 80% | 87% |

The 7-point control gap against a 37-point reference gap means this is specific content,
not "longer answer wins". But the per-field split was sharper than the headline:
`prohibitions.md` carried it almost alone — *publicly-joinable-is-not-public* and
*never-pivot-to-an-exposed-third-party* both went **0% → 100%**. Meanwhile
`translation.md`'s two signature ideas scored **identically in both arms** (100/100 and
60/60), so it was moved out of the load path to `docs/`.
- The word "permitted" leaked in 2 of 3 runs despite an explicit prohibition. The
  instruction has been rewritten to supply the replacement wording rather than only ban the
  word — **not yet re-measured.**

## Install

**Claude Code**

```text
/plugin marketplace add ujjwalks/signal-lens
/plugin install signal-lens@signal-lens-marketplace
```

**Codex** — it reads Claude plugin marketplaces directly, so there is no separate registry:

```bash
codex plugin marketplace add ujjwalks/signal-lens
codex plugin add signal-lens@signal-lens-marketplace
```

**Cursor · Gemini CLI · opencode · Windsurf** — all read `~/.agents/skills/`:

```bash
git clone https://github.com/ujjwalks/signal-lens ~/.agents/skills/signal-lens
```

**Claude Code without the marketplace:**

```bash
git clone https://github.com/ujjwalks/signal-lens ~/.claude/skills/signal-lens
```

Then just ask: *"what buying signals should I watch for — yoursite.com?"*

> The manifests are schema-checked in CI but the marketplace paths have **not been
> installed end-to-end on a clean machine**. If one fails, the two `git clone` lines
> always work.

## Repository layout

```
SKILL.md                  the derivation — canonical
references/
  signal-library.md       the types that recurred across ten businesses
  prohibitions.md         what must never be a signal — measured as the references' whole value
docs/
  translation-method.md   moved out of the load path after it failed to earn its tokens
plugins/signal-lens/      generated mirror for the marketplaces (40KB, skill only)
data/families/            PARKED — a 92-entry first-party intent catalogue (see below)
evals/                    a scorer and gold cases; the cases are stale, see evals/README.md
```

The root is canonical; `plugins/` is generated by `scripts/sync_plugin.py`, because a
`git clone` install needs `SKILL.md` at the root while a marketplace needs a `skills/`
directory. `tests/test_plugin_mirror.py` fails if the mirror drifts, so a stale mirror
cannot ship quietly — and the mirror deliberately carries **only the skill**, not the
parked catalogue, the evals or the tests.

### About the parked catalogue

`data/families/` holds a 92-entry catalogue of first-party purchase-intent signals — the
kind you detect in your own CRM and order tables. It is not used by this skill. It was
built for an earlier direction, and **88 of its 92 rows require a first-party data source**,
which a tool reading public conversations does not have.

It is kept rather than deleted because those signals become relevant as channels are added.
Its 16 prohibition classes fed directly into `references/prohibitions.md`.

## Development

```bash
python3 -m unittest discover -s tests -v          # 50 tests, stdlib only, no deps
python3 scripts/check_output.py <a-plan-the-skill-produced>
```

`check_output.py` ships with the skill and **step 7 of SKILL.md runs it** before a plan is
presented. That is deliberate: the twenty-row floor used to be a sentence asking the model
to count its own output, and the answer that reached a real user had six signals. A model
can talk itself out of a sentence; it cannot talk itself out of an exit code. Everything
the skill can check by code rather than by judgement is checked by code.

You can also run it by hand. Run the skill, save what it produced, check it.
It verifies the CSV contract, the twenty-row enumeration floor, that every row carries a
false positive and a detection method, that exclusions are present, that no clearance
language crept in, and that the working method did not leak into an answer written for a
seller. Deterministic, no model, no cost.

Every rule in it corresponds to a defect that shipped — and **none was caught by an eval.**
All were found by someone running the skill and reading the output. `tests/fixtures/` keeps
both sides of the worst one: the six-signal prose answer a real user got for topmate.io,
and the 38-row CSV from after the fix.

Of the 46 tests, **20 cover the shipped skill** (output contract, plugin packaging). The
other 26 cover the parked catalogue and its scorer, which are not part of this skill.

To release: `python3 scripts/bump_version.py <semver> && python3 scripts/sync_plugin.py`.
The version has to move or installs will not see the change — the Codex plugin cache is
keyed by it.

## Licence

Code and skill text: **MIT** ([LICENSE](LICENSE)).
Legal and sourcing data under `data/`: **CC0** ([LICENSE-DATA](LICENSE-DATA)).
