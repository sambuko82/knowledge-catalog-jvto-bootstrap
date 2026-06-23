# Integration Plan

## No upstream modification

This starter does not add a webhook, submodule, subtree, runtime API, or package dependency to `llm-wiki` or `jvto-itinerary-core`.

## Why snapshots are used

1. Public bundle generation is reproducible from explicit source files.
2. Upstream repositories can contain internal and non-public material.
3. A local snapshot manifest provides curation auditability.
4. Human verification is mandatory before public release.

## Future automation, only after stable curation

- Scheduled snapshot refresh can open a pull request, never auto-publish.
- Source hash changes can label affected candidate concepts.
- The existing Knowledge Catalog graph viewer can be committed as `viz.html` for human review.

## No consumer migration

- `jvto-web` keeps using its existing JSON contracts.
- `jvto-itinerary-core` keeps using generated intelligence JSON.
- `llm-wiki` stays an internal knowledge/compiler system.
- This bundle serves portable public knowledge to agents, graph tools, and future partner/discovery workflows.

## Snapshot failure behavior

If an upstream fetch fails, no public concept is changed. The fetcher records the failure in a local snapshot manifest and exits non-zero only when a required source could not be retrieved. This prevents stale cache or partial data from silently becoming a release input.
