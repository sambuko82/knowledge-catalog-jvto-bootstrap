#!/usr/bin/env bash
# Full OKF validation — run before commit and in CI. The lightweight per-edit hook
# (check-curation-yaml.py) is only a structural fast-check; this is the real gate.
#
# Usage:  .claude/hooks/validate-okf.sh
# Exits non-zero if tests, build, strict-link, or release validation fail.
#
# Live URL checks are intentionally NOT here: external reachability (CAPTCHA, bot
# protection, transient failures) belongs to a separate source-health process and
# must produce a warning record, not fail the build.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT/okf/jvto"

echo "==> unit tests"
python -m unittest discover -s tests

echo "==> build (curated + indexes)"
python scripts/build_bundle.py --curated --indexes

echo "==> strict-link validation"
python scripts/validate_okf.py --strict-links

echo "==> release validation"
python scripts/validate_okf.py --release --strict-links

echo "OKF validation passed."
