# Cross-Repo Consistency Report (corrected against real main `6e1a73c`)

**Date:** 2026-06-25. Compares the **published bundle** ↔ llm-wiki ↔ itinerary-core ↔ **live web**.
Major correction vs the first pass: the bundle already carries the *current* review counts, so the
count problem is a **live-website / raw-SSOT** issue, not a bundle defect.

## C-01 — Review counts: bundle correct, live homepage stale (live-confirmed)

| Surface | Trustpilot | Google Maps | TripAdvisor | As-of |
|---|---|---|---|---|
| **Bundle `reviews/*.md`** | 4.8 / **51** | 4.9 / **123** | 4.95 / **21** | 2026-05-18 / 05-26 |
| `wiki/credentials/trust-signals.md` (canonical) | 4.8 / 51 | 4.9 / 123 | 4.95 / 21 | 2026-05-26 |
| `raw/JVTO_FINAL_CLEAN_SSOT.json` v6.0 | 4.8 / **47** | 4.9 / **92** | 4.95 / 21 | 2026-04-22 (stale) |
| **Live homepage** (fetched 2026-06-25) | 4.8 / 51 | 4.9 / **92** | 4.95 / 21 | 2026-06-25 |

- **The bundle is right** (123/51), matching the operative SSOT. **Classification:** bundle =
  `primary_public` (correct); raw SSOT 47/92 = `stale`; **live homepage Google 92 = `stale`/`conflicting`**.
- **Action:** `recommend_source_refresh` on the **live website** (92→123) — owner action, outside this
  repo. `recommend_validator_change`: JVTO-11 guard so 92/47 can never enter the bundle by a later edit.
- **Human decision:** the website fix is the owner's; the bundle needs no change here.

## C-02 — Package count: resolved in the bundle
Homepage **16**, bundle **16** (12 Surabaya + 4 Bali), llm-wiki SSOT 15, itinerary-core route-map 7–8.
Bundle and homepage agree at 16; the core subset is operational, not a contradiction. **Classification:**
`report_only`. The first pass wrongly flagged this as blocking — retracted.

## C-03 — Kawah Ijen elevation error (the one real bundle defect)
`destinations/kawah-ijen.md` states "(summit roughly **2,386 m**)". Independent authority: the Ijen
complex **summit** is ~2,769 m (Wikipedia) to ~2,799 m (Smithsonian GVP); **2,386 m is the crater-rim**
elevation. So the concept mislabels the rim as the summit. **Classification:** `conflicting` (factual).
**Action:** `recommend_update_existing_concept` — state rim vs summit, or avoid a single asserted figure.
*(Fixed in PR-B.)*

## C-04 — Destination claims under-cited (strengthen-able, not wrong)
- `mount-bromo`: geology supportable by Smithsonian GVP (vn 263310, Tengger Caldera active cone) →
  can reach `verified`.
- `madakaripura`: the **Probolinggo Regency tourism office** states it **is the tallest waterfall in
  Java** (stronger than any hedge) → `verified`.
- `tumpak-sewu`: "multi-tier" is imprecise; independent sources describe a **semicircular curtain**
  (~120 m). `recommend_update_existing_concept`.

## C-05 — Two TripAdvisor listings
Live: `d19983165` (bundle cites this) **and** `d24825561` resolve to the same operator. The bundle
cites d19983165; confirm it is canonical. **Classification:** `conflicting` (duplicate listing).
**Action:** `recommend_evidence_research` (browser-confirm the canonical listing). Low severity.

## C-06 — "BBKSDA clearance" overstated in an existing concept
`trust/credentials/verifiable-licenses.md` lists "conservation-authority (BBKSDA) clearance to operate
at Bromo and Ijen". Independent check: **BBKSDA's public site does not list JVTO**; "clearance" is a
first-party claim. BBKSDA governs Ijen for *all* operators. **Classification:** `supporting_context`
overstated as authority. **Action:** `recommend_update_existing_concept` (soften to "states that it
holds…") — owner-gated; surfaced as a recommendation, plus a correctly-hedged Partner concept that
frames BBKSDA as the **governing authority**.

## C-07 — Authority claims that are NOT publicly verifiable (defer)
- **Satusehat doctor registry** (`QN00001073380217`): a clean independent fetch returns "public
  profile not yet available" (login-gated); name/SIP/expiry are not public, and the figures I first
  "read" were a single-pass fetch fabrication. Publishing them = PII/credential exposure.
- **AHU legal-entity decree** `AHU-0023020.AH.01.02.TAHUN 2023`: not on the public site (the only
  public AHU number is the **HPWKI association** decree — a different credential).
- **Classification:** `unreachable` / `insufficient` + PII. **Action:** `do_not_publish`. The bundle
  already avoids these — correct.

## C-08 — Facebook review surface unmodeled
Live: `facebook.com/javavolcanotours` shows "98% recommend / 41 reviews" — a 4th public surface the
bundle does not model. **Classification:** `independent_public`. **Action:** `recommend_new_concept`
(later, timestamped) — low priority.

## Verdict
The bundle is **consistent and current**. One factual defect (C-03 elevation), a few strengthen-able
destinations (C-04), two genuinely-empty families, and one **live-website** stale count (C-01) that is
not a bundle problem. No `conflicting` family blocks publication; nothing unsafe is in the bundle.
