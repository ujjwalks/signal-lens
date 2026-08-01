# signal-lens — implementation plan

**Status:** draft 3 — evidence-based, adversarially reviewed.
**Date:** 2026-08-01
**Repo target:** `github.com/ujjwalks/signal-lens`
**Verdict on draft 2:** both central claims were **refuted** by red team. Two findings
are publication-blocking. Fixes are known and mostly mechanical.

---

## 0. How this plan was built

| Stage | Method | Agents |
|---|---|---|
| Baseline failure study | 7 realistic prompts × 5 business shapes, answered unaided, independently graded | 15 |
| Best-practice research | 6 parallel web sweeps (spec, portability, community, B2B intent, B2C/profiling, privacy law) | 6 |
| Design | 3 independent architectures from distinct angles | 3 |
| Judge panel | 3 judges × distinct lenses (doctrine / domain correctness / shippability) | 3 |
| Red team | 2 adversaries instructed to refute, grounded in files on this machine | 2 |

Chapter 7's step 1 — run it unaided and watch it fail — is **done**, not deferred.
That is also the without-skill arm of the eval.

**Judges split, which is informative:** doctrine → trigger-first (85), domain
correctness → determinism-first (82), shippability → portability-first (78). No
design wins outright, so the plan below grafts.

---

## 1. What the evidence established

### 1.1 The model is not short of signals — it is short of *coupling*

Unaided runs named 58, 50, 43, 38, 32, 22 signals (mean **40.5**) with accurate domain
vocabulary and zero hallucinated clinical or regulatory terms. But **7/7 conflated
relevance with availability**, **0/7 assigned an identity level**, and **0/7 produced a
do-not-collect bucket**.

Three of seven runs contradicted themselves *inside one answer*:

- Fertility cited the Flo/Premom/GoodRx FTC actions, warned shared-device retargeting
  is "a real harm, not a theoretical one" — then put cross-device household linkage of
  reproductive-health browsing in Tier 1.
- Cyber listed careers-page visits as Tier 1 intent and, later, job seekers on the
  careers page as a false positive. Both standing, no discriminator.
- HVAC was meticulous on TCPA and written consent, then twice recommended call
  recording with no two-party-consent disclosure, in a business spanning three counties.

> **This is an adjacency enforcer, not a knowledge transfer.** In 3/7 runs the closing
> essay was *right* and gated nothing, because nothing forced general knowledge to be
> evaluated against each specific row. A per-signal **column** beats an excellent essay.

### 1.2 The blind spot has a shape

| Missing in | Families |
|---|---|
| 5 of 7 | delivery & onboarding prep · own-customer renewal · social/advisor/authority |
| 4 of 7 | personal/household/occasion · business/operational/regulatory · environmental/market/competitive |
| Covered 6 of 7 | product & category evaluation · price & affordability |

**Everything after the sale, and everything off the website** — a web-analytics-shaped
mental model. The furniture run named the mechanism itself, anchoring on "a typical
Shopify + GA4 + Klaviyo setup" and narrowing the space "to what GA4 can emit."

And the missing family repeatedly holds the vertical's most valuable signal: the
house-move trigger (furniture), the accountant/CPA referral channel ("the dominant way
SMB payroll is actually bought"), the post-failed-cycle patient ("the highest-intent
person in the entire database, and the answer never mentions them"),
architecture-review-board scheduling (enterprise security).

---

## 2. Scope: one locked decision overturned

| Decision | Status |
|---|---|
| Name `signal-lens` | Holds |
| Stage 1 only | Holds, **reinforced** — 5/7 unaided runs drifted into RevOps/ABM program design; Stage 2 content would reward the exact drift the skill exists to prevent |
| Catalogue size | **Full catalogue — all 92 signals the source spec enumerates** |

### The catalogue is the full 92, and every entry knows how to get itself

Draft 2 argued for cutting the catalogue because the unaided mean is 40.5 signals. That
reasoning was wrong on the mechanism, and the correction matters:

> **The catalogue is data a script filters. The model never loads it whole, so its size
> costs zero context.** *"There is no context penalty for content that is never
> accessed."* The delta rule governs the **body**; it does not govern a data file.

And the baseline study shows the signal *names* were never the delta anyway. The
unaided runs named 40.5 signals — but at best **8 of ~50 carried any data fields**
(payroll), 6 of 22 (furniture), **0 of 58** (cyber), and 0/7 runs assigned an identity
level to a single signal. Naming a signal is free. **Knowing how to obtain it is not.**

So the catalogue's unit is not a name — it is an **acquisition row**. Every one of the
92 entries carries, at minimum:

| Field group | Contents |
|---|---|
| **What it is** | id · family · definition · primary question answered · intent dimensions updated |
| **How to observe it** | `required_raw_fields` · `optional_supporting_fields` · `identity_level` · `data_class` |
| **How to get it** | `source_class` · `collection_method` · `capability_ladder` (2–3 rungs: what you can do today → the upgrade) · `min_data` thresholds · `access_conditions[]` |
| **Whether you may** | `availability` · `permission_requirement` · `terms_constrained` · legal facets · `sensitivity` |
| **How much to trust it** | `strength` · `reliability` · `coverage` · `latency` · `half_life_days` · `evidence[{claim, source_url, as_of, independence}]` |
| **What breaks it** | `false_positives[]` · `confirmation_signals[]` · `activation_direction` |

The 92 come straight from the source spec §5, which enumerates them family by family:

| Family | n | Family | n |
|---|---:|---|---:|
| 5.1 Problem & need recognition | 5 | 5.9 Delivery & onboarding prep | 4 |
| 5.2 Discovery & search | 6 | 5.10 Usage, ownership, replacement | 6 |
| 5.3 Content & social influence | 7 | 5.11 Recurring purchase & renewal | 5 |
| 5.4 Product & category evaluation | 6 | 5.12 Personal, household, occasion | 8 |
| 5.5 Fit, compatibility, requirements | 6 | 5.13 Business, operational, regulatory | 8 |
| 5.6 Price, affordability, value | 6 | 5.14 Social, group, advisor, authority | 6 |
| 5.7 Commitment & reciprocal commitment | 8 | 5.15 Environmental, market, competitive | 7 |
| 5.8 Transaction & payment readiness | 4 | **Total** | **92** |

**What the baseline study still constrains** — the findings that survive intact:

- **The exclusion list (§7) governs the BODY, not the catalogue.** Vertical prose,
  decay theory, identity-resolution plumbing, activation plays and measurement
  frameworks stay out of SKILL.md regardless of how large the catalogue grows.
- **No vendor names in catalogue entries.** `source_class` is stable; concrete vendors
  rot within months (Koala dead Sept 2025, Clearbit → Breeze, TrustRadius → HG
  Insights, Capterra → G2). Vendors live in a separate dated `sources.json` keyed by
  class, with `sourcing_verified_at` (§8.4).
- **Nothing vertical-specific inside an entry.** No cyber regulatory clock, no HVAC
  serial decoding, no fertility clinical vocabulary — the model already ships that
  better than we would, and shipping it anchors the model to whichever verticals we
  happened to write.
- **The 15-family walk with an explicit N/A test still ships in the body**, because
  0/7 runs covered more than 12 families and the misses were silent.
- **Family 5.12 makes §3.1 sharper, not softer.** With 8 entries covering "healthcare
  journey", "household consumption" and life events, the `restricted.*` prohibition
  reframe is now load-bearing rather than a corner case.

The cost of a full catalogue is **authoring effort and correctness risk** — ~92 entries
× ~35 facets ≈ 3,200 authored values, and scripts can verify *conformance* but never
*correctness*. That is managed by the provenance rules in §8.3: unevidenced numeric
facets clamp to the neutral midpoint rather than taking an author-chosen value, and the
renderer refuses to print an uncited number.

---

## 3. PUBLICATION BLOCKERS (must be fixed before the repo goes public)

### 3.1 The catalogue would structurally require shipping a pregnancy-inference entry

To print `EXCLUDED: b2c.pregnancy_inference — MD MODPA bans this regardless of consent`,
`signals.json` must *contain* an entry with that id, a definition, `required_events`,
`min_data`, and a `capability_ladder` whose rungs are literally build instructions. The
"all 15 families" rule makes family 5.12 (explicitly "health… healthcare journey")
mandatory. A GitHub screenshot of a pregnancy-inference entry with a three-rung build
ladder under `Copyright (c) 2026 ujjwalks` is the Target story with an author attached,
and "the gate blocks it at runtime" does not survive a screenshot.

**Fix — reframe restricted entries from the inference to the prohibition.** Replace
per-signal ids like `b2c.pregnancy_inference` with family-level **class** ids:
`restricted.health_status_inference`, `restricted.life_event_inference`,
`restricted.household_composition_inference`. `validate_catalogue.py` **hard-fails** if
any entry with `sensitivity: restricted` carries a `capability_ladder`,
`required_events`, or `min_data`. The repo then documents what must not be built,
without shipping the recipe.

### 3.2 All three designs deleted the source spec's permission axis

§15 defines an eleven-value **permission** vocabulary — verbatim *"Publicly available —
available from **lawful** public sources"*, plus `Restricted`, `Should not be
collected`, a `scraping prohibited` capability flag, and §6's separate
`Permission requirement` field (none / notice / explicit consent / contractual access /
regulated access). Every design replaced this with a five-to-six value **cost** enum.
A user reads `public_free` as a permission claim. It is not one.

**Fix.** Restore permission as facets **orthogonal to cost**:
`permission_requirement: none|notice|explicit_consent|contractual_access|regulated_access`
and `terms_constrained: bool` + `terms_note`. Rename `public_free` → `public_cost_free`
so the label can never be read as clearance.

### 3.3 Never emit the word `permitted`

All three designs emit three-valued legal conclusions about a named company's specific
facts, rendered per jurisdiction (`prohibited in EEA, UK, US_MD`). That is a legal
conclusion, not a software output — and no design shipped a `DISCLAIMER.md`.

**Fix.** Non-adjudicative risk tiers only: `blocked_by_policy` /
`requires_consent_review` / `no_known_restriction_identified` (worded so it cannot read
as clearance). Ship repo-level `DISCLAIMER.md`, referenced from README, SKILL.md and
every report footer; `validate_report.py` hard-fails if the disclaimer line is absent.
**Dual-license:** MIT for code, **CC0 for the legal and sourcing tables**, so a
consultancy forking a stale 2026 rule table in 2028 does not carry the author's name
with it.

### 3.4 Jurisdiction must never be crawl-derived

A US-incorporated DTC skincare brand on Shopify, `.com`, USD-only, no hreflang,
`/privacy` mentioning CCPA only → the crawler sets `audience_jurisdictions: [US]` at
confidence ~0.8. Not null, so the strictest-default never fires and no clarifying
question is asked. The gate then returns permitted for person-level identification on a
brand that ships to Ireland.

**Fix.** `audience_jurisdictions`, `child_or_mixed_audience`, and
`makes_significant_decisions` become **mandatory user-answered** fields, always asked
regardless of swing score. The crawl supplies only a labelled *suggestion* to confirm
or correct.

---

## 4. The trigger will not fire today — measured, not argued

The red team measured this machine: **77 installed skills, ~29,306 chars of listing
payload**, before signal-lens is added and excluding plugin skills.

| Failure | Evidence |
|---|---|
| The canonical query loses to buyer-lens | "which of our website visitors are ready to buy" → content tokens {website, visitors, ready, buy, figure, out}. buyer-lens shares the two load-bearing ones ({buy, website}) and literally contains "Reviews a website… reports purchase intent". The candidate descriptions share only the function word "which". |
| Free vocabulary was declined | **`visitor`, `instrument`, and `measure` each appear in 0 of 77 installed descriptions.** The designs used "visitor" as a should-NOT-trigger example instead of claiming it. |
| Codex budget blown 3.7× | Codex caps the entire listing at 8,000 chars when context is unknown and shortens descriptions progressively. A zero-usage skill is first in line for eviction. |
| Undeclared competitors | `signal` is already claimed by seo-geo, seo-local, seo-sxo; `intent` by buyer-lens, seo-dataforseo, seo-sxo. **seo-sxo carries both**, and appears in no design's decoy set. |

**Fixes.**
1. Anchor on **compound phrases uncontested on this machine** — "buying signals",
   "intent data", "in-market accounts", "what events should we fire", "what should we
   instrument", "website visitors ready to buy".
2. **Front-load** triggers and the verb-split disambiguator; Codex truncates the tail,
   which is exactly where house style currently puts the escape hatch.
3. **Never assert a catalogue size in the description** — the first catalogue PR makes
   an always-in-context string factually false. Say "a scored catalogue covering all 15
   signal families".
4. Add **seo-sxo, seo-geo, seo-local** to the decoy set alongside buyer-lens.
5. Publish the trigger rate measured on a **fixture HOME preloaded with the real
   77-skill listing**. A clean-install trigger rate is marketing.
6. Document explicit invocation (`$signal-lens` / the plugin command) as a first-class
   route, not a footnote.

### The buyer-lens boundary

Both descriptions need a clause; neither should simply yield. The unaided run on the
colliding prompt fired **neither** skill — it produced a CRO teardown, so the ambiguity
currently resolves to a third, worse attractor.

| | |
|---|---|
| **buyer-lens** | *Simulates* buyers, returns their reaction to an artifact — personas, panel, distributions, objections |
| **signal-lens** | *Enumerates* observable evidence that real buyers are moving, and whether it can lawfully and technically be obtained |

Tie-break, one line in each body: the verb decides —
review/test/validate/"would they buy" → buyer-lens; track/detect/collect/instrument →
signal-lens. **This edits a shipped, measured skill and invalidates its published
numbers until re-run.** Needs its own before/after paired eval against a snapshot.

---

## 5. The eval cannot measure output — build a wet harness

`skill-doctor/scripts/eval.py:44` sets
`DRY_DISALLOW = [Bash, Edit, Write, NotebookEdit, Skill, Task, Read, Glob, Grep, WebFetch, WebSearch]`
so the baseline arm cannot load the installed skill. Consequence: **no script executes,
no site is fetched, no file is written.** Every pass assertion about scripts running is
untestable on the harness the author owns.

**Split the eval and never blend the numbers:**

| Arm | Measures | Mechanism |
|---|---|---|
| **Tier 0 — CI, deterministic** | description ≤1024 conformance; TF-IDF rank-1 trigger rate `--min-rank1 80`; pairwise description-collision **erroring at ≥75% similarity** | zero tokens; catches the buyer-lens collision mechanically |
| **Tier 1 — dry** | trigger + routing **only**, labelled as such in `evals/README.md` | existing skill-doctor harness, with the 77-skill fixture listing |
| **Tier 2 — wet** | pass rate | five fixture sites in `tests/fixtures/sites/` (Shopify DTC, Next.js SPA shell, enterprise SaaS, local/appointment, holding page), served by `python3 -m http.server`, scripts allowed |

The baseline study **is** the without-skill arm — 7 prompts, 109 graded failures — and
the assertions come straight from §7's delta table.

---

## 6. Correctness fixes the judges and red team found

### 6.1 Null must not mean False — this is the highest-severity logic bug

`if signal.requires_plg_motion and not profile.requires_plg_motion` treats an
*unresolved* field as a negative. On a thin capture (Framer SPA, no `/pricing`, no
`/docs`) nearly every profile field is null, ~15 signals are dropped and printed as
"not applicable" — a **positive claim the crawl never established** — and the user
receives a confident full report, which is worse than a degraded one.

**Fix.** Null **passes** applicability and appends to `unknowns[]`. Only a
positively-determined False (the crawler affirmatively found no `/signup`, no cart
route, no review listing) may drop a signal. The printed reason must distinguish
**"not applicable"** from **"unknown"**. Add a hard completeness gate:
`filter_signals.py` exits non-zero rather than ranking a capture too thin to rank.

### 6.2 The crawler misses every physical-retail and considered-purchase surface

No design detects showroom/store locator, appointment booking, delivery-postcode
checker, financing/BNPL script, configurator/room planner, sample request, or trade
program. **Every decisive family in the source spec's own furniture example (§32) is
gated on one of these.** Add them as first-class detections.

### 6.3 SPA handling must not diverge by harness

Browser escalation exists on Claude Code (chrome-devtools, claude-in-chrome) and **not**
on Codex (`shell`, `apply_patch`, `update_plan` only). So JS-rendered marketing sites
give Claude Code a good capture and Codex a thin one — which per §6.1 becomes a
manufactured report.

**Fix.** Before declaring a shell, `crawl_site.py` must extract and JSON-parse
`__NEXT_DATA__`, `__NUXT_DATA__`/`__NUXT__`, `__remixContext`,
`window.__INITIAL_STATE__`, every `application/ld+json` block, and walk `sitemap.xml`
for route inventory. Stdlib-only, deterministic, and it removes browser escalation from
the common path entirely.

### 6.4 Profile enums are too coarse

- `sales_motion` as `self_serve|hybrid|sales_led` collapses §10's **eleven**-value sales
  model. §32's showroom/consultation-led and §33's procurement-led both become
  "sales_led", destroying the distinction that should drive applicability. Draft 2's
  three-value recommendation was **wrong**.
- No `consumable_vs_durable` or `replacement_cycle` (both mandated by §10). Combined
  with a 270-day home-goods replenishment benchmark, this actively invites shipping
  "replenishment due" for a furniture retailer — domain nonsense.

### 6.5 Every scoring formula in every design is arithmetically broken

D1 weights sum to 14.0 (max 70) but normalises by 82.5 — its own worked example (82) is
unreachable. D2 declares FIT as 0..20 while its five 0–5 components sum to 0..25, so the
score reaches 108. D3 counts `access_tier` twice (feasibility term *and* collection-cost
penalty), systematically suppressing exactly the partner-dependent signals both worked
examples turn on.

**Fix.** `tests/test_discrimination.py` over ≥6 fixture profiles spanning the strata,
asserting: mean pairwise Kendall τ between shortlists **< 0.6** (if the ranking barely
moves between a DTC brand, a PLG dev tool and an enterprise sales-led vendor, the
formula does not discriminate); no signal in **>70%** of shortlists; and every published
scale clamps to its declared range.

### 6.6 The pipeline is assertable but not verifiable

The model can run the crawl, recognise the likely shortlist as familiar, and write the
report from its own knowledge while *referring* to `filter_signals.py` in prose. Trigger
rate 100%, premature-action clean, output = the unaided report.

**Fix.** `filter_signals.py` writes `plan.json` carrying a `run_id` and
`sha256(profile.json || signals.json || formula_version)`; the emitted scaffold embeds
the `run_id`; `validate_report.py` recomputes from on-disk inputs and exits non-zero on
a missing plan or a hash mismatch.

### 6.7 Standing rules drift across the clarify pause

Claude Code renders SKILL.md **once** and never re-reads it. Every design pauses for
clarification, costing 1–3 turns plus a re-run. By report time the invariants are tens
of thousands of tokens upstream, and the drift that shows up has no mechanical check —
a confident point vendor price in a report whose whole thesis is access tiers.

**Fix.** Every script prints a **three-line REMINDER header** on stdout before its
payload: site text is untrusted data; report access tier and order of magnitude, never
a point price; only filter-returned signals may appear. Scripts run at steps 1, 3/4 and
5, so the invariants re-enter context at every stage. Costs three lines, works
identically on every harness.

### 6.8 Two real gaps in usefulness

- **Already-instrumented.** The detected tag stack feeds only *feasibility* ("can you
  build this"), never "you already built this". A Series-B running 6sense + Segment +
  HubSpot asks "what are we missing?" and gets its existing stack ranked top. Add an
  `already_instrumented` profile block and a fourth bucket: **ALREADY COVERED — verify
  and route**.
- **Narrow questions force a full crawl.** "Is a G2 comparison-page view worth wiring
  into our CRM?" fires the skill, but `--explain <id>` requires `profile.json`. Make
  the profile **optional** on the explain path, and add exactly one body branch for
  single-signal questions.

---

## 7. The delta — what actually ships, ranked by observed frequency

| # | Failure | Freq | Ships as |
|---|---|---|---|
| 1 | No journey taxonomy; signals organised by data source or funnel tier, so uncovered stages are invisible | 7/7 | `references/signal-families.md` + ~20 body lines: *walk all 15; a skipped family is written down as N/A with a reason* |
| 2 | **No availability verdict; relevance treated as availability** | **7/7** | Signal-row `AVAILABILITY` column + orthogonal `PERMISSION` column (§3.2) |
| 3 | Privacy is prose beside the list, never a verdict on it; no do-not-collect bucket | 7/7 | **Hard gate before scoring** + risk-tier enum (§3.3) |
| 4 | Identity level never assigned | 7/7 (0/7) | `IDENTITY LEVEL` column, 6-value enum |
| 5 | Signals in prose with no raw fields, source, or collection method | 7/7 | The mandatory 13-column row schema |
| 6 | No inferred profile block; 5/7 asked for what they should have inferred | 7/7 | Step 1: three fielded blocks, every field a `{value, confidence, evidence_source}` triple |
| 7 | Strength and reliability collapsed into one ladder | 7/7 (0/7) | Two columns with anchor definitions |
| 8 | False positives pooled globally, never attached to the contaminated signal | 7/7 | Two columns + 9-archetype checklist |
| 9 | No readiness-partitioned backlog; 0/7 used a do-not-use bucket | 7/7 | Five buckets + ALREADY COVERED (§6.8), every signal in exactly one |
| 10 | No structural self-check | 7/7 | `validate_report.py` with hash verification (§6.6) |
| 11 | No site-evidence gate — one run fabricated an entire website | 3/7 had URLs; catastrophic in 1 | `crawl_site.py` + completeness gate (§6.1) |
| 12 | Event taxonomy partial, missing consent-state and identity keys | 7/7 | One contract line + `assets/` template |
| 13 | Freshness applied globally, not per-signal | 7/7 | `FRESHNESS` column, three window types |
| 14 | Neither framing caveat stated | 7/7 · 4/7 | Two verbatim closing lines |
| 15 | Fabricated precision — unsourced percentages | 4/7 | Output-discipline line + uncited-number degradation (§8.3) |

---

## 8. Catalogue design

### 8.1 `signals.json`, not YAML — confirmed blocker

PyYAML is not stdlib; `ModuleNotFoundError` on any clean machine. Found independently
by the local check and all three designs. **Do not** author in YAML and generate JSON —
that re-erects the barrier one layer up (a contributor needs `pip install pyyaml` to
patch one entry) and adds a drift surface.

*Open:* the spec puts data under `assets/`; house doctrine defines `assets/` as "ends up
in the deliverable". Decide deliberately and state the reason in the README.

### 8.2 Facets the baseline lacked

**Routing binaries** (more discriminating than industry boosts, all crawl-derivable):
`requires_plg_motion`, `has_review_site_category`, `dev_audience`/`has_owned_community`.
**Motion:** `purchase_motion` (transactional ecommerce vs considered/local/high-ticket)
— this *replaces* a `journey-b2c.md` reference, whose two halves have near-disjoint
signal sets so one file would be half dead weight every run.
**Quality/timing:** `latency`, `half_life_days`, `coverage`, `entity_resolution`.
**Direction:** `activation_direction` (`engage|suppress|route`) — discount-affinity
segments exist to *withhold* offers.
**Cheapness:** `data_class` — occasion signals need only a calendar table and a declared
date, making them the cheapest backlog items a behavioural vocabulary mis-scores as hard.
**Thresholds:** `min_data` (no predictions below 500 ordering customers / 180 days /
3+ orders) and identity horizon (Safari ITP caps JS-set cookies at 7 days).
**Legal:** permission axis (§3.2), plus a **CIPA/behavioural-telemetry exposure** facet —
800+ CIPA claims in 2025, 3,500+ projected 2026, targeting exactly session replay and
on-site search, which both worked examples run.
**Ladder:** `capability_ladder` (2–3 rungs) not a binary, so the matrix tells a thin-data
company what to do today *and* the upgrade path. Split the cookie rung into
`first_party_cookie_same_origin` (escapes the 7-day cap, 400-day ceiling) vs
`first_party_cookie_cname_delegated` (`itp_capped: true`) — most managed "server-side
first-party" vendors are CNAME-delegated and do **not** escape it.

### 8.3 Provenance is mandatory, because the evidence base is vendor-published

`champion_job_change` gets strength 5 from usergems.com — which sells job-change
tracking. `review_comparison_page_view` gets reliability 4 from Dreamdata — which sells
the attribution product that measured it. Compressing that into an integer destroys the
provenance flag.

**Fix.** `evidence.independence: independent|vendor_published|practitioner_survey|author_estimate`
is **required** on every non-default `strength`, `reliability` or `coverage_range`. Any
facet whose evidence is `author_estimate` or missing **clamps to the neutral midpoint
(3)** rather than an author-chosen value — absence of evidence becomes inert rather than
opinionated. The renderer **refuses to print an uncited number**, degrading it to a
qualitative band while the score still uses the value internally. Publish the
unevidenced-facet percentage in the README next to the determinism claim.

### 8.4 Ageing gracefully

Access tier is as perishable as price: RB2B moved person-level ID out of its free tier
to $79/mo in Jan 2026; Crunchbase eliminated its free API tier in 2025; Koala shut down
Sept 2025; Clearbit → HubSpot Breeze; TrustRadius → HG Insights; Capterra → G2 (Feb 2026).

**No vendor names in the catalogue** — key on source **class**; vendors and prices go in
a dated, explicitly perishable appendix. Every entry carries `sourcing_verified_at` and
`coverage_trend`; `capability_matrix.py` computes `staleness_days` and **downgrades**
every non-first-party tier past 180 days. Also add `source_license` and
`access_conditions[]` (e.g. *SEC EDGAR — public domain · declared User-Agent with
contact email, max 10 req/sec*). **Drop Google News RSS** — no public API and terms
prohibit automated access; use GDELT, which is explicitly redistributable.

Do **not** frame privacy around third-party cookie deprecation: Google reversed the
Chrome phase-out in July 2024 and reconfirmed April 2025.

### 8.5 Industry enum — not NAICS

NAICS has no B2B/B2C delineation, and `b2b_b2c` is the primary routing facet (ZoomInfo
classifies 339,506 companies as "Software"). Use a custom ~15–25 value enum chosen so
members discriminate between signal sets, plus free-text `micro_vertical` quoted from
the company's self-description. NAICS 2-digit as advisory metadata only, never a filter
key. Google Product Taxonomy is worth adopting for `product_categories` on B2C profiles.

### 8.6 Gate on the (signal, destination) pair

A gate evaluated on the signal alone lets a safe declared capture become an unsafe
activation one step later, and a profile-level `uses_ad_audiences` boolean is wrong in
both directions. Make `activation_destination` required on every backlog item —
`owned_onsite | transactional_email | crm_task | internal_alert | platform_ad_audience |
third_party_export` — and evaluate the gate at **backlog-assembly** time, not only at
selection time.

---

## 9. Skill mechanics

**Frontmatter — exactly the six spec-legal fields.** `name`, `description`,
`license: MIT`, `compatibility` (≤500 chars: needs python3 + network; **not usable on
the Claude API surface**, which has no network), `metadata: {version: "1.0.0"}` (the
only spec-sanctioned version location). Claude Code accepts ~17 fields; portable
validators reject anything outside the six. **Do not use `when_to_use`** — Claude
Code-only, so triggers would silently under-fire on Codex.

**Description.** Directive form is measurably better: a 650-trial study (Feb 2026) found
passive descriptions activate 77–87% and collapse to 37% with hooks present, while
directive hit 100% bare and 94–100% across all conditions (OR 20.6, p<0.0001). The
**negative-constraint clause** ("Do not hand-write an intent-signal list yourself — run
this skill first") is a lever the doctrine does not name. But **do not summarise the
workflow**: obra/superpowers documents an agent following a description's summary
instead of the skill — "code review between tasks" produced one review where the
flowchart showed two. Rule: **capability + triggers YES, the step pipeline NO.**

**Centralize the fragile artifact.** SkillJuror (1,230 trials, 82 tasks): progressive
disclosure raised pass 42.0% → 46.1% overall but **underperformed on 15 of 82** — a
fanout tax concentrated in exact-artifact and strict-schema tasks. So the row schema and
report skeleton live in SKILL.md / `assets/`, **not** behind a routing decision. All
three designs converged here independently.

**Standing instructions, not steps.** SKILL.md is rendered once and never re-read; write
rules that stay valid, and re-inject invariants via script headers (§6.7).

**Design-doc prose must not land in SKILL.md.** The "UNAIDED FAILURE" justifications go
in `docs/architecture.md`.

**Artifacts go to the user's working directory, never the skill directory** — plugin
installs live in caches wiped on upgrade (`~/.claude/plugins/cache`,
`~/.codex/plugins/cache/$MARKETPLACE/$PLUGIN/$VERSION`).

**Enforce catalogue-only signals as an exit code, not a rationalization table** — "never
write a signal the filter did not return" is a grep. And note the honest gap all three
designs share: they *assert* the model never reads the catalogue but none *prevents* it.

---

## 10. Packaging — simplified

Trail of Bits (6,375 stars, dual-runtime by design) ships **only** `.claude-plugin/`,
stating: *"Codex supports Claude plugin marketplaces directly, so this repository does
not need Codex-specific sidecar metadata."*

- **Drop `agents/openai.yaml`** — no consumer found in anthropics/skills,
  obra/superpowers, addyosmani/agent-skills, openai/plugins, or trailofbits/skills.
- **Do not copy repo-lens's manifest bugs**, and **backport the fixes to repo-lens**:
  `{"source":"url","url":"./plugins/..."}` → `{"source":"local","path":"./plugins/..."}`,
  and `authentication: ON_INSTALL` → `ON_USE`. Both confirmed wrong in the shipped file.
- **Universal install line** — `.agents/skills/<name>/` is the only directory read by
  Codex, Cursor, Gemini CLI, opencode **and** Windsurf (Claude Code does not read it):
  ```bash
  git clone https://github.com/ujjwalks/signal-lens ~/.agents/skills/signal-lens
  ```
- **Never name harness-specific tools in the body.** Codex exposes three internal tools;
  "use WebFetch" is dead text there. Also unresolved: `$SKILL_DIR` (repo-lens's
  convention, needed to pass `audit.py`'s portability check) is Claude-Code-only, while
  bare relative paths assume cwd. **Resolve in phase A with a test on both harnesses.**
- **README order is prescribed:** badges + one-sentence what + the measured claim →
  per-harness install one-liners → a real report excerpt → trigger phrases → how the
  filter works → honest limits.

---

## 11. Build sequence

| Phase | Work |
|---|---|
| **0 ✅** | Baseline failure study — 109 failures; also the without-skill arm |
| **A ✅** | Public repo live, MIT + CC0 split, `DISCLAIMER.md`. *Still open in A:* `.claude-plugin/` packaging, universal install line, `$SKILL_DIR` resolution test, repo-lens backport |
| **B ✅** | Acquisition-row contract + `validate_catalogue.py`: §3.1 restricted hard-fail (adversarially tested) plus three cross-field coherence rules |
| **C ✅** | **92 buildable entries across all 15 families** + 16 restricted prohibition classes. 4 red-team blockers fixed; **25 serious findings still open** |
| **D** | `filter_signals.py`: gate → score, null-passes-applicability, completeness gate, `plan.json` hashing, REMINDER header |
| **E** | `crawl_site.py`: SPA JSON extraction, retail/considered-purchase surfaces, sitemap walk |
| **F** | `sources.json` — dated class → concrete-source map with `access_conditions[]` |
| **G** | `capability_matrix.py` + `validate_report.py` + `test_discrimination.py` |
| **H** | SKILL.md + `assets/` templates + ≤2 references; `docs/architecture.md` |
| **I** | buyer-lens boundary clause + its own before/after eval |
| **J** | Tier 0 CI → Tier 1 dry (77-skill fixture listing) → Tier 2 wet (5 fixture sites) → README "Measured" |
| **K** | Verify both install paths clean on a fresh machine |

Two long poles now: **C** (92 acquisition rows — parallelisable by family) and
**D + G** (the deterministic core). The catalogue is authored per-family so families
can land incrementally without blocking the scripts.

---

## 12. Decisions

**Settled:**

- **Repo is public from phase A.** The §3 blockers are content constraints, not
  skeleton constraints — nothing sensitive exists until phase C, and the
  `restricted.*` reframe plus `validate_catalogue.py`'s hard-fail land in phase B,
  *before* any family-5.12 entry is written.
- **buyer-lens gets the boundary clause**, with its own before/after paired eval
  against a snapshot, since the edit invalidates its published trigger numbers.
- **Catalogue is the full 92** with a complete acquisition row per entry (§2).

**Still open:**

1. **`data/` vs `assets/`** for the catalogue — spec says `assets/`, house doctrine
   defines `assets/` as "ends up in the deliverable". Pick and justify in the README.
2. **Report centrepiece** — ranked list vs 2–4 named **signal stacks** with trigger
   rule, response SLA and CRM destination. The B2B evidence favours stacks (91% use
   intent data, only 24% report exceptional ROI; CRM-native scoring lifts sales
   adoption 41% → 67%), and the shippability judge rated the related "party-mix repair"
   rule — guaranteeing a week-1 plan for a company without a six-figure budget — the
   single most commercially astute idea in the set.
3. **`$SKILL_DIR` vs relative paths** — genuinely unresolved between the portability
   research and `audit.py`'s portability check. Needs an empirical test on both
   harnesses in phase A.
