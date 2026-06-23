# Architecture

## Repository placement

```text
knowledge-catalog/
└── okf/
    ├── bundles/
    │   └── jvto/                 # final public OKF bundle
    └── jvto/
        ├── config/               # upstream allow-list and release rules
        ├── curation/             # human-approved facts
        ├── docs/                 # process and data governance
        ├── scripts/              # fetch, build, validate
        ├── sources/snapshots/    # local-only upstream inputs
        └── build/                # local reports
```

## Data flow

```text
1. Fetch allow-listed snapshots
   └─ local only; no public publishing

2. Generate candidates
   └─ Tour Package and Policy records are automatically drafted (as
      generated_pending_review) when their upstream manifest reports clean

3. Curate manually
   └─ destinations, guides, trust, reviews, organization
      require public source verification

4. Validate
   └─ YAML, type, links, citations, public visibility, release status

5. Publish
   └─ commit only reviewed/public concepts under bundles/jvto
```

## Ownership

| Layer | Role | May publish a concept? |
|---|---|---|
| Upstream repos | provide candidate data | No |
| Snapshot fetcher | records reproducible local source state | No |
| Candidate builder | writes package and policy drafts | No |
| Human curator | checks current public sources | Yes |
| Validator | blocks invalid release | No |
| Knowledge Catalog / agents | consume concepts | No |

## Design decision

This is a **public knowledge product**, not a runtime software integration. A reader must be able to understand every public claim from the concept itself and its citations.
