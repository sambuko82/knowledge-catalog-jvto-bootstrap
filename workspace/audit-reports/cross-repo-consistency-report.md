# Cross-Repo Consistency Report

**Date:** 2026-06-25. Compares llm-wiki ↔ jvto-itinerary-core ↔ bootstrap bundle ↔ **live web**.
Each row: the conflict, the values per surface, classification, and recommended action. No public
concept changed.

## C-01 — Review counts disagree across four surfaces (HIGHEST RISK)

| Surface | Trustpilot | Google Maps | TripAdvisor | As-of |
|---|---|---|---|---|
| `raw/JVTO_FINAL_CLEAN_SSOT.json` v6.0 | 4.8 / **47** | 4.9 / **92** | 4.95 / 21 | 2026-04-22 |
| `wiki/credentials/trust-signals.md` (canonical) | 4.8 / **51** | 4.9 / **123** | 4.95 / 21 | 2026-05-26 |
| **Live homepage** (fetched 2026-06-25) | 4.8 / **51** | 4.9 / **92** | 4.95 / 21 | 2026-06-25 |
| Trustpilot search snippet | "4★ / 34" (subset) | — | — | 2026-06-25 |

- **Classification:** `conflicting` + `stale`. The raw SSOT (47/92) is self-declared stale by the
  wiki. The **live homepage still serves Google 92**, so the wiki's 123 "fix" never reached prod (or
  the homepage block was never redeployed). Trustpilot 51 is consistent (wiki + live homepage).
- **Publication safety:** **do_not_publish any review count until reconciled and timestamped.**
- **Action:** `recommend_source_refresh` (reconcile live homepage → 123, re-verify via `/browse`) +
  `recommend_validator_change` (denylist `92`/`47` as review counts in OKF output) +
  `recommend_test_change` (test asserting the denylist). Human decision required: confirm the true
  current Google count via browser before any Review concept is curated.

## C-02 — Package count: 16 vs 15 vs 7–8

| Surface | Packages | Note |
|---|---|---|
| Live homepage | **16** ("6 Surabaya, 4 Bali, plus others") | marketing surface |
| llm-wiki SSOT v6.0 | **15** (11 Surabaya + 4 Bali) | canonical knowledge |
| jvto-itinerary-core `11-package-route-map.json` | **7–8** route-mapped | operational subset, `inferred` |

- **Classification:** `conflicting`. Likely not a true contradiction — itinerary-core models a route
  subset, homepage rounds/bundles differently — but the canonical published set is ambiguous.
- **Action:** `recommend_evidence_research` — pin the canonical package list (and slugs) **before**
  any Tour Package concept is curated, else tour concepts inherit the ambiguity. Block tours until resolved.

## C-03 — Ijen altitude figure varies

| Surface | Ijen altitude | 
|---|---|
| itinerary-core `06-destination-activity-profiles.json` | 2,769 m |
| Live homepage | 2,386 m |
| (general public fact) | summit ~2,769 m; crater-rim viewpoint ~2,386 m |

- **Classification:** `conflicting` (definitional — summit vs rim). Low severity.
- **Action:** `recommend_evidence_research` — when a Kawah Ijen Destination concept is drafted, state
  *which* elevation (summit vs crater rim) with a primary citation; do not assert a bare number.

## C-04 — Bromo entrance pricing: current vs stale-in-the-wild

| Source | Foreign fee | Status |
|---|---|---|
| itinerary-core (PP 36/2024) | IDR 255,000 | `verified` current |
| operator blogs (flagged by core) | IDR 220,000 / 320,000 | `stale` |

- **Classification:** `stale` for the wild values; `official_first_party` for PP 36/2024.
- **Action:** `recommend_source_refresh`; if a pricing-bearing Policy/Guide concept is published, cite
  the regulation and **timestamp**; never reuse blog figures. Internal cost components → `do_not_publish`.

## C-05 — Two TripAdvisor listings for one operator

- Listing A `d19983165` and listing B `d24825561` both resolve to "Java Volcano Tour Operator,
  Surabaya". `conflicting` (duplicate-listing risk).
- **Action:** `recommend_evidence_research` — determine the canonical TripAdvisor listing + live count
  via `/browse` before a TripAdvisor Review concept; citing the wrong listing would understate proof.

## C-06 — Founder police detail enrichable across surfaces

- Homepage adds rank **"Bripka"** (Brigadir Kepala) + Ditpamobvit; SSOT says "active Tourist Police".
  Doctor registry (S6) shows the medical partner practises at **RS Bhayangkara Bondowoso** (police
  hospital) — an independent corroboration of the police linkage not currently exploited.
- **Classification:** `independent_public` corroboration. Not a conflict — an **enrichment**.
- **Action:** `recommend_update_existing_concept` (organization) once press Reference concepts exist;
  do **not** promote `reviewed→verified` on self-published wording alone.

## C-07 — Facebook review surface absent from the model

- Live: Facebook page shows "98% recommend, 41 reviews" — a fourth public review surface the SSOT
  trust graph (C6) does not model.
- **Classification:** `independent_public`. **Action:** `recommend_new_concept` (Review Platform:
  Facebook) — freshness-sensitive, timestamp required.

## C-08 — Empty public families vs evidence-rich upstream (coverage gap)

- Partners, credentials, references, destinations, policies, reviews, tours, travel-guides, trust/
  claims are **all empty** in the bundle while llm-wiki + itinerary-core + live registries hold strong
  evidence for each. `insufficient` (coverage). **Action:** `recommend_new_concept` /
  `recommend_new_partner` / `recommend_new_reference` — prioritized in the roadmap.

## Summary verdict
The repos are **logically consistent on structure** but **inconsistent on dynamic facts** (review
counts, pricing) and **ambiguous on canonical sets** (package count, TripAdvisor listing). The one
finding that must gate any publication is **C-01**: do not let a stale review count enter the public
bundle. Everything else is enrichment or coverage expansion.
