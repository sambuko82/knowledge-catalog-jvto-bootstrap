# Source-Evidence Report

**Date:** 2026-06-25. One row per material claim slated for (or excluded from) publication. Columns:
source repo/file or URL · affected family · evidence class · publication safety · confidence ·
live-verified? · recommended action. Classes per `workspace/CLAUDE.md`.

Live verification this run: ✅ reachable+confirmed · ⛔ bot-blocked (403, needs `/browse`) ·
❌ not found (404) · ⏳ browser-verifiable, not done this run.

## A. Authority / first-party evidence (publishable)

| # | Claim | Source | Family | Class | Safety | Conf | Live | Action |
|---|---|---|---|---|---|---|---|---|
| E1 | Medical-screening doctor SIP valid 2025-12-11→2031-01-13, practises RS Bhayangkara Bondowoso | satusehat.kemkes.go.id/…/QN00001073380217 | Credential | `official_first_party` | public | high | ✅ | `recommend_new_concept` (Credential, status **verified**) |
| E2 | Business registration NIB/TDUP 1102230032918 | homepage + OSS/TDUP issuer | Credential | `official_first_party` | public | med | ⏳ (homepage✅, OSS portal⏳) | `recommend_new_concept` (Credential, **reviewed**) |
| E3 | Legal entity decree AHU-0023020.AH.01.02.TAHUN 2023 | homepage + AHU portal | Credential | `official_first_party` | public | med | ⏳ | `recommend_new_concept` (Credential, **reviewed**) |
| E4 | HPWKI association membership AHU-0001072.AH.01.07.TAHUN 2024 | homepage (live shows ID) + AHU | Partner | `official_first_party` | public | med | ✅(homepage) | `recommend_new_partner` (**reviewed**) |
| E5 | BBKSDA Jatim is the governing conservation authority for Ijen (ticketing, guide oversight) | bbksdajatim.org / tiket.bbksdajatim.org | Partner | `independent_public` | public | high | ⏳ | `recommend_new_partner` (**reviewed**) |
| E6 | ISIC discount-provider relationship (provider 259268) | isic.org + homepage | Partner | `independent_public` | public | med | ⏳ | `recommend_new_partner` (**reviewed**) |
| E7 | Founder is a serving Tourist Police officer (police-led) | homepage; corroborated by E1 (police hospital) | Trust Claim | `primary_public` (+`independent_public` corroboration) | public | med | ✅(homepage) | `recommend_new_concept` (Trust Claim, **reviewed**, "presents itself as" wording) |

## B. First-party marketing facts (publishable as `reviewed`, qualitative)

| # | Claim | Source | Family | Class | Safety | Conf | Live | Action |
|---|---|---|---|---|---|---|---|---|
| E8 | Private-tours-only model (dedicated vehicle/driver/guide) | homepage | Trust Claim | `primary_public` | public | med | ✅ | `recommend_new_concept` (**reviewed**) |
| E9 | All-inclusive pricing (no hidden costs) | homepage `/policy/...` | Trust Claim | `primary_public` | public | med | ✅ | `recommend_new_concept` (**reviewed**) |
| E10 | Kawah Ijen — pre-dawn blue-fire hike, sulfur crater | homepage + BBKSDA | Destination | `primary_public` | public | med | ✅ | `recommend_new_concept` (**reviewed**, elevation qualified — see C-03) |
| E11 | Mount Bromo — sunrise via 4WD jeep, national park | homepage + park authority | Destination | `primary_public` | public | med | ✅ | `recommend_new_concept` (**reviewed**) |
| E12 | Tumpak Sewu — multi-tier curtain waterfall, guided canyon descent | homepage + itinerary-core | Destination | `primary_public` | public | med | ✅ | `recommend_new_concept` (**reviewed**) |
| E13 | Madakaripura — canyon waterfall, "tallest on Java" | homepage | Destination | `primary_public` (claim) | public | low-med | ✅ | `recommend_new_concept` (**reviewed**, "described as among the tallest" wording) |
| E14 | Cancellation → 48 h cutoff, lifetime Travel Credit (not cash) | homepage `/policy/booking-payment-cancellation` | Policy | `primary_public` | public | med | ✅ | `recommend_new_concept` (**reviewed**) |
| E15 | Ijen health screening required where park rules require it | homepage `/travel-guide/ijen-health-screening` + BBKSDA | Policy | `primary_public` | public | med | ✅ | `recommend_new_concept` (**qualified** — conditional wording per skill item 6) |

## C. Centralizable references (publishable as Reference)

| # | Source | Family | Class | Live | Action |
|---|---|---|---|---|---|
| E16 | Official website (canonical first-party base) | Reference | `primary_public` | ✅ | `recommend_new_reference` |
| E17 | Satusehat practitioner registry record | Reference | `official_first_party` | ✅ | `recommend_new_reference` (**verified**) |
| E18 | Google Maps business listing (CID 1266403973589689021) — listing pointer only, **no count asserted** | Reference | `primary_public` | ⏳ | `recommend_new_reference` (**reviewed**) |

## D. Evidence DEFERRED / excluded (not published this run)

| # | Claim | Source | Class | Why excluded | Action |
|---|---|---|---|---|---|
| E19 | Review counts/ratings (Trustpilot 51, Google 92↔123, TripAdvisor 21) | homepage / wiki / platforms | `conflicting`+`stale` | C-01: surfaces disagree; platforms bot-blocked (⛔) | `do_not_publish` now; `recommend_source_refresh` + `/browse` reconcile |
| E20 | Tour Package concepts | llm-wiki / core | `conflicting` | C-02: canonical count 16/15/7–8 unresolved | `do_not_publish` now; `recommend_evidence_research` (Phase 4) |
| E21 | Press coverage (Detik 2021, Radar Jember ×2, BBKSDA report) | news URLs | `independent_public` but `insufficient` link | Detik guessed URL 404; exact canonical URLs not on file | `recommend_evidence_research` (capture exact URLs, then Reference) |
| E22 | INDECON membership; Ditpamobvit as "partner" | homepage | `supporting_context` | weaker/role-ambiguous public relationship evidence | `report_only` / defer to candidate draft |
| E23 | Facebook 98%/41 reviews | facebook.com/javavolcanotours | `independent_public` | freshness-sensitive, count drifts | `recommend_new_concept` later (Review Platform), timestamped |
| E24 | Entrance-fee figures (Bromo 255k; Ijen 100/150k) | itinerary-core (PP 36/2024, BBKSDA) | `official_first_party` | publishable but dynamic; keep out of v1 to avoid stale pricing | `report_only`; if used, timestamp + cite regulation |
| E25 | Internal cost/rate/crew data | itinerary-core `10-cost-components.json`, llm-wiki `raw/FINANCE/` | `internal_only` | rates/margins/crew pay | `do_not_publish` (hard boundary) |

## Evidence-strength summary
- **Strongest, unused:** E1/E17 (live govt registry), E2–E4 (govt-issued IDs) — these turn the bundle's
  trust layer from self-published to authority-backed. Publish first.
- **Safe but qualitative:** E7–E15 — homepage-backed; publish as `reviewed`/`qualified` with the exact
  hedged wording already used in `organization.md` ("presents itself as").
- **Must wait:** E19 (reviews) and E20 (tours) — the two `conflicting` families. Publishing either now
  would import a known inconsistency into the public bundle.
