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
| `published` | reviewed and intentionally released | Yes |
| `deprecated` | retained history, not active | No |

## Sensitive claims

Legal, medical, safety, credential, review-rating, or operational claims need an authoritative public citation and current verification date. Where facts conflict, do not publish a clean assertion.
