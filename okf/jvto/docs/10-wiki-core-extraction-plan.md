# 10 — Wiki + Core → Bootstrap: extraction & integration record (2026-07-07)

This document records the cross-repo extraction pass that reconciled this
repository against its two curation sources (`sambuko82/llm-wiki`,
`sambuko82/jvto-itinerary-core`) and ported their highest-value data and
governance patterns. It extends the extraction contract already defined in
`docs/01-source-to-output-map.md` and `docs/07-source-contract-summary.md`;
nothing here changes the fetch or source-scope allow lists.

## Why this pass happened

A full exploration of all three repos found the bootstrap's 2026-06-23
migration in good shape but exposed one live correctness gap and two
structural gaps:

1. **Health-screening wording drift.** llm-wiki adjudicated Ijen screening
   conditional → **mandatory** on 2026-07-06 (BBKSDA SE.1658/KSA.9/2024 cited
   as supporting authority, not a trigger), but this bundle still published
   the superseded conditional wording. Authority runs upstream → OKF, so the
   graph was contradicting its own source of truth.
2. **Zero direct citations on travel guides.** Every destination and travel
   guide sat at `reviewed` with no fee, ferry, or closure-authority facts —
   while Core's `seed/research/east-java-field-data-2026.json` held exactly
   those facts, confidence-rated, with public source URLs.
3. **Partially machine-enforced claim boundaries.** The root CLAUDE.md
   boundaries (Stefan Loose, Booking.com 2015, Detik, ISIC, BBKSDA) relied on
   manual review; llm-wiki already ships pre-tuned regex rules for all of them
   in `scripts/claim_boundaries.yml`.

## The four extractions (in execution order)

### E1 — Mandatory health-screening propagation *(data, from Wiki)*
Sources: `wiki/destinations/kawah-ijen.md`, `wiki/credentials/medical-screening.md`
(llm-wiki commit `e650fa7`). Updated `trust/claims/medical-screening`,
`policies/ijen-health-screening` (now `qualified`, citing the live-checked
BBKSDA ticket-portal terms), `policies/inclusions-exclusions`,
`destinations/kawah-ijen`, and `people/dr-ahmad-irwandanu` (claim boundary
kept coordination-only). Zero conditional-phrasing grep hits remain.

Note: llm-wiki's *compiled* trust bundle (`claims.json` C4, `policies.json`)
still lags its own 2026-07-06 wiki adjudication. Recorded as a **publication
propagation recommendation** for llm-wiki; per the website-role rule this was
not treated as a reason to hold the upstream-supported fact back.

### E2 — Claim-boundary linter → `JVTO-20` *(pattern, from Wiki)*
Ported `claim_boundaries.yml` + `verify_claims.py` mechanics into an additive,
config-driven rule: `claim_boundaries` + `claim_boundary_context_markers` in
`config/publication-rules.yaml`, scan over whitespace-flattened paragraphs in
`validate_okf.py`. Rules: STEFAN-EDITION, BOOKING-CONTINUITY, DETIK-IJEN,
BBKSDA-CERTIFIED, ISIC-PARTNER, plus a new **MEDICAL-CONDITIONAL** regression
guard that locks E1 in place (mirrors jvto-web's `validate-content-drift.mjs`).
Context markers keep `# Claim Boundary` sections (which legitimately state
what evidence does *not* support) from being flagged.

### E3 — Authority-cited East Java facts *(data, from Core)*
Source: `seed/research/east-java-field-data-2026.json` — **high-confidence
entries only**; concepts cite the underlying public-authority/press URLs
directly (all live-checked 2026-07-07), so Core's `seed/` stays outside the
fetch and source-scope allow lists and its `internal_operational_context_only`
role is untouched. Entrance/ferry figures are public government tariffs (never
JVTO prices), framed with as-of dates and re-verify caveats.

- `destinations/kawah-ijen` → BBKSDA tariff + online-only ticketing → `qualified`
- `destinations/mount-bromo` → PP 36/2024 tariff + mandatory online booking → `qualified`
- `destinations/madakaripura` → flash-flood risk + afternoon-rain scheduling rationale
- `travel-guides/weather-and-closures` → PVMBG/MAGMA alert vs BBKSDA/TNBTS
  closure authority split + 2024 Ijen closure example → `qualified`
- `travel-guides/surabaya-vs-bali-starting-point` → ferry sailing time (WIB/WITA
  artifact), 24h ops, Nyepi stop, Ferizy online-only + geofence, KM 131/2024 fare → `qualified`
- `policies/ijen-health-screening` → in-force-since-January-2024 press evidence

Skipped as below the evidence bar: jeep rates and gear-zone SOP (medium
confidence), Tumpak Sewu incident leads and Kasada closure dates (low /
unverified — research round 3 still open).

### E4 — Freshness SLA → `JVTO-21` *(pattern, from Wiki)*
Ported llm-wiki's F1 rule (`last_verified` vs `stale_after_days`) as a
**warnings-only** check: verified/qualified concepts past their type SLA
(config: `freshness.stale_after_days`) surface in
`build/validation-report.json` as a source-health worklist. Never an error,
never a release blocker — external staleness must not auto-invalidate a
concept. Without it, E3's `qualified` upgrades would silently rot.

## Considered and ruled out

- **Review-count refresh** — this repo's `reviews.yaml` is already fresher
  than llm-wiki's compilations.
- **Trust claims C6–C9** — meta-claims whose substance the bundle already
  covers via `reviews/`, `people/crew/`, `trust/partners/`, `references/`.
- **Core datasets 16–27** — static fixtures with no builder/validation path.
- **`itinerary-builder/`, cost components, expense maps** — private markup and
  vendor rates; excluded by the security boundary.
- **Backoffice raw snapshots** — PII-adjacent; `raw/` is deny-listed.

## Verification

Per the required-validation contract, after every extraction:

```bash
cd okf/jvto
python -m unittest discover -s tests                     # 65 tests
python scripts/build_bundle.py --curated --indexes       # byte-stable bundle
python scripts/validate_okf.py --strict-links            # 0 errors
python scripts/validate_okf.py --release --strict-links  # 0 errors
```

Measured outcomes: 5 concepts upgraded `reviewed` → `qualified` with real
`last_verified` dates; travel-guide direct HTTPS citations 0 → 6; the gate
grew 19 → 21 rules (JVTO-20 blocking, JVTO-21 warning-only) with 6 new tests;
zero conditional-screening phrasings remain in curation or the bundle.
