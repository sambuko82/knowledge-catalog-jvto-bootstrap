# Operating Procedure

## Setup

Run inside `knowledge-catalog/okf/jvto/`:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
```

## 1. Refresh snapshots

```bash
python scripts/fetch_snapshots.py
```

The fetcher downloads only the paths allow-listed in `config/upstreams.yaml`. It writes a local manifest containing source URL, ref, fetch time, byte size, SHA-256, and fetch errors.

## 2. Generate package candidates

```bash
python scripts/build_bundle.py --packages
```

This runs only if Package Readiness reports a compatible schema and `clean: true`. Each package concept is written with `status: generated_pending_review`.

## 3. Add manually curated concepts

Copy and edit the template:

```bash
cp curation/templates/concepts.example.yaml curation/approved/destinations.yaml
```

Only add records after verifying every fact against the listed public citations. Use `reviewed` or `published` status.

## 4. Build curated concepts and indexes

```bash
python scripts/build_bundle.py --curated --indexes
```

## 5. Validate draft bundle

```bash
python scripts/validate_okf.py --strict-links
```

## 6. Validate release candidate

```bash
python scripts/validate_okf.py --release --strict-links
```

A release cannot contain `draft`, `needs_review`, or `generated_pending_review` concepts.

## 7. Generate graph

From `knowledge-catalog/okf/`:

```bash
python -m reference_agent visualize \
  --bundle ./bundles/jvto \
  --out ./bundles/jvto/viz.html \
  --name "Java Volcano Tour Operator"
```

## Update rule

When a public fact changes: update the underlying public page if appropriate, update the relevant concept, update `timestamp` and `last_verified`, add a `log.md` entry, validate, then commit.
