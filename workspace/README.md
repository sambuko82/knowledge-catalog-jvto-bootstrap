# JVTO OKF Audit Workspace

Draft, **non-public** audit artifacts from the cross-repo exploration in `workspace/CLAUDE.md`.
Nothing here is a public OKF concept; these files are never built into `okf/bundles/jvto/`.

> **Read `audit-reports/RE-BASELINE-NOTE.md` first.** This audit was re-done against the real
> `main` (`6e1a73c`, 46 concepts) after an initial pass ran on a stale 1-concept snapshot.

Generated 2026-06-25 with live web verification **and** an adversarial verification pass (18 agents).
Repos: `knowledge-catalog-jvto-bootstrap` (public bundle), `llm-wiki` (SSOT, input), `jvto-itinerary-core`
(operational intelligence, input).

## Contents
- `audit-reports/RE-BASELINE-NOTE.md` — what was stale and what changed (read first).
- `audit-reports/{repo-exploration,cross-repo-consistency,source-evidence,okf-optimization}-report.md`
- `evidence-ledger.yaml`, `okf-gap-register.md`, `optimization-proposals/priority-roadmap.md`
- `source-health/external-source-health.md` — live reachability + freshness (corrected).
- `candidate-*/` — `do_not_publish` drafts for deferred items.

## Evidence classes
`primary_public · official_first_party · independent_public · supporting_context · internal_only ·
sensitive · stale · conflicting · unreachable · insufficient`

## Actions
`report_only · recommend_evidence_research · recommend_source_refresh · recommend_new_reference ·
recommend_new_partner · recommend_new_concept · recommend_update_existing_concept ·
recommend_taxonomy_change · recommend_validator_change · recommend_test_change · do_not_publish`
