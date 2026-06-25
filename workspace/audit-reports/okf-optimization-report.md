# OKF Optimization Report (corrected against real main `6e1a73c`)

**Date:** 2026-06-25. The bundle is mature (46 concepts, current counts, hedged claims). Optimization
is now about **accuracy, two empty families, and graph edges** — not bulk creation.

## 1. Correctness defect (fix)
- `destinations/kawah-ijen` labels the **crater rim (2,386 m) as the "summit"**. Summit is
  ~2,769–2,799 m (Wikipedia / Smithsonian GVP). → `recommend_update_existing_concept`. *(PR-B.)*

## 2. Authority-grade strengthening (existing destinations)
- `mount-bromo` → add Smithsonian GVP (vn 263310) citation, status `verified`.
- `madakaripura` → add Probolinggo Regency tourism citation (states tallest in Java), status `verified`.
- `tumpak-sewu` → "multi-tier" → "semicircular curtain (~120 m)"; add independent citations.
→ moves the destinations family from first-party-only to authority-anchored.

## 3. Empty families (net-new, evidence-sufficient)
- **`references/`**: `official-website`, `google-maps-business-listing` (pointer, no count). Centralizes
  the most-repeated citations. → `recommend_new_reference`.
- **`trust/partners/`**: `bbksda-jatim` (framed as **governing authority**), `hpwki` (net-new; assoc.
  corroborated by BBKSDA training), `isic` (directory listing). → `recommend_new_partner`.
  Note overlap: BBKSDA + ISIC are already named inside `trust/credentials/verifiable-licenses`; the
  Partner concepts add a properly-scoped, correctly-hedged relationship node and a graph anchor.

## 4. Weak / overstated citations (existing)
- `trust/credentials/verifiable-licenses` asserts "BBKSDA clearance to operate" — not on BBKSDA's
  site; soften to "states that it holds…". → `recommend_update_existing_concept` (owner-gated).
- `organization` + most `trust/claims` cite only the homepage. That is the honest ceiling for
  self-presented facts; keep hedged, do **not** promote to `verified`. The BBKSDA/HPWKI/ISIC Partner
  and the new Reference concepts give claims somewhere independent-ish to point.

## 5. Missing graph edges (after PR-B)
- `destinations/kawah-ijen` ↔ `policies/ijen-health-screening` ↔ `trust/partners/bbksda-jatim`
  (the Ijen safety triangle).
- `trust/claims/police-led` ↔ `references/official-website`; reviews ↔ `references/google-maps-business-listing`.
- Each new Partner/Reference cross-links to the concept it supports.

## 6. Validator / taxonomy
- **#8 already added** Partner/Reference to `required_citation_types` — earlier "taxonomy gap" is
  closed. ✔
- **Remaining gap:** no stale-value / freshness guard. → `recommend_validator_change` **JVTO-11**
  (denylist 92/47 near a platform name) + `recommend_test_change`. *(PR-A.)*
- Optional future: a curation lint flagging a `Trust Claim`/`Credential` whose only citation is the
  bundle's own base URL (forces ≥1 independent source). `report_only`.

## 7. Do-not-touch (correctly excluded by the bundle already)
- Satusehat doctor record, AHU legal-entity decree (not publicly readable; PII). 
- Internal cost/rate/crew/margin data. 
- Live-website Google "92" (owner fixes the site, not the bundle).

## Expected impact
Small, high-confidence: 1 factual fix, 2–3 authority upgrades, 2 new families (5 concepts), a
defensive validator. The bundle stays 100% current and safe; no `conflicting`/`stale`/`sensitive`
data is introduced.
