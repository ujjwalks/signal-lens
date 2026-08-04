# Step 1 — Profile the seller

Produces `./signal-lens/<domain>.json`. Everything downstream reads that file and
never the website again, so an error here reaches every signal derived afterwards.
The step therefore ends in a validator rather than a judgement.

## How to think about it

**You are the CSO, the CMO and the person who has actually sold this thing.** Work
out how this company really makes money, who signs, who feels the pain, what the
buyer does on a Tuesday instead of buying, and what that costs them. Be inventive
about where the evidence is — you know how to read a business.

The rest of this file is only the part you would get wrong by default. Four things
the site will not tell you and instinct does not supply, then the contract.

## Order of operations

1. **Look for `./signal-lens/<domain>.json` first.** If it exists, do not re-derive:
   validate it, summarise it back in three lines, and ask what has changed. A profile
   is a claim about a company on a date, and companies reposition — say so if
   `fetched_at` is more than about two quarters old.
2. **Fetch the site.** If it will not render, work from what the user tells you and
   say that is what you did. A profile built from imagined pages is worse than one
   built from a typed paragraph, because it looks sourced.
3. **Derive the five artifacts**, write the JSON, run the validator, ask what it
   could not resolve.

## 1. A homepage is a positioning document, not a source

It is written to be liked, so it hides the price, the workaround and the competitor.
**Do not wait for a link — try the path.** Navigation is often JavaScript, or a
footer that did not render, or a page that exists and is simply not linked.

| Looking for | Try |
|---|---|
| Price, and the severity noun | `/pricing` `/plans` `/rates` `/menu` `/order-online` |
| The workaround in a buyer's words | `/customers` `/case-studies` `/stories` |
| **Who does it by hand today** — usually the best page on the site | `/careers` `/jobs`, and any Greenhouse / Lever / Ashby link |
| What breaks, and how often | `/docs` `/changelog` `/status` `/integrations` |
| Whether the severity noun is *locations* | `/locations` `/stores` |
| Named competitors | `/compare` `/vs` `/alternatives` `/migrate` |
| Everything, in one fetch | `/sitemap.xml` — reach for it early when a homepage is thin |

A job posting beats any marketing page. *"Senior Accountant — multi-entity
consolidation experience required"* names the pain, the count and the budget, in a
document written with no intention of persuading you.

## 2. Where the price hides, and why that is a finding

Most businesses keep price out of the HTML: a PDF rate card or menu, often one per
location · a third-party ordering or booking platform · an image · quote-only · a
marketplace listing. Read the PDF. Follow the platform link.

**And when it is behind a platform, the platform is the answer, not the obstacle.**
If ordering runs through Toast, then Toast is a vendor they pay — `competitors.direct`
— it is a workaround wherever a document is hand-maintained, and it is a broadcast
cohort shock waiting to happen, because a platform fee change strands every business
on it on the same day. *"I could not read the price because it is on Toast"* is a
sentence containing a vendor relationship, a cohort and a renewal date.

Fifteen per-location menu PDFs also tell you the severity noun is *locations*, and
that somebody maintains fifteen files by hand.

## 3. If a phrase could appear on the seller's own website, it is not buyer language

This is the crux of the whole skill and it fails silently — a `buyer_language` list
that paraphrases the seller's marketing produces searches that return the company's
own copy and no buyer at all, and it reads as fine.

The forcing question: **what does someone type before they know this category
exists?** That person is the largest uncontested segment in any market and shares
zero tokens with the site.

Two ways it goes wrong that the test above will not catch:

- **The buyer's ask can invert the seller's promise.** An observability vendor sells
  "keep all your data at full fidelity"; the buyer is asking how to store *less*.
  Searching the seller's language retrieves the happy half of the market.
- **Sometimes there is no gap.** Where the buyer is fluent — *MER*, *blended CAC*,
  *RFE on prong 2* — translate **posture** instead: the sound of someone auditing a
  decision already made. *"Am I being farmed"*, *"is this normal"*, *"talk me out of
  it"*.

## 4. Name the competitors, or say you could not

`competitors.direct` must be **products you could navigate to**. "Generic BI tools"
is a category: there is no changelog to poll, no pricing page to diff, no reviews to
read. A real run filled this field with category nouns and the plan built on it lost
six signals, every one returning `n/a`.

## The contract

Write `./signal-lens/<domain>.json` against `scripts/profile_schema.json`, which
documents every field:

```
domain, source, fetched_at
seller     { sells, category, motion, industry[], price_band, buyer[] }
artifacts  { workarounds[], competitors{}, severity_noun{}, vocabulary{},
             prohibited_bridge[] }
unresolved [ { field, question, why_it_matters } ]
```

| | |
|---|---|
| **A** `workarounds[]` | what they do instead, the **verb** they perform on it weekly, **who maintains it**, what makes it **fail**, and how long it holds first |
| **B** `competitors{}` | named products · the free or manual substitute · **the person they pay** — the firm, the freelancer, the VA. Tier three never appears on a website and is a paid competitor about half the time |
| **C** `severity_noun{}` | the countable noun whose number decides whether a post is worth nothing or five figures |
| **D** `vocabulary{}` | the same complaint in the seller's register and the buyer's |
| **E** `prohibited_bridge[]` | inferences that would reach this buyer through a protected characteristic, a distress disclosure, or an exposed third party. An empty list is an answer; an absent one means nobody asked |

`seller.industry` is the **buyer's** industry, not the seller's — a company selling
software to accountants is in accounting, not SaaS. `seller.motion: dual` means an
individual's complaint is a lead for their employer, which changes step 5.

Every inferred field carries the value, how sure you are, and where you saw it.
Where the site does not say, put it in `unresolved` — that is a finding about the
site, not a gap to fill with a plausible sentence.

## Validate, then ask

```
python3 scripts/validate_profile.py ./signal-lens/<domain>.json
python3 scripts/validate_profile.py ./signal-lens/<domain>.json --questions
```

Non-zero means fix what it names and run again; every signal in step 3 would
otherwise inherit the defect invisibly. Then put the unresolved questions to the
user in your own words, capped at about four, and write the answers back.

**A valid profile with open questions is usable.** Continue to step 2 and say which
parts of the plan rest on an assumption. An assumption you named is a finding; an
assumption you buried is a defect.
