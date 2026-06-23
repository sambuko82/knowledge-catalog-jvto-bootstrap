# Merge Instructions

Copy these additive directories into the root of a checked-out `knowledge-catalog` repository:

```bash
cp -R /path/to/knowledge-catalog-jvto-bootstrap/okf/jvto ./okf/
cp -R /path/to/knowledge-catalog-jvto-bootstrap/okf/bundles/jvto ./okf/bundles/
cp /path/to/knowledge-catalog-jvto-bootstrap/.github/workflows/jvto-okf.yml ./.github/workflows/
```

Then run:

```bash
cd okf/jvto
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
python scripts/fetch_snapshots.py
python scripts/build_bundle.py --all
python scripts/validate_okf.py --strict-links
```

Do not run the release check until every generated candidate has been manually reviewed and its status changed to `reviewed` or `published`.
