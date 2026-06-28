"""Validate a published Customer Sales Release.

Fails (non-zero exit) if any private/internal/PII field leaks, if a required file or
record field is missing, or if a published price lacks currency/tiers. Run in CI alongside
the OKF validators.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import OKF_ROOT, read_json

REQUIRED_FILES = [
    "package-profiles.json", "standard-price-tiers.json", "component-matrices.json",
    "endpoint-chains.json", "accommodation-rules.json", "vehicle-and-luggage-rules.json",
    "guide-support-rules.json", "policy-cards.json", "destination-guidance.json",
    "location-aliases.json", "coverage-report.json", "gap-report.json",
    "source-lock.json", "release-manifest.json",
]

# Anything that would mean supplier cost / margin / internal-ops / PII leaked into the release.
FORBIDDEN_SUBSTRINGS = (
    "driver_cost", "escort_cost", "supplier", "margin", "vendor", "profit",
    "backoffice_observed", "rate_idr", "cost_idr", "price_per_day", "per_day_rate",
    "customer_email", "customer_phone", "passport", "payment_reference",
    "api_key", "private_key",
)

PACKAGE_KEYED = [
    "package-profiles.json", "standard-price-tiers.json", "component-matrices.json",
    "endpoint-chains.json", "accommodation-rules.json", "vehicle-and-luggage-rules.json",
    "guide-support-rules.json",
]


def validate(out_dir: Path) -> dict:
    findings: list[str] = []

    for name in REQUIRED_FILES:
        if not (out_dir / name).exists():
            findings.append(f"missing release file: {name}")
    if findings:
        return {"status": "fail", "findings": findings}

    # Forbidden-content scan across the DATA objects (case-insensitive). The meta files
    # (manifest/coverage/gap/source-lock) legitimately DESCRIBE what is excluded, so they
    # are validated structurally below rather than by substring.
    meta_files = {"release-manifest.json", "coverage-report.json", "gap-report.json", "source-lock.json"}
    for name in REQUIRED_FILES:
        if name in meta_files:
            continue
        text = (out_dir / name).read_text(encoding="utf-8").lower()
        for needle in FORBIDDEN_SUBSTRINGS:
            if needle in text:
                findings.append(f"{name}: forbidden field/term present: {needle}")

    # Package-keyed records must carry package_key + release_id + readiness + source_evidence.
    for name in PACKAGE_KEYED:
        for rec in read_json(out_dir / name):
            if not rec.get("package_key"):
                findings.append(f"{name}: record missing package_key")
            if not rec.get("release_id"):
                findings.append(f"{name}: record missing release_id")
            if not rec.get("readiness"):
                findings.append(f"{name}: record missing readiness")
            if "source_evidence" not in rec:
                findings.append(f"{name}: record missing source_evidence")

    # Published prices must have currency + non-empty tiers + the published_standard marker.
    for rec in read_json(out_dir / "standard-price-tiers.json"):
        if rec.get("price_type") != "published_standard":
            findings.append(f"standard-price-tiers: {rec.get('package_key')} not marked published_standard")
        if not rec.get("currency"):
            findings.append(f"standard-price-tiers: {rec.get('package_key')} missing currency")
        if not rec.get("pax_tiers"):
            findings.append(f"standard-price-tiers: {rec.get('package_key')} has no pax_tiers")

    manifest = read_json(out_dir / "release-manifest.json")
    if manifest.get("customer_traffic_ready") is not False:
        findings.append("release-manifest: customer_traffic_ready must be false")

    lock = read_json(out_dir / "source-lock.json")
    if not lock.get("knowledge_catalog", {}).get("revision"):
        findings.append("source-lock: missing knowledge_catalog revision")
    if not lock.get("itinerary_core", {}).get("revision"):
        findings.append("source-lock: missing itinerary_core revision")

    return {"status": "pass" if not findings else "fail", "findings": findings,
            "release_id": manifest.get("release_id")}


def main() -> None:
    parser = argparse.ArgumentParser(prog="validate_customer_sales_release")
    parser.add_argument("--out", default=str(OKF_ROOT / "customer-sales-release" / "jvto"))
    args = parser.parse_args()
    result = validate(Path(args.out))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
