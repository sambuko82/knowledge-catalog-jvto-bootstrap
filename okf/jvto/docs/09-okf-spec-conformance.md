# 09 — OKF Spec Conformance

This document states how the JVTO bundle relates to the **Open Knowledge
Format (OKF) v0.1** specification published in the upstream
`knowledge-catalog` repository (`okf/SPEC.md`), and how JVTO's additional
governance fields fit within it. It complements
[`05-concept-model.md`](05-concept-model.md) (JVTO's concept model) and
[`08-okf-pipeline-blueprint.md`](08-okf-pipeline-blueprint.md) (the build
pipeline).

## JVTO is a conformant OKF v0.1 producer

A bundle is conformant with OKF v0.1 (SPEC §9) if:

1. Every non-reserved `.md` file has a parseable YAML frontmatter block.
2. Every frontmatter block has a non-empty `type` field.
3. Reserved files (`index.md`, `log.md`) follow the index/log structure.

The JVTO bundle in `okf/bundles/jvto/` satisfies all three. `type` is one of
the JVTO `known_concept_types` (Organization, Destination, Tour Package,
Travel Guide, Policy, Trust Claim, Credential, Partner, Reference, Review
Platform, Person), and `index.md` / `log.md` are reserved (never used for
concepts) — this is enforced by `validate_okf.py` (rules `OKF-01`, `JVTO-17`)
and by `RESERVED_FILENAMES` in `scripts/common.py`.

The shared `scripts/okf_core.py` module provides the same minimal
`OKFDocument` parse/serialize/validate contract as the upstream reference
agent, so JVTO concepts round-trip through standard OKF tooling.

## JVTO frontmatter as OKF extensions

OKF v0.1 (SPEC §4.1) treats every key beyond `type` as optional and says
"Producers MAY include any additional keys. Consumers SHOULD preserve unknown
keys … and SHOULD NOT reject documents with unrecognized fields." JVTO relies
on this extension model. The mapping:

| Frontmatter key | OKF status | JVTO meaning |
| --- | --- | --- |
| `type` | **Required** (SPEC §4.1) | One of the JVTO `known_concept_types`. |
| `title` | Recommended | Human-readable concept name. |
| `description` | Recommended | One-line summary used in `index.md`. |
| `tags` | Recommended | Cross-cutting labels. |
| `timestamp` | Recommended | ISO 8601 last-meaningful-change time. |
| `resource` | Recommended | Canonical public URL for the concept. |
| `id` | **Extension** | Stable lowercase URL-safe concept id (governs the file path). |
| `status` | **Extension** | Publication lifecycle: `draft` → `needs_review` → `reviewed` / `qualified` / `verified` → `published` (and `deprecated`). Only release-eligible statuses are exported. |
| `visibility` | **Extension** | `public` or `public_sensitive`. |
| `last_verified` | **Extension** | Date a source was actually checked (required on `qualified` / `verified`). |
| `source_refs` | **Extension** | Provenance anchors (`source_id`, `repo`, `path`, `source_class`, `captured_at`). |
| `citations` | **Extension** | Public HTTPS source URLs, rendered into a `# Citations` section. |
| `observations`, `activity`, `commercial_context`, `relationship_type`, `claim_basis` | **Extension** | Domain-specific governed fields. |

These extensions are additive: a generic OKF consumer ignores them and still
reads every concept correctly, while JVTO's `validate_okf.py` enforces the
extra rules (`JVTO-02`..`JVTO-19`) on top of OKF conformance. The JVTO bundle
is therefore a **strict subset producer**: it never relaxes an OKF rule, only
adds governance.

## Conventional sections

OKF (SPEC §4.2, §8) defines `# Schema`, `# Examples`, and `# Citations` as
conventional headings. JVTO uses `# Citations` as specified and adds its own
conventional sections governed by `CLAUDE.md` — most importantly the
`# Claim Boundary` section required on every Partner and Reference concept.
These are ordinary markdown headings and remain OKF-conformant.

## Cross-linking

JVTO uses OKF **bundle-relative absolute links** (SPEC §5.1), e.g.
`[Kawah Ijen](/destinations/kawah-ijen.md)`, which is the recommended form
because it is stable when documents move within a subdirectory. Obsidian
wikilinks are prohibited (`CLAUDE.md`, Link Rules). The new
`scripts/visualize.py` resolves exactly these links into graph edges.

## `okf_version`

OKF v0.1 (SPEC §11) allows a bundle to declare the version it targets via
`okf_version: "0.1"` in the **bundle-root `index.md` frontmatter** — the only
place frontmatter is permitted in an `index.md`.

The JVTO bundle targets **OKF v0.1** and declares it. `build_bundle.py:
build_indexes()` emits

```yaml
---
okf_version: "0.1"
---
```

as the frontmatter of the bundle-root `index.md` (and only there — every other
`index.md` stays frontmatter-free, per SPEC §6). `validate_okf.py` skips
reserved files, so this declaration does not affect concept validation, and the
build stays idempotent (the string is static).

## Visualization

The bundle can be rendered as an interactive graph — the OKF "visualize"
capability from the upstream reference agent, ported here:

```bash
cd okf/jvto
python scripts/visualize.py          # writes ../bundles/jvto/viz.html
# or: make viz
```

The output is a single HTML file, coloured by concept `type`, with search,
type filtering, backlinks, and the concept body rendered in a detail panel. It
is generated on demand and is git-ignored (not committed) to keep the
published bundle to concepts and indexes; regenerate it any time from the
curated bundle.

Cytoscape.js and marked.js are loaded from a CDN, so the file is single-file
but not fully offline: the first render needs network access, and opening it
in an environment that blocks external CDNs shows a blank graph. This mirrors
the upstream reference agent's viewer. If a fully offline viewer is ever
required, vendor the two libraries into `scripts/viz_assets/` and inline them
the same way `viz.css` / `viz.js` are inlined.

## Consumption index (catalog.json)

`okf/bundles/jvto/catalog.json` is a derived, committed sidecar regenerated by
`build_bundle.py` alongside the indexes. It is **not** an OKF concept: OKF SPEC §3
defines a bundle as a tree of Markdown files, and a non-`.md` sidecar is simply
ignored by consumers that don't want it, per the permissive consumption model in
SPEC §9.

It contains only release-eligible concepts (the same filter as the generated
indexes), carries the same `okf_version: "0.1"`, and mirrors the bundle 1:1 — the
CI no-bundle-diff guard keeps it in sync because the build regenerates it
deterministically (sorted keys, no timestamps).

It exists so agents and search tools can load the full concept graph — ids,
types, titles, descriptions, statuses, tags, citations, and cross-link edges — in
a single fetch instead of crawling every Markdown file. This is the consumption
half of the producer→consumer OKF flow.

```json
{
  "okf_version": "0.1",
  "bundle": "jvto",
  "concept_count": <int>,
  "type_counts": { "<type>": <int>, ... },
  "concepts": [ { "id","path","type","title","description","status","visibility","last_verified","tags","resource","citations","links_to" } ],
  "edges": [ { "source","target" } ]
}
```
