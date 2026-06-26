# Goal and Boundaries

## Goal

Build a **clean, standalone, public JVTO knowledge bundle** at:

```text
knowledge-catalog/okf/bundles/jvto/
```

It must be useful to people, LLMs, search/indexing systems, and the Knowledge Catalog graph viewer **without needing access** to `llm-wiki`, `jvto-itinerary-core`, a private database, or API credentials.

## What it is

- Portable Markdown concepts with YAML frontmatter.
- Citation-led, factual, public-safe JVTO knowledge.
- A graph of organization, destinations, tours, policies, guides, trust facts, reviews, and references.

## What it is not

- Not a mirror of `llm-wiki`.
- Not a raw database export or source archive.
- Not a replacement for website or booking runtime data.
- Not an automatic sync of internal upstream content.

## Source relationship

```text
llm-wiki ──────────────┐
                        │ controlled local snapshots
itinerary-core ────────┼──> curation + public verification ──> JVTO OKF bundle
                        │                                      (knowledge-catalog)
public authority pages ┘
```

Authority flows in one direction — source knowledge and original evidence → the canonical OKF graph → the website (for presentation and future propagation):

1. **Canonical upstream knowledge** in `llm-wiki` / `jvto-itinerary-core` (the `source_refs` anchors) is the primary discovery basis.
2. **External reference sources** (direct platform, authority, partner, media, and registry URLs) support and refresh claims — for dynamic facts a direct observation is stronger than any copy. (The validator only tells a non-secondary URL from a website-host one; authority, relevance, and freshness come from a separate source-health review.)
3. The **JVTO website** (`javavolcano-touroperator.com`) is a *secondary* presentation and corroboration layer: useful for public context, hosted assets, cross-checking, and finding propagation gaps.
4. The website may **never override, erase, downgrade, or invalidate** a fact that is supported upstream merely because it is absent, incomplete, stale, or contradictory there. It may appear as supplementary context but is never the sole evidence for a claim (validator rule JVTO-18). Where the website lags the graph, that is a *publication propagation recommendation*, not an evidence failure.

## Non-negotiable boundary

Do not publish customer PII, internal commercial terms, raw financial data, private operational procedures, private source documents, secrets, raw credential scans, or claims that rely only on AI-generated material.
