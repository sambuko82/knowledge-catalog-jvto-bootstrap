# External Source Health — Live Verification Snapshot (corrected)

**Run date:** 2026-06-25 · **Method:** automated WebFetch/WebSearch **plus** an independent
adversarial verification pass (18 agents). Where the two disagreed, the adversarial result wins —
notably the Satusehat record (a first single-pass fetch fabricated a "valid" record; a clean fetch
shows it is login-gated). Every dynamic value is point-in-time.

| # | Source | URL | HTTP | Observed (2026-06-25) | Class | Note |
|---|---|---|---|---|---|---|
| S1 | JVTO homepage | javavolcano-touroperator.com | 200 | Trustpilot 4.8/51, Google 4.90/**92**, TripAdvisor 4.95/21; NIB 1102230032918; founder Agung Sambuko (Bripka, Ditpamobvit); "16 tours" | `primary_public` | **Homepage Google 92 is stale** vs canonical 123. Owner should refresh the live site. Bundle already uses 123. |
| S2 | Trustpilot | trustpilot.com/review/javavolcano-touroperator.com | **403** | not readable; search snippet "34" is a *subset*, not the total | `unreachable` | Bundle's 51 (timestamped 2026-05-18) comes from the canonical SSOT, not this fetch. |
| S3 | TripAdvisor A | …d19983165… | **403** | not readable | `unreachable` | Bundle cites this listing. |
| S4 | TripAdvisor B | …d24825561… | listed | second listing, same operator | `conflicting` | Duplicate listing; confirm canonical. |
| S5 | Google Maps (CID) | google.com/maps?cid=1266403973589689021 | 302→JS | no title to automated fetch; CID well-formed | `unreachable` | Reference concept must be a **pointer only**, no count. |
| S6 | **Satusehat practitioner** | satusehat.kemkes.go.id/sdmk/nakes/QN00001073380217 | 200 | **"Laman profil publik belum tersedia"** — login-gated; no name/SIP/facility/expiry shown publicly | `unreachable` + **sensitive** | **Correction:** an earlier single-pass fetch fabricated a full "valid" record. Not publicly verifiable; PII risk. **do_not_publish.** |
| S7 | RS Bhayangkara Bondowoso doctor list | hospital site | 200 | "Ahmad Irwandanu" **absent** from the 20 named doctors | `insufficient` | No independent corroboration of the name. |
| S8 | AHU portal | ahu.go.id | interactive | decree `AHU-0023020.AH.01.02.TAHUN 2023` not on public site; only HPWKI assoc. AHU is public | `insufficient` | Legal-entity decree → `do_not_publish`. |
| S9 | OSS / NIB | oss.go.id (NIB 1102230032918) | JS portal | not queryable in session; first-party only | `supporting_context` | NIB stays `reviewed` (first-party), not `verified`. |
| S10 | BBKSDA Jatim | bbksdajatim.org; ksdae.menlhk.go.id | 200 | authority for Ijen; Ijen Blue Fire e-ticket, QRIS, guide training (incl. HPWKI, May 2024) | `independent_public` | Authority confirmed; **does not name/endorse JVTO**. |
| S11 | ISIC/Totum | isic.totum.com/discounts?providerId=259268 | 200 (member page 429) | provider id 259268 indexed to "Java Volcano Tour Operator"; student page "no packages available" | `independent_public` | Directory listing; assert no discount %. |
| S12 | Facebook | facebook.com/javavolcanotours | indexed | "98% recommend / 41 reviews" | `independent_public` | Unmodeled review surface. |
| S13 | Detik press | (exact URL unknown) | **404** on guessed slug | not confirmed | `insufficient` | Capture exact URL before any press Reference. |
| S14 | Smithsonian GVP | volcano.si.edu (Tengger Caldera 263310; Ijen 263350) | 200 | confirms Bromo active cone; Ijen geology | `independent_public` (authority) | Enables `verified` on mount-bromo. |
| S15 | Probolinggo Regency tourism | pariwisata.probolinggokab.go.id | 200 | states Madakaripura is the **tallest in Java** (~200 m) | `official_first_party` (govt) | Enables `verified` on madakaripura. |

## Conclusions
- **Bot-blocked review platforms** (S2/S3/S5) are `unreachable` for automated runs — a `/browse`
  stealth pass is the way to live-confirm counts; the bundle's timestamped values stand meanwhile.
- **Satusehat/AHU (S6–S8)** are not publicly readable → permanently `do_not_publish` until the
  registries expose public profiles AND the PII concern is resolved.
- **Two real authority upgrades** exist (S14 Smithsonian, S15 Probolinggo govt) for the destinations.
- **One website bug** (S1 Google 92) is the owner's to fix; the bundle is already correct.
