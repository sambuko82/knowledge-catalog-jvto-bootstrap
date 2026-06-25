# Source-Evidence Report (corrected; includes adversarial verification)

**Date:** 2026-06-25. Each candidate/existing claim was independently and **adversarially** verified
(18 verifiers, each told to refute and to find the safest public-supported wording). Classes per
`workspace/CLAUDE.md`. Status reflects what a *public* source supports, not what an internal repo says.

## A. Publishable — net-new families (genuinely empty today)

| Concept | Type | Status | Evidence class | Safe wording basis | Action |
|---|---|---|---|---|---|
| `references/official-website` | Reference | reviewed | `primary_public` | first-party domain; hedge "presents itself as" (no registry ties URL→entity) | `recommend_new_reference` |
| `references/google-maps-business-listing` | Reference | reviewed | `primary_public` | listing pointer only; **assert no count** (92↔123 contested) | `recommend_new_reference` |
| `trust/partners/bbksda-jatim` | Partner | reviewed | `independent_public` | frame as **governing conservation authority**, not commercial partner; "clearance" is first-party | `recommend_new_partner` |
| `trust/partners/hpwki` | Partner | reviewed | `independent_public` (assoc. corroborated by BBKSDA training) | "JVTO states it holds membership…"; AHU number self-reported | `recommend_new_partner` |
| `trust/partners/isic` | Partner | reviewed | `independent_public` | ISIC/Totum directory listing provider 259268; no discount % asserted; student page currently empty | `recommend_new_partner` |

## B. Existing concepts — strengthen / correct (already published)

| Concept | Finding | Status target | Action |
|---|---|---|---|
| `destinations/kawah-ijen` | mislabels rim **2,386 m** as "summit" (summit ~2,769–2,799 m); "active" should hedge (PVMBG Level 1 Normal, Sep 2025) | reviewed (corrected) → `qualified` | `recommend_update_existing_concept` |
| `destinations/mount-bromo` | geology supportable by Smithsonian GVP (vn 263310) | `verified` | `recommend_update_existing_concept` |
| `destinations/madakaripura` | Probolinggo govt office states it **is** the tallest in Java | `verified` | `recommend_update_existing_concept` |
| `destinations/tumpak-sewu` | "multi-tier" → "semicircular curtain (~120 m)"; add independent cites | reviewed | `recommend_update_existing_concept` |
| `trust/credentials/verifiable-licenses` | "BBKSDA clearance to operate" overstated (not on BBKSDA site) | reviewed (soften) | `recommend_update_existing_concept` (owner-gated) |
| `policies/ijen-health-screening` | better-sourced via jatimtimes (Jan 2024 rule); JVTO-coordination is first-party | `qualified` | `report_only` (already hedged) |

## C. DEFER / do_not_publish (adversarially refuted)

| Item | Why | Class | Action |
|---|---|---|---|
| `references/satusehat-practitioner-registry` | URL login-gated ("public profile not yet available"); name/SIP/expiry not public; **PII risk** | `unreachable` + sensitive | `do_not_publish` |
| `trust/credentials/medical-screening-license` | same Satusehat gating; bundle already uses safe generic wording instead | `unreachable` + sensitive | `do_not_publish` |
| `trust/credentials/legal-entity-decree` | AHU decree string absent from public site (only HPWKI assoc. AHU is public) | `insufficient` | `do_not_publish` |
| `trust/credentials/business-registration` (as new) | duplicates existing `legal-registration`; "NIB/TDUP 1102230032918" wrongly assigns NIB digits to TDUP | redundant + `supporting_context` | `report_only` (don't add) |
| Review counts as facts | bundle already correct (123/51); **live homepage 92 stale** | `stale` (website) | `recommend_source_refresh` (website) |
| Entrance fees, internal cost/crew/margins | dynamic / `internal_only` | dynamic / internal | `report_only` / `do_not_publish` |

## Key evidence lessons
- **Authority ≠ reachable.** Three "authority" sources (Satusehat ×2, AHU) are not publicly readable;
  a single-pass WebFetch fabricated a "valid" Satusehat record that the adversarial pass corrected.
  Anything resting only on the internal repo's source-health note must stay `do_not_publish`.
- **First-party is the honest ceiling for most trust claims** (police-led, private-only, all-inclusive,
  NIB): publishable as `reviewed` with "presents itself as / states" hedging — which the bundle
  already does. None should be promoted to `verified` on self-published wording.
- **The only authority-grade upgrades available** are the two destinations with real third-party
  sources (Bromo→Smithsonian GVP; Madakaripura→Probolinggo govt).
