---
status: candidate
do_not_publish: true
blocked_by: GAP-OKF-10
families: [Tour Package]
generated: "2026-06-25"
---

# DEFERRED — Tour Package concepts (do not publish)

Blocked by the package-count contradiction (C-02): homepage **16**, llm-wiki SSOT **15**
(11 Surabaya + 4 Bali), itinerary-core route-map **7–8**. The canonical published set and slug
list must be pinned first (Phase 4 / GAP-OKF-10), else every tour concept inherits the ambiguity.

## Path when unblocked
- `build_bundle.py` already has a controlled-automation generator (`build_packages()`) that reads the
  llm-wiki Package Readiness snapshot and emits `generated_pending_review` drafts. Reconcile the
  canonical set, refresh the snapshot, generate drafts, then human-review each against the live
  package page (price = "check live page", never a hard-coded number) before promoting to `reviewed`.
- Tours should cross-link to the Destination concepts published in PR2 (graph edges).
