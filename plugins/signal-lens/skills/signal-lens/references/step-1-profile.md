# Step 1 — Profile the seller

Produce `./signal-lens/<domain>.json`. Everything downstream reads that file and
never the website again.

## How

**You are the CSO, the CMO, and the person who has actually sold this thing.** Work
out how this company makes money, who signs, who feels the pain, and what the buyer
does on a Tuesday instead of buying. Be inventive about where the evidence is — you
know how to read a business.

1. If `./signal-lens/<domain>.json` already exists, validate it, summarise it back in
   three lines and ask what has changed. Do not re-derive.
2. Otherwise read the site and write the profile.
3. Validate it. Fix what the validator names. Put its questions to the user.

## The contract

`scripts/profile_schema.json` defines and documents every field. Write against it.

```
domain, source, fetched_at
seller     { sells, category, motion, industry[], price_band, buyer[] }
artifacts  { workarounds[], competitors{}, severity_noun{}, vocabulary{},
             prohibited_bridge[] }
unresolved [ { field, question, why_it_matters } ]
```

Two things the schema cannot tell you:

- `seller.industry` is the **buyer's** industry, not the seller's. A company selling
  software to accountants is in accounting, not in SaaS.
- Where the site does not say, put it in `unresolved` rather than filling the field.
  That is a finding about the site, not a gap to close with a plausible sentence.

## Validate

```
python3 scripts/validate_profile.py ./signal-lens/<domain>.json
python3 scripts/validate_profile.py ./signal-lens/<domain>.json --questions
```

Non-zero means fix what it names and run again — every signal derived later inherits
the defect, invisibly. Then ask the unresolved questions in your own words, capped at
about four, and write the answers back.

A valid profile with open questions is usable. Continue, and say which parts rest on
an assumption.
