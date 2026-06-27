# JVTO OKF Bootstrap for Knowledge Catalog

This is a clean additive starter for building a **public, standalone Java Volcano Tour Operator (JVTO) Open Knowledge Format (OKF) bundle** inside the `knowledge-catalog` repository.

It is intentionally **not** a copy of `llm-wiki` and it does not make `llm-wiki` a runtime dependency. The two upstream repositories are used only as controlled snapshot sources during curation:

- `sambuko82/llm-wiki` — package readiness, policy, trust, destination, and public-content candidates.
- `sambuko82/jvto-itinerary-core` — detailed operational route and itinerary context that may guide curation but is never copied automatically into the public bundle.

## Target location after merge

```text
knowledge-catalog/
└── okf/
    ├── bundles/
    │   └── jvto/              # final public, portable OKF bundle
    └── jvto/                  # curation tooling, source contracts, docs, snapshots
```

## Start here

1. Read `okf/jvto/docs/00-goal-and-boundaries.md`.
2. Read `okf/jvto/docs/01-source-to-output-map.md`.
3. Create a virtual environment in `okf/jvto/` and install dependencies.
4. Run `python scripts/fetch_snapshots.py` (remote). If an upstream is private
   or you are offline, use local clones instead:
   `JVTO_OKF_LOCAL_LLM_WIKI=/path/to/llm-wiki JVTO_OKF_LOCAL_ITINERARY_CORE=/path/to/jvto-itinerary-core python scripts/fetch_snapshots.py --local`.
5. Run `python scripts/build_bundle.py`.
6. Review generated package concepts. They are intentionally marked `generated_pending_review`.
7. Add verified, public-safe concepts using `curation/approved/*.yaml`.
8. Use `okf/jvto/skills/jvto-okf-verified-curation/SKILL.md` whenever a concept needs generation and claim-level verification in the same workflow.
9. Run `python scripts/validate_okf.py --strict-links`.
10. Only release after `python scripts/validate_okf.py --release --strict-links` passes.
11. Generate `viz.html` with `python scripts/visualize.py` (or `make viz`). This is the OKF visualize capability ported from Knowledge Catalog's reference agent; the output is git-ignored and regenerated on demand. See `okf/jvto/docs/09-okf-spec-conformance.md`.

## Merge into `knowledge-catalog`

Copy the two directories below into the existing `knowledge-catalog/okf/` directory:

```text
okf/jvto/
okf/bundles/jvto/
```

The bootstrap deliberately does not overwrite existing Knowledge Catalog source files, sample bundles, or the reference agent.

## Security boundary

Never commit snapshot files, raw database exports, PII, private vendor rates, operational cost details, internal customer chats, API secrets, or raw credential scans. `okf/jvto/sources/snapshots/` and `okf/jvto/build/` are gitignored except for their README/.gitkeep files.
