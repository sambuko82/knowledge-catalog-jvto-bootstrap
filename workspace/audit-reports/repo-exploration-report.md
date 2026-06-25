# Repo Exploration Report

**Date:** 2026-06-25 · **Scope:** read-only exploration of all three repos. No public concept modified.

## 1. knowledge-catalog-jvto-bootstrap (the public OKF repo)

**Two layers:**
- `okf/bundles/jvto/` — the **public, portable bundle** (final output). Families: `organization.md`,
  `destinations/`, `tours/{from-bali,from-surabaya}/`, `policies/`, `travel-guides/`, `reviews/`,
  `references/`, `trust/{claims,credentials,partners}/`, plus `index.md` / `log.md`.
- `okf/jvto/` — curation + tooling: `config/` (`publication-rules.yaml`, `concept-map.yaml`,
  `upstreams.yaml`), `scripts/` (`validate_okf.py`, `build_bundle.py`, `fetch_snapshots.py`,
  `common.py`), `curation/approved/`, `docs/00..07`, `tests/test_okf_tools.py`, `skills/
  jvto-okf-verified-curation/SKILL.md`, `Makefile`, `pyproject.toml`.

**Published state (main):** exactly **one** concept — `okf/bundles/jvto/organization.md` (`status:
reviewed`, single homepage citation). Every other family `index.md` reads "No reviewed concepts are
published in this directory yet." Git shows concepts existed on branches/commits `da96a4e9` (5
verified) and `0480929` ("40 concepts") but **not in main** today.

**Evidence model (already defined — reuse, don't reinvent):**
- Status lifecycle: `draft → generated_pending_review → needs_review → reviewed → verified →
  qualified → published → deprecated`. Only `reviewed/verified/qualified/published` are release-eligible.
- `jvto-okf-verified-curation` skill enforces per-claim statuses (`verified/qualified/stale/conflict/
  unsupported/internal_only`) and a paired internal verification report under `build/verification/`.
  Core rule: **upstream presence (llm-wiki / itinerary-core) is never sufficient** to publish; a
  current public/authority source supporting the *exact* wording is required.
- `validate_okf.py` rules OKF-01..JVTO-10: frontmatter parse, required fields, visibility, known/
  release statuses, unique id, **required `# Citations` with a public URL** for the eight citable
  families, verification metadata on verified/qualified, forbidden-term scan, link-escape, link-resolve.

**Validator blind spots found:** no freshness/timestamp check on dynamic facts; no stale-value
denylist (e.g. would not catch a concept asserting "92 Google reviews"); citation rule checks
*presence* of a public URL, not that the URL actually supports the claim; no reachability check.

**Safety config:** `publication-rules.yaml` forbidden terms (customer email/phone, passport, payment
ref, vendor/crew rate, profit margin, api/private key). `upstreams.yaml` forbids `raw/`, `secrets/`,
`input/`, `seed/` prefixes from ever being ingested.

## 2. llm-wiki (knowledge SSOT — upstream input only)

**Two SSOTs that can disagree:**
- `raw/JVTO_FINAL_CLEAN_SSOT.json` v6.0 (2026-04-22): 13 domains, 15 packages, 50 routes, 9 narrative
  claims C1–C9, 15 credentials. **Contains the now-stale counts** (Trustpilot 4.8/47, Google 4.9/92).
- `wiki/credentials/trust-signals.md` (newer, 2026-05-26): the *operative* trust SSOT —
  **Trustpilot 4.8/51** (2026-05-18), **Google 4.9/123** (2026-05-26 API), TripAdvisor 4.95/21, total
  195 — and states verbatim "Any content showing 92 Google reviews or 47 Trustpilot is **stale**."

**Trust architecture:** 9 claims (C1 safety, C2 private-only, C3 all-inclusive, C4 Ijen health
screening, C5 proof-first, C6 reviews-as-registry, C7 team registry, C8 partnerships-by-function,
C9 press) mapped to 8 proof groups (legality, police, medical, partner, press, review, continuity,
history). Credentials: NIB/TDUP 1102230032918; AHU-0023020.AH.01.02.TAHUN 2023; founder Agung
Sambuko (Tourist Police, Ditpamobvit); Dr. Ahmad Irwandanu SIP; guide KTA licences; HPWKI / ISIC
(259268) / INDECON / BBKSDA partnerships; press (Detik, Radar Jember ×2, BBKSDA report); Stefan Loose
guidebook 2016; Booking.com 2015.

**Sprint/gap state** (`CLAUDE.md`, `wiki/log.md`): last GAP-01 pass (2026-06) conformed secondary
mentions to 123/195; open items GAP-06 (bromo-ijen status page), GAP-08 (Yadnya Kasada 2026), GAP-09
(market landing pages) — all "static-fallback sourceable", not true blockers.

**Sensitive zones (never ingest):** `raw/FINANCE/`, `raw/db_export_raw.json`, finance outputs,
whatsapp/CRM, GPX coordinate files (operational).

## 3. jvto-itinerary-core (operational intelligence — upstream input only)

**Output:** `generated/itinerary-intelligence/01..15*.json` (+manifest) compiled from llm-wiki,
jvto-web, new-backoffice via `contracts/`. Models 6 destinations, 14 route legs, **7–8 packages**,
21 cost categories, 12–15 recommendation rules.

**Public-safe vs internal (already labelled):** `customer_visible` flags separate published facts
(entrance fees, jeep included, weather/safety recommendations) from internal (vehicle/driver/escort/
crew cost, `actual_expense_calibration`). `contracts/pii-rules.yaml` blocks customer name/passport/
phone/email/address; `seed/` and `input/` are calibration/raw and OKF-forbidden.

**Public-safe regulatory facts** (good Policy/Reference evidence): Bromo PP 36/2024 entrance (foreign
IDR 255,000; domestic 54k/79k; mandatory online booking) — and an explicit warning that **220k/320k
operator-blog rates are stale**; Ijen BBKSDA fees (foreign 100k/150k; **QRIS-only since 2025-01-31**;
daily cap ~2,000; monthly volcanic closure); Ketapang–Gilimanuk ferry (Ferizy H-1 pre-book,
geofence 2.65 km, 2–3 h peak queue). Weather/flash-flood SOPs for Madakaripura ("2 PM rule") and
Tumpak Sewu.

**Confidence labelling:** every record carries `confidence ∈ {verified, inferred, manual_seed,
needs_review}` and `source_trace[]` — directly reusable as OKF evidence signals.

## 4. Cross-cutting observations
- The bootstrap repo is **architecturally complete but content-empty**: world-class curation
  guardrails, ~1 concept of payload. The binding constraint is curation throughput, not tooling.
- The richest, safest evidence (govt registries, doctor registry, press, association decrees) is
  **first-party/authority and currently 100% unused** by the public bundle.
- The single biggest *correctness* risk is dynamic review counts: three internal surfaces (raw SSOT
  47/92, wiki canonical 51/123, live homepage 51/**92**) disagree. Details in the consistency report.
