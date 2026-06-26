# JVTO OKF Working Contract

## Publication Boundary
This repository is the only public OKF publication target.
Do not create public OKF concepts in llm-wiki, jvto-itinerary-core,
workspace folders, or generated website-output folders.

Edit public concept sources only through:
- `okf/jvto/curation/approved/*.yaml`

Generate bundle Markdown only through:
- `python okf/jvto/scripts/build_bundle.py --curated --indexes`

## Status Rules
- `reviewed`: public evidence has been checked; wording remains bounded.
- `qualified`: public release allowed only with a visible limitation.
- `verified`: each material claim has direct authoritative evidence.
- Never upgrade status because a claim exists in llm-wiki alone.

(Release-eligible statuses are `reviewed`, `qualified`, `verified`, `published`.
`last_verified` is the actual date a source was checked — required on `qualified`
and `verified` concepts, not a static placeholder.)

## Partner Claim Boundaries
- INDECON: public network listing only.
- HPWKI: public partner or membership context only.
- Dr. Ahmad Irwandanu: Ijen screening coordination only.
- ISIC: provider listing only after direct provider evidence is available.

## Reference Claim Boundaries
- Booking.com 2015: historical award artifact only.
- Stefan Loose: historical guidebook reference only.
- Detik and Radar Jember: historical press evidence only.
- BBKSDA training: HPWKI training context only.
- AHU source: HPWKI legal-association registration only.

## Required Sections
Every Partner or Reference concept must contain:

    # Claim Boundary

State exactly what the evidence supports and what it does not support.

## Link Rules
- Use bundle-relative links with `.md` (e.g. `[Kawah Ijen](/destinations/kawah-ijen.md)`).
- Use full HTTPS URLs in Citations.
- Do not use Obsidian wikilinks in public concepts.

## Website Role
- Authority runs one way: source knowledge + original evidence → the canonical OKF graph → the website.
- The JVTO website (`javavolcano-touroperator.com`) is a **secondary** presentation and corroboration layer. It may appear as supplementary context, but it is **never the sole evidence** for a claim — a concept that cites the website must also carry a `source_refs` anchor or a non-secondary external reference URL (enforced by `validate_okf.py` JVTO-18). The validator only distinguishes secondary vs non-secondary URLs; authority, relevance, and freshness are confirmed by a separate source-health review.
- A website gap (absent, outdated, or contradictory) is **never** a reason to delete or downgrade a fact supported upstream. Record it as a **publication propagation recommendation** in the loop report instead.

## Required Validation
Before commit:

```bash
cd okf/jvto
python -m unittest discover -s tests
python scripts/build_bundle.py --curated --indexes
python scripts/validate_okf.py --strict-links
python scripts/validate_okf.py --release --strict-links
```

Live URL checks are a separate source-health process. CAPTCHA, bot protection, or
temporary external failure must create a warning record, not automatically invalidate
a concept.
