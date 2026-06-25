---
status: candidate
do_not_publish: true
generated: "2026-06-25"
---

# DEFERRED — do not publish (adversarially refuted or owner-gated)

These were considered and rejected for the public bundle this pass. Recorded so they are not
re-attempted without the stated condition being met.

## Authority records that are NOT publicly readable (PII risk) — GAP-10
- **Satusehat doctor registry** `QN00001073380217`: a clean fetch returns *"Laman profil publik belum
  tersedia"* (login-gated). Name/SIP/practice/expiry are not public; the doctor's name is absent from
  the hospital's published list. Publishing any of it would expose a named individual's government
  credential. **Condition to revisit:** the registry exposes a public profile AND a privacy review
  clears it. The bundle already uses safe generic wording ("trained medical staff / licensed doctor
  on file") in `trust/claims/medical-screening` — keep that.
- **AHU legal-entity decree** `AHU-0023020.AH.01.02.TAHUN 2023`: not displayed on the public site (the
  only public AHU number is the **HPWKI association** decree, a different credential). **Condition:**
  capture the decree from the AHU portal via a browser session.

## Dynamic / drifting facts
- **Review counts** — the bundle is correct (Google 123 / Trustpilot 51 / TripAdvisor 21, timestamped).
  The **live homepage still shows Google 92** → owner refreshes the *website*, not the bundle (GAP-09).
- **Facebook** (98% / 41) — unmodeled review surface (GAP-12); only with a timestamp + `/browse` confirm.
- **Entrance fees** (Bromo 255k PP 36/2024; Ijen 100/150k; QRIS-only 2025-01-31) — publishable but
  dynamic; keep out unless timestamped and regulation-cited. Stale 220k/320k must never be used.

## Research-needed before publishing
- **Press references** (Detik 2021, Radar Jember ×2, BBKSDA report) — exact canonical URLs not captured
  (guessed Detik slug 404). Capture, then publish as press References to de-circularize "police-led" (GAP-13).
- **Canonical TripAdvisor listing** — two listings exist (d19983165 / d24825561); confirm via `/browse` (GAP-11).

## Redundant
- A new `trust/credentials/business-registration` would duplicate the existing `legal-registration`
  (NIB) concept and risks attaching the NIB number to TDUP. Do not add.
