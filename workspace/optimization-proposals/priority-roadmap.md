# Priority Roadmap

**Date:** 2026-06-25. Ranked execution plan tying each step to a gap ID and the focused PR it becomes.
Ordering principle: fix correctness risks → publish authority-backed evidence → expand coverage →
reconcile the two `conflicting` families last.

## P0 — Correctness guardrails (before/with any publication)
1. **JVTO-11 stale review-count denylist + test** — GAP-OKF-02. Block `92`/`47` as review counts in
   any concept; unit test. *(Implemented — PR1.)*
2. **Do NOT publish review or tour concepts** — GAP-OKF-01, GAP-OKF-10. Hold until reconciled.
   *(Enforced by deferral; documented in gap register + candidate drafts.)*

## P1 — High-confidence, authority-backed publication (PR2)
3. **References** — GAP-OKF-05. `references/official-website` (E16), `references/satusehat-practitioner-registry`
   (E17, **verified**), `references/google-maps-business-listing` (E18). Publish first so other concepts cite them.
4. **Credentials** — GAP-OKF-03. `trust/credentials/medical-screening-license` (E1, **verified**, live
   registry), `trust/credentials/business-registration` (E2, NIB/TDUP), `trust/credentials/legal-entity-decree`
   (E3, AHU).
5. **Partners** — GAP-OKF-04. `trust/partners/bbksda-jatim` (E5), `trust/partners/hpwki` (E4),
   `trust/partners/isic` (E6).
6. **Trust Claims** — GAP-OKF-06. `trust/claims/police-led` (E7, hedged), `trust/claims/private-tours-only`
   (E8), `trust/claims/all-inclusive-pricing` (E9).
7. **Organization graph links** — GAP-OKF-09. Add `# Related Concepts` edges from `organization.md` to
   the new credentials/partners/claims; add the Satusehat + Google Maps references as supporting
   citations. **Stays `reviewed`** — no promotion to `verified` on self-published wording.

## P2 — Coverage expansion (PR2, same release if clean)
8. **Destinations** — GAP-OKF-07. `destinations/{kawah-ijen,mount-bromo,tumpak-sewu,madakaripura}` (E10–E13),
   elevation/superlatives qualified (GAP-OKF-14).
9. **Policies** — GAP-OKF-08. `policies/cancellation-travel-credit` (E14, **reviewed**),
   `policies/ijen-health-screening` (E15, **qualified**, conditional wording).
10. Build the safety graph triangle: Destination(Kawah Ijen) ↔ Policy(ijen-health-screening) ↔
    Partner(bbksda-jatim) ↔ Credential(medical-screening-license) ↔ Reference(satusehat).

## P3 — Deferred, needs a human decision or live reconcile (future PRs)
11. **Reconcile review counts** — GAP-OKF-01/17. `/browse` Trustpilot + the canonical TripAdvisor
    listing + Google Maps; set one canonical count; refresh live homepage 92→canonical; then publish
    Review Platform concepts (incl. Facebook E23) **timestamped**.
12. **Reconcile package set** — GAP-OKF-10. Pin canonical packages + slugs across SSOT/homepage/core,
    then generate Tour Package concepts (controlled-automation path already exists in `build_bundle.py`).
13. **Capture press URLs** — GAP-OKF-12. Get exact Detik/Radar Jember/BBKSDA article URLs; publish as
    press References; then upgrade `organization.md` / `police-led` citations toward `verified`.
14. **Taxonomy proposals** — GAP-OKF-11/16. Owner decision: add `Partner`(/`Reference`) to
    `required_citation_types`; split the `trust/` family in `concept-map.yaml`.
15. **Pricing concepts** — GAP-OKF-15. Only if a freshness/timestamp gate exists; cite the regulation.

## Focused PR plan
- **PR1 — `chore/okf-audit-and-validator-hardening`**: `workspace/**` audit artifacts + JVTO-11
  validator rule + unit test. Docs/tooling only; no bundle concept changes.
- **PR2 — `feat/okf-high-confidence-concepts`**: curation records + built bundle concepts for steps
  3–9 + organization graph links. Passes `validate_okf.py --release --strict-links` and the full test
  suite. No review/tour concepts, no dynamic counts, no internal data.
- **Future PRs**: steps 11–15, each gated on its human decision / live reconcile.

## Success criteria
- Bundle grows 1 → ~19 concepts, ≥1 `verified` (registry-backed), connected graph, **zero** stale
  counts, **zero** unsafe data, both `conflicting` families explicitly deferred with reasons.
