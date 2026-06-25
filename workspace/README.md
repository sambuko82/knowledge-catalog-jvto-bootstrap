# JVTO OKF Audit Workspace

Draft, non-public audit artifacts produced by the cross-repo knowledge exploration described in
`workspace/CLAUDE.md`. **Nothing here is a public OKF concept.** Files in this directory are never
built into `okf/bundles/jvto/` and must not be merged into the public bundle automatically.

Generated: 2026-06-25. Repos audited:
- `knowledge-catalog-jvto-bootstrap` (this repo — public OKF bundle + curation tooling)
- `llm-wiki` (`e:\Users\JAVA VOLCANO\llm-wiki`) — knowledge SSOT, upstream input only
- `jvto-itinerary-core` (`d:\jvto-itinerary-core`) — operational intelligence, upstream input only

## Contents
- `audit-reports/` — the four required narrative reports.
- `evidence-ledger.yaml` — machine-readable claim/source ledger.
- `okf-gap-register.md` — enumerated gaps (GAP-OKF-NN).
- `optimization-proposals/priority-roadmap.md` — ranked execution roadmap.
- `source-health/` — live reachability + freshness snapshot of external sources.
- `candidate-partners/`, `candidate-references/`, `candidate-concepts/` — **draft** (`status: candidate`)
  artifacts seeding future verified-curation PRs. Public-safe fields only.

## Evidence classification scheme (from `workspace/CLAUDE.md`)
`primary_public` · `official_first_party` · `independent_public` · `supporting_context` ·
`internal_only` · `sensitive` · `stale` · `conflicting` · `unreachable` · `insufficient`

## Recommended-action vocabulary
`report_only` · `recommend_evidence_research` · `recommend_source_refresh` · `recommend_new_reference` ·
`recommend_new_partner` · `recommend_new_concept` · `recommend_update_existing_concept` ·
`recommend_taxonomy_change` · `recommend_validator_change` · `recommend_test_change` · `do_not_publish`
