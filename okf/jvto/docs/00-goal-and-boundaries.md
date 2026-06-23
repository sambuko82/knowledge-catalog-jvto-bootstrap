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

Upstream repositories identify candidates and structure. Current public sources remain the final authority for published concepts.

## Non-negotiable boundary

Do not publish customer PII, internal commercial terms, raw financial data, private operational procedures, private source documents, secrets, raw credential scans, or claims that rely only on AI-generated material.
