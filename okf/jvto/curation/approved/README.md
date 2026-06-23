This directory holds human-reviewed curation records. Add `*.yaml` files using
`../templates/concepts.example.yaml` after verifying every fact against the cited
public sources.

Only records with a release-eligible status are exported by the curated build step:
`reviewed`, `verified`, `qualified`, or `published`. Records marked `draft`,
`needs_review`, `generated_pending_review`, or `deprecated` are ignored. Every record
must carry its own `timestamp` — the build will not generate one.

Current records: `organization.yaml` (the Organization bundle entrypoint).
