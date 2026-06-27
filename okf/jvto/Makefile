PYTHON ?= python

fetch:
	$(PYTHON) scripts/fetch_snapshots.py

build:
	$(PYTHON) scripts/build_bundle.py --all

viz:
	$(PYTHON) scripts/visualize.py

validate:
	$(PYTHON) scripts/validate_okf.py --strict-links

release-check:
	$(PYTHON) scripts/validate_okf.py --release --strict-links

test:
	$(PYTHON) -m unittest discover -s tests -v
