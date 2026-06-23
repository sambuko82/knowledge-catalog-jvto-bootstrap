# JVTO Concept Model

| Family | OKF `type` | Purpose | Default source route |
|---|---|---|---|
| Organization | `Organization` | Identifies JVTO and bundle entrypoint | manual public official pages |
| Destination | `Destination` | Visitor context for a physical place | official/public pages |
| Tour | `Tour Package` | One purchasable public route | controlled automation + review |
| Policy | `Policy` | Customer-facing rule | controlled automation + review |
| Guide | `Travel Guide` | Traveler preparation or planning | public source citations |
| Claim | `Trust Claim` | Bounded, verifiable assertion | public evidence only |
| Credential | `Credential` | Public verification path, not raw documents | authority page |
| Partner | `Partner` | Relevant public institutional relationship | partner page |
| Review | `Review Platform` | Public aggregate reputation | public profile and date |
| Reference | `Reference` | Reusable authoritative source | manual |

## Recommended frontmatter

```yaml
---
type: Tour Package
title: Human-readable title
description: One-sentence summary
resource: https://canonical-public-url.example
tags: [queryable, labels]
timestamp: "2026-06-23T00:00:00+07:00"

id: tours/from-surabaya/example
status: reviewed
visibility: public
last_verified: "2026-06-23"
---
```

OKF v0.1 requires only a non-empty `type`. This JVTO profile adds `id`, `status`, `visibility`, and `last_verified` so agents and reviewers can recognize ownership, freshness, and release safety.

## Link rule

Use bundle-relative standard Markdown links:

```markdown
[Ijen health screening](/travel-guides/ijen-health-screening.md)
```

Do not export Obsidian-only wikilinks.
