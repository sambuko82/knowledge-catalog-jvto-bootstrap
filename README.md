# JVTO OKF Bootstrap for Knowledge Catalog

A clean additive starter for building a **public, standalone Java Volcano Tour Operator (JVTO) Open Knowledge Format bundle** inside `knowledge-catalog`.

This starter deliberately does **not** copy, merge, or depend on `llm-wiki` at runtime. It uses controlled local snapshots from two upstream repositories only during curation:

- `sambuko82/llm-wiki`: package readiness plus policy, trust, destination, and travel-guide candidates.
- `sambuko82/jvto-itinerary-core`: operational route context used to review public itinerary language.

## Target placement

```text
knowledge-catalog/
└── okf/
    ├── bundles/jvto/     # final public, portable OKF bundle
    └── jvto/             # source contracts, local snapshots, curation and validation tools
```

## Start

1. Read `okf/jvto/docs/00-goal-and-boundaries.md`.
2. Read `okf/jvto/docs/01-source-to-output-map.md`.
3. Run the setup in `okf/jvto/docs/03-operating-procedure.md`.
4. Commit only the public bundle and reviewed curation records. Do not commit local snapshots or build reports.

## Delivery model

- `llm-wiki` and `jvto-itinerary-core` are **curation inputs**, not public sources of truth.
- Public concepts must link to current official JVTO pages, authority pages, partner pages, or public platform profiles.
- Generated package concepts are marked `generated_pending_review`; the release validator rejects them until a human changes them to `reviewed` or `published`.
