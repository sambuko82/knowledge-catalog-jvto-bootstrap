# Repo Exploration Report (corrected against real main `6e1a73c`)

**Date:** 2026-06-25. See `RE-BASELINE-NOTE.md` for why this supersedes the first pass. Read-only.

## 1. knowledge-catalog-jvto-bootstrap — the public bundle as it actually is

`okf/bundles/jvto/` currently holds **46 published concepts** (all `reviewed`, release-eligible),
built from human-curated YAML records via `build_bundle.py --curated --indexes`:

| Family | Count | Notes |
|---|---|---|
| organization | 1 | police-led framing, hedged ("presents itself as") |
| destinations | 5 | kawah-ijen, mount-bromo, tumpak-sewu, madakaripura, papuma-beach |
| policies | 9 | cancellation, ijen-health-screening, inclusions/exclusions, payment, booking-paths, police-escort, natural-phenomena, anti-fraud, isic-student |
| reviews | 3 | trustpilot (4.8/51), google-maps (4.9/123), tripadvisor (4.95/21) — **current, timestamped, hedged** |
| tours | 16 | 12 from-surabaya + 4 from-bali — **matches the homepage's "16 tours"** |
| travel-guides | 7 | best-time, bromo-vs-ijen, how-many-days, packing-fitness, safety, surabaya-vs-bali, weather-closures |
| trust/claims | 4 | police-led, medical-screening, no-hidden-costs, private-format |
| trust/credentials | 2 | legal-registration (NIB), verifiable-licenses (NIB/TDUP, BBKSDA, ISIC, police) |
| **trust/partners** | **0** | **empty — genuine gap** |
| **references** | **0** | **empty — genuine gap** |

**Build/curation model:** every concept has a source record under `okf/jvto/curation/approved/*.yaml`
(`organization, destinations, policies, reviews, travel-guides, trust, packages`). Editing a concept
means editing its YAML record, then `build_bundle.py --curated --indexes`. The committed `.md` files
are generated artifacts.

**Tooling (current):** `validate_okf.py` enforces OKF-01..JVTO-10; `publication-rules.yaml` already
lists **Partner and Reference** in `required_citation_types` (added in #8) and carries the
forbidden-term denylist. `tests/test_okf_tools.py` covers build/validate/fetch/release gates.

**Validator gap that remains:** no freshness/stale-value guard — a future edit could paste the live
homepage's stale "92 Google reviews" into a concept and pass. Addressed by the JVTO-11 guard added in
this audit's PR-A.

## 2. llm-wiki (knowledge SSOT — input only)
Two internal SSOTs, one of which is stale: `raw/JVTO_FINAL_CLEAN_SSOT.json` v6.0 (Trustpilot 47 /
Google 92) vs the operative `wiki/credentials/trust-signals.md` (Trustpilot 51 / Google 123, total
195) which states verbatim that 92/47 are stale. The **bundle followed the correct SSOT** (123/51).
Trust architecture (9 claims C1–C9, credentials, partners, press) is the candidate pool the bundle
draws from. Sensitive zones never to ingest: `raw/FINANCE/`, `raw/db_export_raw.json`, whatsapp/CRM, GPX.

## 3. jvto-itinerary-core (operational intelligence — input only)
`generated/itinerary-intelligence/*.json`: 6 destinations, 14 route legs, 7–8 route-mapped packages,
21 cost categories, recommendation rules. `customer_visible` flags + `contracts/pii-rules.yaml`
separate public-safe regulatory facts (entrance fees PP 36/2024, BBKSDA QRIS-only 2025-01-31, ferry
H-1) from internal cost/crew data. Confidence labels (`verified/inferred/manual_seed/needs_review`)
are reusable OKF evidence signals. Nothing here is auto-published.

## 4. Cross-cutting
- The bundle is **mature and conservative**: current counts, hedged claims, citation discipline.
- The two empty families (`partners`, `references`) and a handful of **accuracy/strengthening**
  opportunities in existing destinations are the real surface for optimization — not bulk creation.
- The only true correctness defect found is the **kawah-ijen "summit 2,386 m"** mislabel; everything
  else is enrichment or a live-website (not bundle) issue.
