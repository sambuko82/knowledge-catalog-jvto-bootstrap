# Source → Action → Result → Storage Map

| Source | Extracted information | Next action | Result | Storage | Publication rule |
|---|---|---|---|---|---|
| `llm-wiki/output/products/package-readiness/_manifest.json` | schema version, `clean`, hashes | Build gate checks it first | permission to process package files | local snapshot only | never a public concept |
| `llm-wiki/.../package-registry.json` | package ID, origin, title, duration, URL, route flags | Generate one package candidate per record | Tour Package Markdown | `okf/bundles/jvto/tours/...` | `generated_pending_review` |
| `llm-wiki/.../package-itineraries.json` | day titles | Add itinerary outline to candidate | package itinerary summary | same Tour Package concept | human review required |
| `llm-wiki/.../package-pricing.json` | tier existence, currency, ferry indicator | give reviewer context only | no price auto-published | local snapshot only | current public page review required |
| `llm-wiki/.../booking-compatibility.json` | booking mode flags | add review note only | booking language candidate | same Tour Package concept | human review required |
| `llm-wiki/.../policy-bundle/*.json` | policy wording and consumer logic | check against current public policy pages | Policy concepts | `okf/bundles/jvto/policies/` | manual only |
| `llm-wiki/.../trust-bundle/claims.json` | claim/evidence candidate graph | verify each public proof source | Trust Claim / Credential concepts | `okf/bundles/jvto/trust/` | manual only |
| `llm-wiki/wiki/destinations/*.md` | aliases, content coverage, source leads | verify official/public sources | Destination concepts | `okf/bundles/jvto/destinations/` | manual only |
| `itinerary-core/.../manifest.json` | data maturity and gaps | decide whether a public topic is mature enough | curation checklist | local snapshot only | never public directly |
| `itinerary-core/.../route-leg-index.json` | route relations, feasibility context | check public itinerary accuracy | review evidence | local snapshot only | never public directly |
| `itinerary-core/.../operational-events.json` | event candidates | verify with a public current source | Travel Guide candidate | `okf/bundles/jvto/travel-guides/` | manual only |

## Why strict separation exists

`llm-wiki` is an internal knowledge system and `jvto-itinerary-core` is an operational intelligence layer. The public OKF bundle is narrower: only durable, shareable, and independently verifiable knowledge belongs in it.
