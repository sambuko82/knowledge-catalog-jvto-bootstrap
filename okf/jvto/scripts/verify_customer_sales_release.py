"""Verify the committed Customer Sales Release is reproducible from its declared sources.

This is the release analog of `build_bundle.py` -> `git diff --exit-code` (the bundle's
no-diff guard). It rebuilds the release from:
  - the CURRENT OKF catalog (okf/bundles/jvto/catalog.json in this checkout), and
  - a jvto-itinerary-core checkout pinned to the revision recorded in the committed
    source-lock.json (passed via --core-root),
and fails if any DETERMINISTIC artifact differs from what is committed. It catches a
hand-edited release, or an OKF concept change that was not propagated into the release.

Two files are excluded from the byte comparison because they legitimately change every
build and carry no customer-facing content:
  - source-lock.json     (created_at timestamp + knowledge_catalog.revision = the OKF git
                           HEAD; content is pinned by catalog_sha256, which IS compared)
  - release-manifest.json (created_at timestamp)

Before rebuilding, the 7 itinerary-core source files are checked against the SHA256s in
source-lock.json so a wrong --core-root revision fails with a clear message instead of a
confusing data-file diff.

Usage:
    python scripts/verify_customer_sales_release.py --core-root /path/to/jvto-itinerary-core
Exit 0 = reproducible; exit 1 = drift (rebuild + commit the release).
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

from common import OKF_ROOT, read_json
import build_customer_sales_release as builder

RELEASE_DIR = OKF_ROOT / "customer-sales-release" / "jvto"

# Deterministic outputs that MUST reproduce byte-for-byte (the 10 data objects + the two
# report files). source-lock.json / release-manifest.json are intentionally excluded.
DETERMINISTIC_FILES = [
    "package-profiles.json",
    "standard-price-tiers.json",
    "component-matrices.json",
    "endpoint-chains.json",
    "accommodation-rules.json",
    "vehicle-and-luggage-rules.json",
    "guide-support-rules.json",
    "policy-cards.json",
    "destination-guidance.json",
    "location-aliases.json",
    "coverage-report.json",
    "gap-report.json",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_source_lock(core_root: Path) -> list[str]:
    """Verify BOTH declared sources match source-lock.json: the 7 itinerary-core
    files (by SHA) AND the OKF catalog (by SHA). The catalog check matters because
    source-lock.json is excluded from the byte diff on the premise its content is
    pinned by catalog_sha256 — but a catalog-only change that doesn't touch the
    fields builder.build reads (e.g. catalog edges / non-release concept metadata)
    would leave source-lock stale while the data artifacts still reproduce. Fail
    here so a stale lock is caught rather than silently reported reproducible."""
    lock = read_json(RELEASE_DIR / "source-lock.json")
    findings: list[str] = []

    core = lock.get("itinerary_core", {})
    for rel, want in (core.get("sources") or {}).items():
        src = core_root / rel
        if not src.exists():
            findings.append(f"core source missing: {rel}")
            continue
        got = _sha256(src)
        if got != want:
            findings.append(
                f"core source SHA mismatch: {rel}\n"
                f"    expected {want} (source-lock pins itinerary_core@{core.get('revision', '?')[:12]})\n"
                f"    got      {got} — is --core-root at the pinned revision?"
            )

    kc = lock.get("knowledge_catalog", {})
    want_cat = kc.get("catalog_sha256")
    if want_cat:
        catalog = builder.BUNDLE_ROOT / "catalog.json"
        got_cat = _sha256(catalog) if catalog.exists() else None
        if got_cat != want_cat:
            findings.append(
                f"OKF catalog SHA mismatch: {catalog.name}\n"
                f"    expected {want_cat} (source-lock pins knowledge_catalog@{kc.get('revision', '?')[:12]})\n"
                f"    got      {got_cat or 'MISSING'} — the OKF catalog changed since the release was locked; "
                f"rebuild the release to refresh source-lock."
            )

    return findings


def main() -> None:
    parser = argparse.ArgumentParser(prog="verify_customer_sales_release")
    parser.add_argument("--core-root", required=True, help="Path to a jvto-itinerary-core checkout (pinned to source-lock's revision)")
    parser.add_argument("--release-id", default=builder.DEFAULT_RELEASE_ID)
    args = parser.parse_args()

    core_root = Path(args.core_root).resolve()
    if not RELEASE_DIR.exists():
        print(f"ERROR: committed release dir not found: {RELEASE_DIR}")
        sys.exit(1)

    lock_findings = _check_source_lock(core_root)
    if lock_findings:
        print("Customer Sales Release verification FAILED (source mismatch):")
        for f in lock_findings:
            print(f"  - {f}")
        sys.exit(1)

    # Rebuild into a temp dir seeded with a copy of the committed release, so the
    # hand-authored module-layer files (read by the build to populate the manifest) are
    # present and nothing in the working tree is touched.
    tmp = Path(tempfile.mkdtemp(prefix="csr-verify-"))
    try:
        shutil.copytree(RELEASE_DIR, tmp, dirs_exist_ok=True)
        built = builder.build(core_root, args.release_id)
        for name, payload in built["objects"].items():
            builder.write_json(tmp / name, payload)
        builder.write_json(tmp / "coverage-report.json", built["coverage"])
        builder.write_json(tmp / "gap-report.json", built["gap_report"])

        drifted = [name for name in DETERMINISTIC_FILES
                   if not filecmp.cmp(RELEASE_DIR / name, tmp / name, shallow=False)]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if drifted:
        print("Customer Sales Release verification FAILED — committed artifacts drifted from source:")
        for name in drifted:
            print(f"  - {name}")
        print(
            "\nThe committed release no longer matches a rebuild from its declared sources.\n"
            "Rebuild and commit:\n"
            "  python scripts/build_customer_sales_release.py --core-root <jvto-itinerary-core>\n"
        )
        sys.exit(1)

    print(f"Customer Sales Release reproducible ({len(DETERMINISTIC_FILES)} deterministic artifacts match) — {args.release_id}")


if __name__ == "__main__":
    main()
