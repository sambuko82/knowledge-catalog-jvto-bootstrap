# JVTO OKF Pipeline Blueprint

A single-page map of how the public JVTO Open Knowledge Format (OKF) bundle is
produced and kept safe. For step-by-step commands see
[03-operating-procedure.md](03-operating-procedure.md); for the concept schema
see [05-concept-model.md](05-concept-model.md).

## Goal

A self-contained, public-safe knowledge bundle at `okf/bundles/jvto/` that AI
agents, search tools, and the Knowledge Catalog visualizer can consume **without
any runtime access** to the private upstream repositories.

## Flow

```text
upstream snapshots        controlled extraction      curation              validation        release
(local clone or remote)   (gated, draft-only)        (human verified)      (8 rule classes)  (gate)
        │                         │                        │                      │              │
llm-wiki ─┐                 build_packages() ─┐      curation/approved/*.yaml     │              │
itinerary ┤─ fetch_snapshots ─► snapshots ──► build_policies() ─► drafts ─┐       ▼              ▼
          │   (allow-list +         (sha256 +  build_curated() ──► public  ├─► validate_okf.py ─► okf/bundles/jvto
          │    forbidden_prefixes)   commit)                       concepts │   (--strict-links    (reviewed/verified/
          └────────────────────────────────────────────────────────────────┘    [--release])      qualified/published)
```

## Stages

| Stage | Tool | Produces | Status of output |
|---|---|---|---|
| Snapshot | `scripts/fetch_snapshots.py` (`--local` / remote) | `sources/snapshots/` + `_snapshot_manifest.json` (mode, ref/commit, sha256) | local only, never published |
| Extract: tours | `build_bundle.py` `build_packages()` | `tours/from-{surabaya,bali}/<slug>.md` | `generated_pending_review` |
| Extract: policies | `build_bundle.py` `build_policies()` | `policies/<policy_id>.md` | `generated_pending_review` |
| Curate | `curation/approved/*.yaml` → `build_curated()` | any concept type | `reviewed` / `verified` / `qualified` / `published` |
| Index | `build_bundle.py` `build_indexes()` (release-eligible concepts only) | every `index.md` | n/a |
| Validate | `scripts/validate_okf.py` | `build/validation-report.json` | gate |

## Gates (what blocks bad data)

- **Source gate** — a generator runs only when its source `_manifest.json`
  reports a compatible `schema_version` and `clean: true`.
- **Boundary gate** — `fetch_snapshots.py` reads only allow-listed paths and
  refuses `forbidden_prefixes`, symlink escapes, and out-of-clone targets.
- **Draft gate** — all extracted concepts are `generated_pending_review`; only
  human curation produces release-eligible statuses.
- **Validation gate** — `validate_okf.py` enforces, per concept:
  frontmatter parse (OKF-01), required fields (JVTO-06), public visibility
  (JVTO-02), known status (JVTO-07), unique id (JVTO-08), a non-empty citations
  section with a public URL for material types (JVTO-04), verification metadata
  for `verified`/`qualified` concepts (JVTO-09), no forbidden terms (JVTO-05),
  internal links that resolve (OKF-03) and stay inside the bundle (JVTO-10),
  and — with `--release` — a release-eligible status (JVTO-03).

## Required frontmatter (every concept)

`type`, `title`, `description`, `tags`, `timestamp`, `id`, `status`. Material
types (Organization, Destination, Tour Package, Travel Guide, Policy, Trust
Claim, Credential, Review Platform) also require a `# Citations` section.

## Status lifecycle

`draft` → `generated_pending_review` → `needs_review` → **`reviewed` /
`verified` / `qualified` / `published`** (release-eligible) · `deprecated`
(retired). The full vocabulary and the release allow-list live in
`config/publication-rules.yaml`.

## Safety boundary

Never copy raw private files, customer data, operational costs, vendor rates,
margins, credential scans, secrets, or internal-only content into the bundle.
Snapshots and build reports are git-ignored; the bundle holds only durable,
publicly verifiable knowledge.
