# JVTO OKF Tools

This directory is the curation and validation layer for `../bundles/jvto/`.

- `config/`: upstream allow-list and publication rules.
- `sources/snapshots/`: local, uncommitted upstream inputs.
- `curation/approved/`: human-reviewed YAML records converted into public concepts.
- `scripts/`: fetch, build, index, validation, and visualization tools.
- `docs/`: architecture and operating procedures.

The public artifact is `../bundles/jvto/`. It must be self-contained and readable without this tooling directory.

## Visualizing the bundle

Render the bundle as an interactive graph (the OKF "visualize" capability, ported from the upstream reference agent):

```bash
python scripts/visualize.py    # writes ../bundles/jvto/viz.html
# or: make viz
```

The output is a single self-contained HTML file (Cytoscape.js graph, coloured by concept type, with search, type filtering, backlinks, and a markdown detail panel). It is generated on demand and git-ignored. See [`docs/09-okf-spec-conformance.md`](docs/09-okf-spec-conformance.md) for how JVTO maps onto OKF v0.1.

## Verified curation skill

Use [`skills/jvto-okf-verified-curation/SKILL.md`](skills/jvto-okf-verified-curation/SKILL.md) whenever a public OKF concept needs to be generated and verified in one workflow. It produces the concept plus a separate claim-level verification report before release.
