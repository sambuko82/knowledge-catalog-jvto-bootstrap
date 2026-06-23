# Operating Procedure

## Setup

Run inside `knowledge-catalog/okf/jvto/`:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
```

## 1. Refresh snapshots

Remote mode (default) downloads only the paths allow-listed in
`config/upstreams.yaml` over `raw.githubusercontent.com`. It writes a local
manifest containing source URL, ref, fetch time, byte size, SHA-256, and fetch
errors.

```bash
python scripts/fetch_snapshots.py
```

Use **local mode** when an upstream must stay private (for example `llm-wiki`,
which holds non-public `raw/FINANCE/` data) or when working offline. It copies
the same allow-listed paths from local clones instead of downloading them, and
records each clone's HEAD commit for provenance. Point each upstream at its
clone with `JVTO_OKF_LOCAL_<KEY_UPPER>`:

```bash
export JVTO_OKF_LOCAL_LLM_WIKI=/path/to/llm-wiki
export JVTO_OKF_LOCAL_ITINERARY_CORE=/path/to/jvto-itinerary-core
python scripts/fetch_snapshots.py --local
```

Both modes enforce the same allow-list and `forbidden_prefixes` guard and write
the same snapshot layout, so the build and validate steps are identical.

## 2. Generate draft candidates (packages + policies)

```bash
python scripts/build_bundle.py --packages   # Tour Package drafts
python scripts/build_bundle.py --policies   # Policy drafts
# or both, plus curated concepts and indexes, in one pass:
python scripts/build_bundle.py --all
```

Each generator runs only if its source bundle reports a compatible schema and
`clean: true` (Package Readiness for `--packages`, the Policy Bundle for
`--policies`; policy generation is skipped silently when its snapshot is
absent). Every generated concept is written with
`status: generated_pending_review` and cannot enter a release until a reviewer
promotes it. Policy drafts flatten Obsidian wikilinks and never print internal
source paths.

## 3. Add manually curated concepts

Copy and edit the template:

```bash
cp curation/templates/concepts.example.yaml curation/approved/destinations.yaml
```

Only add records after verifying every fact against the listed public citations.
Use a release-eligible status: `reviewed`, `verified`, or `qualified` (the
verified-curation skill emits `verified`/`qualified`), or `published`.

## 4. Build curated concepts and indexes

```bash
python scripts/build_bundle.py --curated --indexes
```

## 5. Validate draft bundle

```bash
python scripts/validate_okf.py --strict-links
```

This checks frontmatter parsing, required fields (`type`, `title`, `description`,
`tags`, `timestamp`, `id`, `status`), a known status value, unique concept ids,
citation presence for material types, forbidden/sensitive terms, and internal
link resolution.

## 6. Validate release candidate

```bash
python scripts/validate_okf.py --release --strict-links
```

A release may contain only `reviewed`, `verified`, `qualified`, or `published`
concepts; `draft`, `needs_review`, and `generated_pending_review` are blocked.

## 7. Generate graph

From `knowledge-catalog/okf/`:

```bash
python -m reference_agent visualize \
  --bundle ./bundles/jvto \
  --out ./bundles/jvto/viz.html \
  --name "Java Volcano Tour Operator"
```

## Update rule

When a public fact changes: update the underlying public page if appropriate, update the relevant concept, update `timestamp` and `last_verified`, add a `log.md` entry, validate, then commit.
