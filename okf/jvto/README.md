# JVTO OKF Tools

This directory is the curation and validation layer for `../bundles/jvto/`.

- `config/`: upstream allow-list and publication rules.
- `sources/snapshots/`: local, uncommitted upstream inputs.
- `curation/approved/`: human-reviewed YAML records converted into public concepts.
- `scripts/`: fetch, build, index, and validation tools.
- `docs/`: architecture and operating procedures.

The public artifact is `../bundles/jvto/`. It must be self-contained and readable without this tooling directory.
