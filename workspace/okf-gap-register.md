# OKF Gap Register

**Date:** 2026-06-25. Enumerated gaps with severity, evidence status, recommended action, expected
OKF-quality impact, and whether a human decision is required. Severity: P0 (correctness risk) →
P3 (nice-to-have).

| Gap | Severity | Family | Description | Evidence status | Action | Impact | Human decision |
|---|---|---|---|---|---|---|---|
| **GAP-OKF-01** | P0 | Review Platform | Review counts disagree across 4 surfaces (raw 47/92, wiki 51/123, live homepage 51/92); platforms bot-blocked | `conflicting`+`stale`; live ⛔403 | `do_not_publish` now → `recommend_source_refresh` (reconcile via `/browse`) | Prevents publishing a wrong trust number | **Yes** — confirm true Google count |
| **GAP-OKF-02** | P0 | tooling | Validator accepts known-stale counts (92/47) | confirmed in `validate_okf.py` | `recommend_validator_change` (JVTO-11) + `recommend_test_change` | Stops stale counts entering bundle | No *(done this audit)* |
| **GAP-OKF-03** | P1 | Credential | No Credential concepts; NIB/TDUP, AHU decree, doctor SIP unused | E1 `official_first_party` (live ✅), E2/E3 (homepage+registry) | `recommend_new_concept` | Trust layer → authority-backed | No |
| **GAP-OKF-04** | P1 | Partner | No Partner concepts; BBKSDA, HPWKI, ISIC unused | E4–E6 `official/independent_public` | `recommend_new_partner` | Adds verifiable relationships | No |
| **GAP-OKF-05** | P1 | Reference | No Reference concepts; citations not centralized | E16–E18 (live ✅ for E16/E17) | `recommend_new_reference` | De-duplicates citations; de-circularizes claims | No |
| **GAP-OKF-06** | P1 | Trust Claim | Narrative claims C1–C9 unmodeled (police-led, private-only, all-inclusive) | E7–E9 `primary_public` | `recommend_new_concept` (hedged wording) | Core positioning becomes navigable | No |
| **GAP-OKF-07** | P2 | Destination | No Destination concepts (Ijen, Bromo, Tumpak Sewu, Madakaripura) | E10–E13 `primary_public` (live ✅) | `recommend_new_concept` | Anchors the product graph | No |
| **GAP-OKF-08** | P2 | Policy | No Policy concepts (cancellation, Ijen health-screening) | E14 `primary_public`; E15 needs conditional wording | `recommend_new_concept` (E15 `qualified`) | Publishes customer-facing rules safely | No |
| **GAP-OKF-09** | P1 | Organization | `organization.md` cites only its own homepage for "police-led" (single self-published source) | E7 + corroboration via E1/E21 | `recommend_update_existing_concept` (graph links + independent refs) | Reduces circular citation | No (publish), **Yes** for press (E21) |
| **GAP-OKF-10** | P2 | Tour Package | Tours unpublished AND package count ambiguous (16/15/7–8) | E20 `conflicting` | `do_not_publish` now → `recommend_evidence_research` (Phase 4) | Unblocks tours once reconciled | **Yes** — pin canonical set |
| **GAP-OKF-11** | P2 | taxonomy | `Partner`/`Reference` absent from `required_citation_types` | V2 | `recommend_taxonomy_change` + `recommend_validator_change` | Forces evidence on relationship concepts | **Yes** |
| **GAP-OKF-12** | P2 | Reference | Press coverage (Detik/Radar Jember/BBKSDA) lacks captured canonical URLs (Detik 404) | E21 `independent_public`+`insufficient` | `recommend_evidence_research` | Converts press into citable refs; de-circularizes E7 | **Yes** |
| **GAP-OKF-13** | P3 | Review Platform | Facebook (98%/41) review surface unmodeled | E23 `independent_public` | `recommend_new_concept` (later, timestamped) | Adds an independent proof surface | **Yes** |
| **GAP-OKF-14** | P3 | Destination | Ijen elevation figure conflicting (summit 2769m vs rim 2386m) | C-03 `conflicting` | `recommend_evidence_research`; qualify wording in concept | Avoids asserting a contested number | No |
| **GAP-OKF-15** | P3 | Policy | Entrance-fee figures publishable but dynamic; stale 220k/320k circulate | E24 `official_first_party` / C-04 | `report_only` (timestamp if used) | Prevents stale pricing | **Yes** if published |
| **GAP-OKF-16** | P3 | taxonomy | `trust/` family collapses claims+credentials+partners w/ one upstream | V3 | `recommend_taxonomy_change` | Cleaner source-to-output mapping | **Yes** |
| **GAP-OKF-17** | P2 | Review Platform | Two TripAdvisor listings (d19983165 / d24825561) | C-05 `conflicting` | `recommend_evidence_research` | Avoids citing the wrong listing | **Yes** |

## Disposition this audit
- **Closing now (publish):** GAP-OKF-03/04/05/06/07/08 (the high-confidence set) + GAP-OKF-09 (graph
  links, publish-side) + GAP-OKF-02 (validator JVTO-11 + test).
- **Deferred with documented reason:** GAP-OKF-01 (reviews), GAP-OKF-10 (tours), GAP-OKF-12 (press),
  GAP-OKF-13/15/17 (need a human decision or `/browse` reconcile), GAP-OKF-11/16 (taxonomy proposals
  surfaced for owner decision).
