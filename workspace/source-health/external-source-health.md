# External Source Health — Live Verification Snapshot

**Run date:** 2026-06-25 · **Method:** WebFetch / WebSearch (automated, US egress). Bot-protected
review platforms block automated fetch (HTTP 403) and require an interactive browser (`/browse` with
stealth) to read live counts. Treat every dynamic value below as **point-in-time**; any OKF concept
citing these must timestamp or exclude the number.

## Reachability + observed values

| # | Source | URL | HTTP | Live observed value (2026-06-25) | Evidence class | Note |
|---|---|---|---|---|---|---|
| S1 | JVTO homepage | https://javavolcano-touroperator.com | 200 | Trustpilot 4.8/**51**, Google 4.90/**92**, TripAdvisor 4.95/**21**; NIB 1102230032918; founder "Agung Sambuko", rank **Bripka**, Ditpamobvit; "16 private tours (6 Surabaya, 4 Bali, plus others)" | `primary_public` | **Homepage still shows Google 92** — contradicts wiki canonical 123 (see C-01). Trustpilot 51 matches wiki. |
| S2 | Trustpilot profile | https://www.trustpilot.com/review/javavolcano-touroperator.com | **403** | unreadable via fetch; search snippet showed "4-star, 34 reviews" (Trustpilot indexes a review *subset*, not the canonical total) | `unreachable` | Need `/browse` to read live TrustScore + count. Do not trust the 34 snippet as the canonical count. |
| S3 | TripAdvisor listing A | …-d19983165-… | **403** | unreadable via fetch | `unreachable` | Primary attraction listing. |
| S4 | TripAdvisor listing B | …-d24825561-… | (listed) | second distinct listing ID for same operator | `conflicting` | **Two TripAdvisor listings** — possible duplicate; confirm canonical before publishing a Review concept. |
| S5 | Google Maps (CID) | https://www.google.com/maps?cid=1266403973589689021 | n/a | not fetched (JS app; needs browser) | `unreachable` | wiki canonical 4.9/123 (API, 2026-05-26); homepage shows 92. |
| S6 | Satusehat doctor registry | https://satusehat.kemkes.go.id/sdmk/nakes/QN00001073380217 | 200 | **VALID** — Ahmad Irwandanu; STR QN00001073380217; SIP 503.446/658-1268/DRU/4/430.9.13/2025; practice **RS Bhayangkara Bondowoso**; licence 2025-12-11 → **2031-01-13**; SKP status "Tidak Cukup" as of 2026-06-25 | `official_first_party` | Practice site is the **police hospital** — independently reinforces the police/medical proof link. Strong Credential candidate. |
| S7 | Facebook page | https://www.facebook.com/javavolcanotours/ | (indexed) | search snippet: **98% recommend, 41 reviews** | `independent_public` | **Unmodeled review surface** — not in SSOT trust graph. Candidate Review Platform. |
| S8 | Detik press article | (exact URL unknown) | **404** on guessed slug | not confirmed | `insufficient` | Article cited in wiki (2021-03-14) but no canonical URL on file. Needs exact-link research before use as a Reference. |
| S9 | OSS / NIB registry | https://oss.go.id (lookup by NIB 1102230032918) | not fetched | interactive lookup | `official_first_party` (pending) | NIB is govt-issued; verify via OSS portal in a browser session. |
| S10 | AHU portal | https://ahu.go.id (decree AHU-0023020.AH.01.02.TAHUN 2023; HPWKI AHU-0001072.AH.01.07.TAHUN 2024) | not fetched | interactive lookup | `official_first_party` (pending) | Legal-entity + association decrees; AHU-searchable. |

## Conclusions for the audit
- **C-01 (live-confirmed):** Live homepage Google-Maps count (92) is **stale** vs the wiki's own
  canonical (123, API-verified 2026-05-26). The internal "fix homepage 92→123" task did not reach the
  live surface (or surfaces disagree). → `recommend_source_refresh` on the live site **and** a
  validator denylist for 92/47 in OKF output (`recommend_validator_change`).
- **Trustpilot 51** is corroborated by the live homepage and the wiki canonical (2026-05-18) → safe
  basis for a Review concept *if timestamped*, but the platform itself is bot-blocked, so the canonical
  count must be captured via `/browse`, not search snippets (which showed a misleading "34").
- **Two TripAdvisor listings (S4)** must be reconciled before any TripAdvisor Review concept.
- **Doctor registry (S6)** and **govt registries (S9/S10)** are first-party authority sources, reachable
  or browser-verifiable — the strongest evidence in the whole graph, currently unused by the bundle.
- **Facebook (S7)** is an independent review surface the SSOT does not model at all.
- Review platforms that block automated fetch are classified `unreachable` **for this run** — not
  "missing"; a follow-up `/browse` pass can promote them.
