# Data Safety and Release Policy

## Public-safe data

- Published package title, duration, start location, public URL.
- Current customer-facing policy summaries.
- Travel guidance backed by public authority or official JVTO pages.
- Public partner, press, and review-platform references.
- Review aggregates with an `as_of` or `last_verified` date.
- Public verification metadata that does not expose sensitive documents.

## Prohibited data

- Customer names, contacts, payments, passports/KTP, or medical details.
- Raw CRM chats, booking attachments, identifiable itineraries.
- Vendor contracts, internal costs, margin, crew pay, debt.
- API keys, tokens, database exports, secrets.
- Raw scans of police, medical, or personal credentials.
- Claims that have only AI-generated evidence.

## Release statuses

| Status | Meaning | Public release? |
|---|---|---|
| `draft` | manually started | No |
| `generated_pending_review` | script-generated candidate | No |
| `needs_review` | stale, conflicting, or unsupported | No |
| `reviewed` | human verified against citations | Yes |
| `verified` | all material claims verified against public evidence | Yes |
| `qualified` | released with narrower wording where evidence is limited | Yes |
| `published` | reviewed and intentionally released | Yes |
| `deprecated` | retained history, not active | No |

These are the canonical statuses; the machine-checked source of truth is
`config/publication-rules.yaml` (`known_statuses` and `allowed_statuses_for_release`).

## Sensitive claims

Legal, medical, safety, credential, review-rating, or operational claims need an authoritative public citation and current verification date. Where facts conflict, do not publish a clean assertion.

## Authority hierarchy and the website's role

Evidence authority runs in one direction — source knowledge and original evidence → the canonical OKF graph → the website:

1. **Canonical upstream knowledge** in `llm-wiki` / `jvto-itinerary-core` (`source_refs`) is the primary basis.
2. **External primary sources** (platform, authority, partner, media, registry URLs) support and refresh claims; for dynamic facts a direct observation outranks any copy.
3. The **JVTO website** is a *secondary* presentation and corroboration layer.
4. The website may **never** override, erase, downgrade, or invalidate a fact supported upstream because it is absent, incomplete, stale, or contradictory there.

Rule **JVTO-18** enforces the checkable half: the website may appear as supplementary context, but a concept that references the website must also carry a `source_refs` anchor or a non-website external primary URL — the website is never the sole evidence for a claim. The non-deletion half (a website gap is not grounds to remove or downgrade an upstream-supported fact) is governance: record the gap as a propagation recommendation instead.

## Publication propagation recommendations

Every convergence loop's final report includes a compact **publication propagation recommendations** section listing:

- canonical facts that are absent from the website;
- canonical facts that are outdated or inconsistently represented there;
- valuable data discovered upstream that should later be recommended for website publication.

This is a downstream recommendation list only — not a new concept, folder, pipeline, or truth layer. No website change is made in the OKF PR unless explicitly assigned.
