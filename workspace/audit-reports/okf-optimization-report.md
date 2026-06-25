# OKF Optimization Report

**Date:** 2026-06-25. Missing concepts, weak/circular citations, missing graph edges, taxonomy gaps,
validator gaps. Each item carries a recommended action.

## 1. Missing concepts (coverage)
The bundle has 1 of a plausible ~30+ concepts. Highest-value, evidence-backed gaps (publishable now):
- **Credentials** (none published): business-registration (NIB/TDUP), legal-entity-decree (AHU),
  medical-screening-license (doctor SIP, **live-verified**). → `recommend_new_concept`.
- **Partners** (none): BBKSDA Jatim, HPWKI, ISIC. → `recommend_new_partner`.
- **References** (none): official website, Satusehat registry, Google Maps listing. → `recommend_new_reference`.
- **Trust Claims** (none): police-led, private-tours-only, all-inclusive-pricing. → `recommend_new_concept`.
- **Destinations** (none): Kawah Ijen, Mount Bromo, Tumpak Sewu, Madakaripura. → `recommend_new_concept`.
- **Policies** (none): cancellation/travel-credit, Ijen health-screening (qualified). → `recommend_new_concept`.

Deferred (evidence not yet clean): **Reviews** (C-01), **Tours** (C-02), **press References** (E21),
**Travel Guides** (bromo-ijen status — wiki GAP-06 static-fallback; Yadnya Kasada — wiki GAP-08).

## 2. Weak / circular citations
- `organization.md` cites **only** `https://javavolcano-touroperator.com` (the subject's own homepage)
  for every claim including "police-led" — a single self-published citation. **Circular-ish**: the
  trust claim and its evidence are the same surface. → `recommend_update_existing_concept`: add
  independent Reference concepts (registry, press once E21 resolved) and graph-link them.
- The generated draft pipeline emits `# Citations\n- {public package URL}` — citation *presence* but
  not *support*; the validator cannot tell a topic link from a claim-supporting link. → see §5.

## 3. Missing graph edges (the bundle is nearly edgeless)
Today only `organization.md → /tours/index.md, /policies/index.md` (index stubs). Target edges once
concepts exist:
- Organization → Credentials (NIB, AHU, doctor SIP), Partners (BBKSDA/HPWKI/ISIC), Trust Claims.
- Destination(Kawah Ijen) ↔ Policy(ijen-health-screening) ↔ Partner(BBKSDA) — the safety triangle.
- Trust Claim(police-led) → Credential(medical-screening-license at police hospital) → Reference(Satusehat).
- Every Credential/Partner/Claim → its Reference (centralized citation).
→ `recommend_update_existing_concept` + author concepts with explicit `# Related Concepts` links.

## 4. Taxonomy gaps
- **Reference** and **Partner** types are used by the data model (concept-map `trust/` family) but are
  **not** in `required_citation_types`. A Partner asserts a real-world relationship yet is not required
  to cite evidence. → `recommend_taxonomy_change` + `recommend_validator_change`: add `Partner` (and
  optionally `Reference`) to `required_citation_types`.
- `concept-map.yaml` collapses claims/credentials/partners under a single `trust/` family with one
  upstream candidate (`trust-bundle/claims.json`); credentials & partners have distinct upstream
  evidence (registries, association decrees) not modeled. → `recommend_taxonomy_change` (split trust
  sub-families with their own `upstream_candidates`).
- No `Review Platform` freshness sub-status; review concepts need a dynamic-fact marker. → see §5.

## 5. Validator / test gaps (confirmed against `validate_okf.py`)
- **No stale-value denylist.** A concept asserting "92 Google reviews" or "47 Trustpilot reviews"
  (both self-declared stale by the wiki) passes today. → `recommend_validator_change` **JVTO-11**:
  fail on known-stale review counts; + `recommend_test_change` (unit test). *(Implemented this audit.)*
- **No freshness gate on dynamic facts.** `verified/qualified` require `last_verified` metadata, but a
  `reviewed` concept can assert a price/count with no timestamp. → `recommend_validator_change`:
  warn when a concept contains a number-bearing review/price token without `last_verified`.
- **Citation support not checked.** JVTO-04 only checks a URL exists in `# Citations`. → out of scope
  for static validation; `recommend_test_change`: a curation lint that flags a Citations section whose
  only URL is the bundle's own `canonical_public_base_url` for `Trust Claim`/`Credential` types
  (forces at least one independent source).
- **No reachability/HTTP check** (by design — offline build). Document as a manual `/browse` gate in
  the curation skill rather than the validator.

## 6. Source-refresh opportunities
- **C-01**: refresh live homepage Google count 92→canonical (reconcile 123 via `/browse` first).
- **C-04**: ensure no stale entrance-fee figures (220k/320k) ever reach a concept.
- Re-pull press exact URLs (E21) to convert `independent_public` press into citable References.

## 7. Expected impact (if the publishable set ships)
- Trust layer moves from **1 self-cited concept** → ~18 concepts, several **authority-backed**
  (registry-verified doctor SIP, govt IDs), with a connected graph (Org↔Credential↔Reference,
  Destination↔Policy↔Partner). This is the single largest OKF-quality jump available from current
  evidence — without importing either known inconsistency (reviews, tours).
