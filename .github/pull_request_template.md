<!-- OKF convergence/curation PRs must keep the sections below. Delete this comment. -->

## Summary

<!-- What changed and why. -->

## Validation

- [ ] `python -m unittest discover -s tests`
- [ ] `python scripts/build_bundle.py --curated --indexes` (no `okf/bundles/jvto` diff)
- [ ] `python scripts/validate_okf.py --strict-links` (0/0)
- [ ] `python scripts/validate_okf.py --release --strict-links` (0/0)

## Publication propagation recommendations

<!-- Required on every convergence loop. A downstream recommendation list only — no new concept,
folder, pipeline, or truth layer; no website change is made in this OKF PR unless explicitly
assigned. Write "none this loop" if empty. -->

- Canonical facts absent from the website:
- Canonical facts outdated or inconsistently represented there:
- Upstream-discovered data to recommend for later website publication:
