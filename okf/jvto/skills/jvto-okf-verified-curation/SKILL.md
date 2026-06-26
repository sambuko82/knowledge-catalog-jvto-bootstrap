---
name: jvto-okf-verified-curation
description: Create a public-safe JVTO Open Knowledge Format concept and verify every material claim against approved upstream snapshots and current public primary sources before it can be released.
---

# JVTO OKF Verified Curation

## Purpose

Use this skill when a JVTO knowledge concept must be **generated and checked in the same workflow**.

The skill produces two outputs:

1. A candidate OKF concept for `okf/bundles/jvto/`.
2. A verification report that records every material claim, its evidence, freshness, publication safety, and release decision.

It prevents a recurring manual task: reviewing AI-written destination, tour, policy, trust, review, or travel-guide content after generation to determine whether it is factual, current, cited, and safe for the public OKF bundle.

## Core Rule

Do not publish a claim because it appears in an AI draft, `llm-wiki`, or `jvto-itinerary-core` alone.

- `llm-wiki` is an **internal knowledge candidate source**.
- `jvto-itinerary-core` is an **internal operational-detail candidate source**.
- Current public first-party or authoritative external sources are required for public factual claims whenever they are available.
- Conflicts, stale values, unsupported claims, internal-only facts, and personal data are excluded or blocked.

## When to Trigger

Trigger this skill for requests such as:

- "Create a verified OKF concept for Mount Ijen."
- "Add the current 3D2N Ijen–Bromo package to the JVTO knowledge bundle."
- "Write and verify a cancellation-policy concept."
- "Create a factual trust claim about JVTO's legal registration."
- "Update the Trustpilot concept with the latest public rating and review count."
- "Turn this public JVTO page into a clean OKF guide and verify it."
- "Review this generated concept before it is added to `knowledge-catalog`."

Do **not** trigger for:

- Internal route costing, vendor rates, margins, crew payment, customer records, booking details, raw WhatsApp conversations, secrets, or any data classified as PII.
- A request to copy an entire upstream repository or raw source into the public bundle.
- Marketing copy that intentionally does not claim factual accuracy; use a separate copywriting workflow.

## Required Inputs

- **Concept target**: destination, tour, policy, travel guide, trust claim, credential summary, review platform, partner, or organization.
- **Bundle path**: intended file path below `okf/bundles/jvto/`.
- **Public primary sources**: official JVTO page, authority page, partner registry, review-platform page, or reputable press source where relevant.
- **Upstream candidate sources**: permitted snapshots from `llm-wiki` and, where necessary, `jvto-itinerary-core`.

When the user does not give a path, derive it from the concept type:

| Concept type | Default path |
|---|---|
| Organization | `organization.md` |
| Destination | `destinations/<slug>.md` |
| Tour Package | `tours/from-surabaya/<slug>.md` or `tours/from-bali/<slug>.md` |
| Policy | `policies/<slug>.md` |
| Travel Guide | `travel-guides/<slug>.md` |
| Trust Claim | `trust/claims/<slug>.md` |
| Credential Summary | `trust/credentials/<slug>.md` |
| Partner | `trust/partners/<slug>.md` |
| Review Platform | `reviews/<slug>.md` |
| Reference | `references/<slug>.md` |

## Allowed Upstream Evidence

### From `sambuko82/llm-wiki`

Use only public-safe, curated, or validated material:

- `output/products/package-readiness/`
- `output/website/policy-bundle/`
- `output/website/trust-bundle/`
- `wiki/destinations/`
- `wiki/products/`
- `wiki/credentials/`
- `wiki/reviews/`
- `wiki/website/faq-master.md`
- `wiki/website/operational-facts.md`

Never ingest raw private files, raw customer records, secrets, or internal-only source material into the public bundle.

### From `sambuko82/jvto-itinerary-core`

Use only non-sensitive, supporting operational context:

- `generated/itinerary-intelligence/manifest.json`
- `generated/itinerary-intelligence/04-route-leg-index.json`
- `generated/itinerary-intelligence/06-destination-activity-profiles.json`
- `generated/itinerary-intelligence/07-operational-events.json`
- `generated/itinerary-intelligence/09-accommodation-logic.json`
- `generated/itinerary-intelligence/11-package-route-map.json`
- `generated/itinerary-intelligence/12-recommendation-rules.json`

Treat inferred, seed, manual calibration, historical aggregate, placeholder geometry, and low-sample fields as **supporting context only**, never as public final fact.

## Workflow

### 1. Scope and safety gate

Classify the requested concept as `public`, `public_sensitive`, `internal`, or `blocked`.

Block the request when it contains or requires:

- Customer PII or individual booking data.
- Internal vendor rates, margins, salaries, payment references, or operational secrets.
- Private medical documents, police documents, or credential scans.
- A claim that cannot be safely supported with public or authoritative evidence.

### 2. Gather candidate facts

Read the permitted upstream snapshots and extract only facts relevant to the requested concept.

Create a working fact list. For each item, record:

```text
claim_id
claim_text
upstream_source
source_path
source_status
source_date
visibility
candidate_public_source
```

Do not draft the final concept yet.

### 3. Verify each material claim

A material claim is any statement about:

- Legal identity, registration, credential, authority, partner, or regulation.
- Package availability, route, duration, price, inclusion, exclusion, booking path, or policy.
- Safety procedure, access rule, closure, medical screening, or escort condition.
- Rating, review count, award, press mention, staff credential, or operational capability.
- Current timetable, weather-related requirement, fee, capacity, or route feasibility.

For every material claim:

1. Find a primary public source or authoritative source.
2. Compare it with the upstream candidate source.
3. Check recency and identify whether the fact is dynamic.
4. Assign one status:
   - `verified` — source supports the exact claim.
   - `qualified` — source supports the claim only with narrower wording or a date qualifier.
   - `stale` — source is older than its freshness threshold or a newer source disagrees.
   - `conflict` — credible sources disagree.
   - `unsupported` — no adequate evidence found.
   - `internal_only` — true or useful, but unsuitable for a public bundle.
5. Decide the action:
   - include,
   - include_with_qualifier,
   - exclude,
   - block_for_human_decision.

### 4. Draft the OKF concept

Create a single UTF-8 Markdown concept with:

- YAML frontmatter containing at minimum `type`.
- Recommended fields: `title`, `description`, `resource`, `tags`, `timestamp`.
- JVTO extensions: `id`, `visibility`, `status`, `verified_at`, `source_status`.
- Structured markdown body using appropriate headings.
- Standard bundle-relative Markdown links such as `/destinations/kawah-ijen.md`.
- A `# Citations` section.

Use only facts marked `verified` or `qualified`. Every `qualified` fact must contain the relevant qualifier in the final wording.

### 5. Create the verification report

Write a separate internal report; do not place it inside the public bundle.

Default path:

```text
okf/jvto/build/verification/<concept-id>-verification.md
```

Use this structure:

```markdown
# Verification Report — <Concept Title>

## Decision

- Release status: `approved` | `approved_with_qualifiers` | `blocked`
- Verified at: <ISO 8601 timestamp>
- Reviewer mode: automated evidence comparison
- Human decision required: yes | no

## Claim Ledger

| # | Claim | Upstream candidate | Public/authority evidence | Status | Action |
|---|---|---|---|---|---|
| 1 | ... | ... | ... | verified | include |

## Excluded or Qualified Content

- ...

## Publication Propagation Recommendations

- Canonical facts absent from the website: ...
- Canonical facts outdated or inconsistently represented there: ...
- Upstream-discovered data to recommend for later website publication: ...

(The website is a secondary layer; a website gap is a propagation recommendation, never a reason to delete or downgrade a fact supported upstream. No website change is made in the OKF PR unless explicitly assigned. Write "none this loop" when there is nothing to recommend.)

## Safety Check

- PII: pass/fail
- Internal commercial data: pass/fail
- Unsupported legal/medical/safety claim: pass/fail
- Dynamic facts timestamped: pass/fail

## Release Rationale

...
```

### 6. Validate the bundle

Run the bundle validator after writing the concept:

```bash
cd okf/jvto && python scripts/validate_okf.py --strict-links
```

Verify:

- YAML frontmatter parses.
- `type` is present.
- `id` is unique and stable.
- Internal links use standard Markdown paths.
- Citation heading exists where the concept contains material facts.
- No forbidden internal or PII content appears.
- `status` is `verified` or `qualified`; never silently promote `generated_pending_review`.

### 7. Release decision

| Verification outcome | Public concept status | Next action |
|---|---|---|
| All material claims verified | `verified` | Update indexes and log; eligible for commit |
| Some claims require narrow wording | `qualified` | Include qualifiers; update indexes and log |
| Conflict or missing evidence | `blocked` | Do not add concept to public bundle; keep report only |
| Internal data only | No public concept | Keep out of bundle or route to a private system |

## Verification Step: Non-Negotiable Checklist

Before release, answer all questions below with **yes**:

1. Does each material factual claim have a current public or authoritative citation?
2. Does the citation support the exact wording, not merely a related topic?
3. Are dynamic facts—prices, review counts, access rules, dates, capacities—timestamped or excluded?
4. Did the final content exclude PII, internal commercial data, private documents, and secrets?
5. Did the concept avoid promoting inferred or seed operational data as fact?
6. Are any Ijen health-screening statements conditional where the current rule requires conditional wording?
7. Are all internal links standard Markdown links and not Obsidian wikilinks?
8. Did the validator pass after the concept and index update?
9. Does the verification report explicitly record excluded, stale, conflicted, or qualified claims?

If any answer is **no**, set release status to `blocked`.

## Output Contract

Return the following together:

1. **Generated concept** — ready to save at its bundle path only when approved.
2. **Verification report** — claim ledger and release decision.
3. **Concise verification summary** — verified claims, qualified claims, exclusions, and human decisions needed.
4. **Index/log changes** — exact entries required in the relevant `index.md` and `log.md`.
5. **Publication propagation recommendations** — canonical facts absent/outdated/inconsistent on the website and upstream-discovered data to recommend for later website publication ("none this loop" when empty). A downstream list only — never a reason to delete or downgrade an upstream-supported fact.

Never return only a polished answer without the verification result.

## Tooling Needed

### Required

| Tool | Why it is needed |
|---|---|
| GitHub repository access | Read exact, versioned upstream snapshots from `llm-wiki`, `jvto-itinerary-core`, and `knowledge-catalog`; inspect commit paths and update the JVTO bundle. |
| Web browser/search | Verify current public facts against official JVTO pages, authorities, partners, review platforms, and public press pages. |
| Local filesystem + Python | Create Markdown concepts, produce verification reports, run `validate_okf.py`, and generate a clean diff. |
| Git | Review the final diff, retain provenance, and commit only approved public concepts. |

### Strongly Recommended

| Tool | Why it improves accuracy |
|---|---|
| Public-source freshness checker | Detect whether public pages, policy pages, review counts, or authority notices changed after the latest verification. |
| Link checker | Detect broken public citations and broken bundle-relative links before publication. |
| YAML/frontmatter linter | Prevent malformed concept metadata. |
| OKF visualizer | Generate `viz.html` to inspect graph relations, orphan concepts, and missing backlinks. |

### Optional

| Tool | When useful |
|---|---|
| Google Drive / document connector | When verified public-ready source documents are stored outside GitHub. |
| Screenshot/PDF reader | When an official authority source is a PDF or scanned document and the claim depends on tables, diagrams, or images. |

## Examples

### Example 1 — Verified destination concept

**Request:** “Create a verified OKF concept for Kawah Ijen.”

**Expected behavior:**

- Read permitted destination material in `llm-wiki`.
- Verify current JVTO destination page and relevant authority/public guidance.
- Draft `okf/bundles/jvto/destinations/kawah-ijen.md`.
- Use conditional wording for health-screening information unless the current authoritative source supports a stricter claim.
- Produce `okf/jvto/build/verification/destinations-kawah-ijen-verification.md`.
- Block publication if the access-rule source cannot be verified.

### Example 2 — Current review platform concept

**Request:** “Update the JVTO Trustpilot concept.”

**Expected behavior:**

- Read prior internal review candidate data.
- Check the live Trustpilot profile.
- Include only the rating, count, profile URL, and date checked.
- Exclude individual reviewer data unless separately approved and demonstrably public-safe.
- Mark the concept `verified` only when the current profile supports the number.

### Example 3 — Tour package concept

**Request:** “Add the 3D2N Ijen–Bromo–Madakaripura package.”

**Expected behavior:**

- Read the package registry, pricing, itinerary, and booking compatibility snapshots.
- Confirm the live package URL and public route content.
- Omit internal COGS, actual margins, vehicle cost, and operational seed assumptions.
- Add package-to-destination and package-to-policy links.
- Generate a verification report for duration, route, inclusions, booking path, and Ijen wording.

## Quality Bar

A high-quality output is:

- Clean enough to publish in a public repository.
- Self-contained enough for a new agent to understand without `llm-wiki`.
- Conservative enough that uncertain facts are excluded rather than polished into false confidence.
- Traceable enough that a future reviewer can see why every important statement was included.
