# What must never be a signal

Derived from running the derivation across ten unrelated businesses. Every item below was
named independently in most or all of them.

Public conversation is **more** exposed than first-party data, not less. You are profiling
a stranger from things they said for another purpose, on a platform whose terms you are
subject to, in a community that can see what you do. The regulator is slower than the
community, and the community's punishment lands first.

Run this as a pass over the finished signal list, not as a filter on output.

## Contents

- [The two that end companies](#the-two-that-end-companies)
- [The rest](#the-rest)
- [How to record an exclusion](#how-to-record-an-exclusion)

## The two that end companies

### Never de-anonymise

Named in 10 of 10, usually as the brightest line.

A pseudonymous handle must never be joined to a LinkedIn profile, an employer, a real
name, an email or any contact channel — not by post history, writing style, timezone, a
three-year-old comment, the view out of a window in a photo, or EXIF.

Enforce it **structurally**: pseudonymous and identified identities belong in separate
namespaces the system is *incapable* of joining, not merely forbidden from joining. One
violation produces a front-page callout, permanent community bans, and in the UK/EU
processing with no lawful basis and no notice.

### Exclude distress before scoring, not after

Burnout and crisis posts, suicidal ideation, self-harm, bereavement and probate, financial
distress and insolvency, individual job loss, medical emergencies, active outages and
breaches, anonymous confessions of error, disclosure of unlawful status.

In several markets **these are the highest-intent strings in the entire corpus** — which is
precisely why a naive relevance model ranks them first, and why the exclusion has to run
upstream of scoring rather than as a filter afterwards.

The failure mode is not a wasted email. It is the screenshot that ends the company.

## The rest

**Answer in the channel they chose, in public, with the affiliation on its face.** No DMs
to pseudonymous posters, no SMS to a number scraped from a post, no email from a commit
log, no off-platform contact. Community rules and platform terms everywhere; TCPA and
state DNC in local services; ABA Model Rule 7.3 in law. The inverse matters too — an
identified professional who wrote "DMs open" has invited contact. Never apply the LinkedIn
playbook to a Reddit handle, or the reverse.

**No undisclosed vendor participation.** Replying as a satisfied peer, seeding a comparison
thread, running a persona account, or having staff recommend without stating the
relationship breaches the FTC Endorsement Guides and every community's rules at once. The
generator should be structurally incapable of producing a reply without disclosure.

**Never target on protected or inferred sensitive characteristics, even when volunteered.**
Health and inferred health status, disability, pregnancy or parental leave, mental-health
disclosure, age, bereavement, immigration status, national origin, religion, union
activity. **The pain is why they posted; it is not a field.** Hard exclusion at the
classifier, before scoring. Note the exposure is not limited to HIPAA-covered entities —
Washington's My Health My Data Act carries a private right of action, and the FTC's
BetterHelp order reached public conduct.

**Never pivot from the poster to a third party they exposed.** The employer they complained
about, the client in their screenshot, the elderly parent behind the caregiver, the
employee behind a benefits post, the candidate behind an open-to-work badge.

> Test: if the outreach only makes sense by revealing where the information came from, it
> must not be sent.

You may use a disclosure to *select* an account. You may never quote it, paraphrase it
closely, attribute it, or time outreach so the source is identifiable. Getting a stranger
fired for a post they wrote seeking help is the most reliably reputation-ending outcome
this product can produce.

**"Publicly joinable" is not "public".** Nothing behind a login, a membership or a
platform's terms: Slack and Discord communities, private subreddits, Nextdoor, private
neighbourhood groups, paid peer networks, alumni groups, internal wikis that happen to be
indexed. In referral-driven industries, being caught mining a private community ends the
acquisition channel outright.

## How to record an exclusion

Put it in a **do not use** section with the signal it would have been and the reason.

Do not write the word *permitted*. If nothing matched, write that nothing matched — that
is the absence of a finding, not clearance, and the difference matters when someone later
asks what was checked.
