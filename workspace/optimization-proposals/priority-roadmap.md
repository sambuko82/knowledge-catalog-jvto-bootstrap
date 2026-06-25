# Priority Roadmap (corrected against real main `6e1a73c`)

**Date:** 2026-06-25. The bundle is mature and current; this is a small, high-confidence optimization
pass plus owner-decision items. Ordering: correctness → authority strengthening → empty families →
owner-gated → deferred.

## PR-A — audit + validator guard (`chore/okf-evidence-audit`)
1. Corrected `workspace/` audit (this directory) vs the real 46-concept bundle, incl. the re-baseline
   note and the 18 adversarial verdicts.
2. **JVTO-11** stale review-count guard (denylist 92/47 near a platform name) + 2 unit tests
   (stale blocked, current 123 passes). Defensive — bundle is clean today (GAP-07).
   *Docs/tooling only; no concept changes; preserves #8's Partner/Reference rule.*

## PR-B — concept accuracy + empty families (`feat/okf-concept-accuracy-and-graph`)
3. **Fix `kawah-ijen`** (GAP-01): correct the "summit 2,386 m" to rim-vs-summit wording; hedge
   "active". → status `qualified`.
4. **Upgrade `mount-bromo`** (GAP-02): add Smithsonian GVP citation → `verified`.
5. **Upgrade `madakaripura`** (GAP-03): add Probolinggo Regency tourism citation (tallest in Java) →
   `verified`.
6. **Fix `tumpak-sewu`** (GAP-04): "multi-tier" → "semicircular curtain (~120 m)" + independent cites.
7. **References family** (GAP-06): `references/official-website`, `references/google-maps-business-listing`
   (pointer, no count).
8. **Partners family** (GAP-05): `trust/partners/bbksda-jatim` (governing authority), `hpwki` (net-new),
   `isic` (directory). Hedged per the adversarial verdicts; cross-linked into the Ijen safety triangle.
9. Build `--curated --indexes`; `validate_okf.py --release --strict-links` = 0 errors; full test suite.

## Owner-decision items (surfaced, not changed)
- **GAP-09 (website):** refresh the live homepage Google count 92 → 123. Outside this repo.
- **GAP-08:** soften `verifiable-licenses` "BBKSDA clearance to operate" → "states that it holds…".
- **GAP-10:** keep Satusehat/AHU **deferred** (not publicly readable; PII). Do not publish.
- **GAP-11/12/13:** browser-confirm canonical TripAdvisor listing; model Facebook (timestamped);
  capture press exact URLs — then optional future PRs.

## Success criteria
1 factual correction, 2 authority upgrades, 1 wording fix, 2 new families (5 concepts), 1 defensive
validator. Bundle stays 100% current and safe; nothing `stale`/`conflicting`/`sensitive` is
introduced; release validation passes.
