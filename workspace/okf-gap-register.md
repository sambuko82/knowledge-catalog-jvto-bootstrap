# OKF Gap Register (corrected against real main `6e1a73c`)

**Date:** 2026-06-25. Real gaps only — the bundle already has 46 current, hedged concepts.
Severity P0 (correctness) → P3 (nice-to-have).

| Gap | Sev | Family | Description | Evidence | Action | Human decision |
|---|---|---|---|---|---|---|
| **GAP-01** | P1 | Destination | `kawah-ijen` mislabels crater rim **2,386 m** as "summit" (summit ~2,769–2,799 m) | `conflicting` (Wikipedia/GVP) | `recommend_update_existing_concept` *(PR-B)* | No |
| **GAP-02** | P2 | Destination | `mount-bromo` first-party-only; Smithsonian GVP available | `independent_public` | `recommend_update_existing_concept` → `verified` *(PR-B)* | No |
| **GAP-03** | P2 | Destination | `madakaripura` hedged; Probolinggo govt states it **is** tallest in Java | `official_first_party` | `recommend_update_existing_concept` → `verified` *(PR-B)* | No |
| **GAP-04** | P3 | Destination | `tumpak-sewu` "multi-tier" imprecise → "semicircular curtain" | `independent_public` | `recommend_update_existing_concept` *(PR-B)* | No |
| **GAP-05** | P1 | Partner | `trust/partners/` empty; BBKSDA (authority), HPWKI (net-new), ISIC available | `independent_public` | `recommend_new_partner` *(PR-B)* | No |
| **GAP-06** | P2 | Reference | `references/` empty; official-website + google-maps pointer | `primary_public` | `recommend_new_reference` *(PR-B)* | No |
| **GAP-07** | P1 | tooling | No stale-value guard; live homepage "92" could be pasted into a concept | confirmed | `recommend_validator_change` JVTO-11 + `recommend_test_change` *(PR-A)* | No |
| **GAP-08** | P1 | Credential | `verifiable-licenses` overstates "BBKSDA clearance to operate" (not on BBKSDA site) | `supporting_context` | `recommend_update_existing_concept` (soften) | **Yes** |
| **GAP-09** | P0\* | website | **Live homepage shows Google 92** vs canonical 123 (\*severity is for the website, not the bundle) | `stale` (live) | `recommend_source_refresh` (owner fixes site) | **Yes** |
| **GAP-10** | — | Credential | Satusehat doctor record + AHU legal-entity decree not publicly readable; **PII** | `unreachable`+sensitive | `do_not_publish` (bundle already complies) | **Yes** |
| **GAP-11** | P3 | Review Platform | Two TripAdvisor listings (d19983165 / d24825561) | `conflicting` | `recommend_evidence_research` (confirm canonical) | **Yes** |
| **GAP-12** | P3 | Review Platform | Facebook (98%/41) unmodeled | `independent_public` | `recommend_new_concept` (later, timestamped) | **Yes** |
| **GAP-13** | P3 | Reference | Press (Detik/Radar Jember/BBKSDA report) lacks captured canonical URLs | `insufficient` | `recommend_evidence_research` | **Yes** |

## Disposition this audit
- **PR-A:** GAP-07 (validator) + the corrected `workspace/` audit.
- **PR-B:** GAP-01 (fix), GAP-02/03 (verified upgrades), GAP-04 (wording), GAP-05 (Partners), GAP-06 (References).
- **Surfaced for owner decision (not changed):** GAP-08 (soften clearance wording), GAP-09 (website
  92→123), GAP-10 (keep deferred), GAP-11/12/13 (need browser/exact-URL research).
