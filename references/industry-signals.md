# Industry × signal

Which signal types actually fire in a given market, which are dead there, and what
the local lookalike is. Step 3 reads this for every value in `seller.industry`.

**Why this exists.** The strengths in `signal-library.md` are cross-industry
averages, and an average is the wrong number for any specific seller. "Continuity
break" is the strongest signal there is in accounting and nearly worthless in DTC,
where nobody maintains anything. Applying a library-wide strength to one seller
produces a plan that is confidently mis-ranked.

**These are observed patterns, not measurements.** Nothing here has been backtested
against closed-won data. Treat every claim as a prior to be replaced by the seller's
own numbers, and say so in the output.

**If the industry is not listed**, use [the fallback](#when-the-industry-is-not-here)
at the bottom. Do not force the seller into the nearest row.

## Contents

- [Accounting and finance operations](#accounting-and-finance-operations)
- [Developer tools and infrastructure](#developer-tools-and-infrastructure)
- [DTC and physical goods](#dtc-and-physical-goods)
- [Local services and trades](#local-services-and-trades)
- [Healthcare and clinical](#healthcare-and-clinical)
- [Legal and immigration](#legal-and-immigration)
- [Recruiting and HR](#recruiting-and-hr)
- [Creator economy, coaching and courses](#creator-economy-coaching-and-courses)
- [Logistics and freight](#logistics-and-freight)
- [When the industry is not here](#when-the-industry-is-not-here)

---

## Accounting and finance operations

| | |
|---|---|
| **Severity noun** | legal entities · locations · intercompany pairs · close days · headcount in finance |
| **Surfaces** | r/Accounting, r/QuickBooks, r/bookkeeping, r/CPA, QuickBooks and Xero community boards, state CPA society lists, LinkedIn posts by controllers |
| **Fires hard** | Continuity break (the person who built the workbook leaves) · new person in a buying role (a new controller has ~90 days of mandate) · clock (year-end, audit, filing deadlines are public and dated) · outgrown their setup (entity count crossed a threshold) |
| **Dead here** | Public commitment · funding round as a trigger — finance tooling decisions lag a raise by quarters and the raise itself changes nothing about entity count |
| **Local lookalike** | The **practitioner peer**. r/Accounting is overwhelmingly accountants talking to accountants. Most vivid complaints come from people with no budget authority discussing their employer's tools. Qualify on the severity noun before anything else |

The single highest-yield artifact in this industry is a **job posting**, not a post.
A req for "Senior Accountant — multi-entity consolidation experience required"
names the pain, the count, and the budget in one document the company wrote itself.
Two leads at different times: the hiring manager now, the new hire on their start date.

## Developer tools and infrastructure

| | |
|---|---|
| **Severity noun** | GB/month ingested · services · spans · seats · environments · monthly bill |
| **Surfaces** | GitHub issues on the incumbent, HN threads, r/devops, r/sre, r/selfhosted, vendor status pages, changelog and deprecation notices, Discord/Slack for the incumbent tool |
| **Fires hard** | Vendor death (an EOL notice is dated, public, and strands everyone at once) · broadcast cohort shock (a pricing change on a major vendor is the single most reliable event in this market) · counted failed attempt loop · unhappy with a named incumbent |
| **Dead here** | Asking what it costs — pricing is usually public, so nobody asks · asking for a recommendation is present but low-yield, dominated by opinion |
| **Local lookalike** | **Building it themselves.** Approaching at the build announcement reliably produces a defensive "why would I ever pay for this". Key a timer to the *second* breakage post instead, usually three to nine months later |

The strongest signal in this market is a **bill screenshot**. It carries the count,
the date, and the emotional trigger in one artifact, and it is voluntarily public.

## DTC and physical goods

| | |
|---|---|
| **Severity noun** | units · reorder interval · ad spend · AOV · returns rate |
| **Surfaces** | product subreddits, review sections on the incumbent, Amazon Q&A, Facebook groups for the category, TikTok comment sections, r/BuyItForLife |
| **Fires hard** | Clock (replenishment — the bottle runs out on a schedule) · vendor death (a discontinued SKU or reformulation strands a whole cohort) · broadcast cohort shock (a recall or price rise) · just churned off something |
| **Dead here** | Continuity break — nobody maintains a consumer workaround · hiring for the pain · new person in a buying role. Any B2B-shaped signal is dead in B2C |
| **Local lookalike** | The **enthusiast**, who enjoys the manual process and will never buy the thing that removes it, and the **affiliate**, who looks like an advocate and has a coupon code |

"They changed the formula" and "this has been discontinued" are the two highest-value
strings in this market. Both create a dated cohort of people who were satisfied
customers of something that no longer exists.

## Local services and trades

| | |
|---|---|
| **Severity noun** | trucks · crews · doors · jobs per week · square footage |
| **Surfaces** | r/HVAC, r/Plumbing, r/Contractor, city and county permit registers, Nextdoor, local Facebook groups, Google review responses |
| **Fires hard** | Second opinion (someone has a quote and is asking strangers whether it is fair — the latest-stage signal that exists) · gatekeeper spec · clock (seasonal, warranty expiry, inspection dates) |
| **Dead here** | Anything requiring the buyer to know a software category exists |
| **Local lookalike** | The **tradesperson**, not the homeowner. These subreddits are professionals. A homeowner asking about a quote is the buyer; the twelve people answering are the supply side |

**Public registers are the underused surface.** Permits, licence renewals and
inspection results are dated, structured, name the business, and are nobody's
marketing. They are the cleanest signal source in this industry and almost no seller
watches them.

## Healthcare and clinical

| | |
|---|---|
| **Severity noun** | providers · claims/month · sites · panel size · denial rate |
| **Surfaces** | r/medicine, r/healthIT, specialty society forums, CMS rule comment periods, payer bulletins |
| **Fires hard** | Broadcast cohort shock (a regulatory or payer rule change with a compliance date strands an entire population on a known date) · gatekeeper spec · clock |
| **Dead here** | Most consumer-style signals. And note that **distress posts rank highest on naive relevance here and must be excluded before scoring, not after** — see `prohibitions.md` |
| **Local lookalike** | The **patient**, whose post about a billing problem is not a lead for a revenue-cycle vendor and must not be treated as one |

This is the industry where the prohibitions matter most and where a naive intent
model does the most damage. Run step 6 before you rank anything, not after.

## Legal and immigration

| | |
|---|---|
| **Severity noun** | matters · filings · priority date · headcount on visas |
| **Surfaces** | r/immigration, r/legaladvice, r/Lawyertalk, USCIS processing-time pages, court dockets |
| **Fires hard** | Clock (a priority date or filing deadline is the purest dated signal in any market) · second opinion · gatekeeper requirement |
| **Dead here** | Unaware the category exists — people know lawyers exist |
| **Local lookalike** | The **person in distress**, who is a protected case rather than a lead. Also the fluent buyer: applicants use precise procedural vocabulary, so the vocabulary gap in artifact D is small and you must translate **posture** instead |

## Recruiting and HR

| | |
|---|---|
| **Severity noun** | open reqs · time-to-fill · headcount · locations |
| **Surfaces** | LinkedIn, r/recruiting, r/humanresources, the company's own careers page, job boards |
| **Fires hard** | The req that will not close (a role reposted after 60 days is a public admission of failure, dated and countable) · new person in a buying role · outgrown their setup |
| **Dead here** | Replenishment · vendor death (HR tools rarely die loudly) |
| **Local lookalike** | The **agency recruiter**, who talks exactly like an in-house one and is a competitor, not a buyer |

## Creator economy, coaching and courses

| | |
|---|---|
| **Severity noun** | clients per month · bookings · list size · products sold · hours in calls |
| **Surfaces** | LinkedIn, X, creator Discords, r/Entrepreneur, r/coaching, bio-link pages themselves |
| **Fires hard** | Outgrown their setup (a link-in-bio stack that stopped scaling) · counted failed attempt loop · doing it the hard way ("DM me for pricing" is a public admission of manual sales) · just churned off something |
| **Dead here** | Public registers · gatekeeper spec · compliance clocks |
| **Local lookalike** | The **aspirant** with no customers, who writes the most confident posts about tooling and has no revenue. Qualify on the severity noun ruthlessly |

**The artifact is the profile, not the post.** A bio-link page showing Calendly plus
a payment link plus a separate storefront is a visible, checkable, un-marketed
statement that the workaround is fragmenting. It is worth more than anything the
person writes.

## Logistics and freight

| | |
|---|---|
| **Severity noun** | loads/week · trucks · lanes · pallets · dwell hours |
| **Surfaces** | r/FreightBrokers, r/Truckers, load boards, FMCSA registers, port and rail status notices |
| **Fires hard** | Broadcast cohort shock (a rate change, port disruption or regulatory date) · vendor death · clock |
| **Dead here** | Category-unaware signals — this market is software-saturated |
| **Local lookalike** | The **owner-operator** discussing enterprise tooling they will never buy |

---

## When the industry is not here

Do not force the seller into the nearest row. Derive the four columns yourself, in
this order:

1. **Severity noun** — you already have it, from `artifacts.severity_noun`.
2. **Surfaces** — where would somebody with this problem have gone *before* they knew
   this category existed? That is usually a community organised around the workaround
   or the profession, not around the product.
3. **Which types fire** — walk the step 3 list and ask, for each: *does this market
   have the thing the signal is about?* No maintained workaround means no continuity
   break. No renewal means no clock. No named incumbent means no churn signal.
4. **The local lookalike** — ask who else uses this exact vocabulary and is not a
   buyer. In any professional field the answer is a peer; in any consumer field it is
   an enthusiast or an affiliate.

Then say in the output that the industry was derived rather than looked up, so the
next person knows which parts to distrust.
