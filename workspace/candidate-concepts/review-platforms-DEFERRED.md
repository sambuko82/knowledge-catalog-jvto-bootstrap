---
status: candidate
do_not_publish: true
blocked_by: GAP-OKF-01, GAP-OKF-17
families: [Review Platform]
generated: "2026-06-25"
---

# DEFERRED — Review Platform concepts (do not publish)

Blocked by the review-count contradiction (C-01) and the duplicate-TripAdvisor-listing issue (C-05).
**Not publishable until a single canonical count is reconciled via `/browse`.**

## Contradiction snapshot (2026-06-25)
| Platform | raw SSOT v6.0 | wiki canonical | live homepage | platform (automated) |
|---|---|---|---|---|
| Trustpilot | 4.8 / 47 | 4.8 / 51 (2026-05-18) | 4.8 / 51 | ⛔ 403 (search snippet "34") |
| Google Maps | 4.9 / 92 | 4.9 / 123 (2026-05-26 API) | 4.9 / **92** | ⛔ JS app |
| TripAdvisor | 4.95 / 21 | 4.95 / 21 | 4.95 / 21 | ⛔ 403; **two listings** d19983165 / d24825561 |
| Facebook | — (unmodeled) | — | — | "98% recommend / 41 reviews" (snippet) |

## Required before publishing
1. `/browse` each platform (stealth) to read the live canonical count.
2. Decide the canonical Google count (homepage 92 vs wiki 123) and refresh the live homepage.
3. Identify the canonical TripAdvisor listing.
4. Author Review Platform concepts with `last_verified` + the platform-specific rating (never
   interchange Trustpilot 4.8 with Google 4.9), and a freshness note. Subject to JVTO-11 denylist.
