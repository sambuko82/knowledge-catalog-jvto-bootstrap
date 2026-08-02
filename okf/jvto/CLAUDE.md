# JVTO OKF Tooling Contract

Scope: `okf/jvto/` — the curation and build tooling for the public bundle at
`okf/bundles/jvto/`. This complements the repository-root `CLAUDE.md` (which
governs publication, status, and claim boundaries). Where they overlap, the
root contract wins.

## Golden rules
- **The bundle is derived, never hand-edited.** Edit concept sources only in
  `curation/approved/*.yaml`; generate Markdown only via
  `python scripts/build_bundle.py --curated --indexes`. Everything under
  `okf/bundles/jvto/` (concepts, every `index.md`, `catalog.json`) is build
  output — changing it by hand will be overwritten and will fail the CI
  no-bundle-diff guard.
- **Additive by default.** Prefer new modules over changing existing ones.
  Do **not** alter `validate_okf.py`'s rule set or `common.py`'s strict
  `parse_frontmatter` casually — `validate_okf.py`'s OKF-01 rule depends on
  `parse_frontmatter` *raising* on missing/unterminated frontmatter.
- **Builds are deterministic.** Generated artifacts must be byte-stable across
  runs (sorted keys, no embedded timestamps in published output). Curation
  records therefore require an explicit `timestamp`. Local build reports under
  `build/` are git-ignored and may be time-stamped.
- **Release-eligible only.** Only concepts with status `reviewed`, `verified`,
  `qualified`, or `published` are exported to indexes and `catalog.json`;
  `generated_pending_review` / `draft` / `needs_review` / `deprecated` never
  reach published output.

## Scripts
- `fetch_snapshots.py` — pull allow-listed upstream files into the git-ignored
  `sources/snapshots/` (boundary- and symlink-checked).
- `build_bundle.py` — `build_packages()` / `build_policies()` (gated drafts),
  `build_curated()` (release concepts), `build_indexes()` (every `index.md`;
  root carries `okf_version: "0.1"`), `build_catalog_file()` (`catalog.json`).
- `validate_okf.py` — the 21-rule gate (`OKF-01`, `JVTO-02..21`; `JVTO-21` is
  warning-only); run with `--strict-links` and, for release,
  `--release --strict-links`.
- `visualize.py` — local `viz.html` graph (git-ignored, regenerate on demand).
- `bundle_graph.py` — shared concept-walk + graph model used by both
  `visualize.py` and `build_catalog`. `okf_core.py` — shared OKF
  document/path primitives (lenient parser; the strict gate stays in `common`).

Customer Sales Release (`okf/customer-sales-release/jvto/`) — a separate
publication artifact, NOT part of the no-diff-guarded bundle above:
- `build_customer_sales_release.py --core-root <jvto-itinerary-core>` — joins
  release-eligible concepts with itinerary-core operational/pricing facts into
  the 10 release objects + coverage/gap/source-lock/release-manifest.
- `validate_customer_sales_release.py` — content/leak gate on the committed
  files (missing files, malformed records, private/internal/PII leaks).
- `verify_customer_sales_release.py --core-root <jvto-itinerary-core>` —
  rebuild-and-diff reproducibility gate: checks the 7 core source SHAs + the
  OKF `catalog_sha256` against `source-lock.json`, then byte-compares the 12
  deterministic artifacts. CI runs it (`jvto-okf.yml`, GH_PAT-gated); run it
  locally with a core checkout pinned to `source-lock`'s revision.

## Derived bundle artifacts
- `index.md` (every directory) — progressive-disclosure listings; root declares
  `okf_version`.
- `catalog.json` (bundle root) — machine-readable consumption index: every
  release-eligible concept (id, type, title, description, status, tags,
  citations, links) plus cross-link edges and type counts, for single-fetch
  consumption by agents and search tools. See `docs/09-okf-spec-conformance.md`.

## Before every commit
```bash
cd okf/jvto
python -m unittest discover -s tests
python scripts/build_bundle.py --curated --indexes   # must leave no bundle diff
python scripts/validate_okf.py --strict-links            # 0 errors
python scripts/validate_okf.py --release --strict-links  # 0 errors
```

## Customer Sales Release — reproducibility sequence
`build_customer_sales_release.py` records `source-lock.json` `knowledge_catalog.revision` = `git rev-parse HEAD` and `catalog_sha256` = the working-tree catalog. **Build the release AFTER committing the curation+bundle**, so `revision` points at the catalog-bearing commit. Building *before* that commit records the parent revision (whose catalog differs), so a consumer checking out `revision` can't reproduce the release — `verify_customer_sales_release.py` hashes the current checkout and misses it (caught in review #36). Sequence when a concept changes: (1) commit `curation/` + `bundles/`; (2) `python scripts/build_customer_sales_release.py --core-root <core>`; (3) `python scripts/validate_customer_sales_release.py` then `python scripts/verify_customer_sales_release.py --core-root <core>`; (4) commit the release files. Core pin stays unless the itinerary-core source itself changed.
