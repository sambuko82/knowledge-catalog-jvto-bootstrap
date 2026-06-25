#!/usr/bin/env python3
"""Validate the public JVTO OKF bundle and write a machine-readable local report.

Rules:
  OKF-01  frontmatter parses
  JVTO-06 required fields present (type, title, description, tags, timestamp, id, status)
  JVTO-02 visibility is public / public_sensitive
  JVTO-07 status is a known lifecycle value
  JVTO-03 (release) status is release-eligible
  JVTO-08 concept id is unique across the bundle
  JVTO-04 required-citation types carry a non-empty "# Citations" section with a public URL
  JVTO-09 verified/qualified concepts carry verification metadata (last_verified or verified_at)
  JVTO-05 no forbidden/sensitive terms
  JVTO-11 no known-stale review counts (config: stale_review_claims)
  JVTO-10 internal Markdown links stay inside the bundle (no escape)
  OKF-03  internal Markdown links resolve
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import BUNDLE_ROOT, BUILD_ROOT, RESERVED_FILENAMES, parse_frontmatter, read_yaml, utc_now, write_json

LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
URL = re.compile(r"https?://[^\s)]+")
NEXT_HEADING = re.compile(r"\n#\s")
DEFAULT_REQUIRED_FIELDS = ["type", "title", "description", "tags", "timestamp", "id", "status"]
VERIFICATION_FIELDS = ("last_verified", "verified_at")


def internal_target(source: Path, link: str) -> Path:
    if link.startswith("/"):
        return BUNDLE_ROOT / link.lstrip("/")
    return source.parent / link


def field_missing(meta: dict, field: str) -> bool:
    value = meta.get(field)
    if value is None:
        return True
    if field == "tags":
        return not isinstance(value, list) or len(value) == 0
    if isinstance(value, str):
        return not value.strip()
    return False


def citations_block(body: str) -> str | None:
    """Return the text of the '# Citations' section, or None if it is absent."""
    idx = body.find("# Citations")
    if idx == -1:
        return None
    after = body[idx + len("# Citations"):]
    nxt = NEXT_HEADING.search(after)
    return after[: nxt.start()] if nxt else after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--strict-links", action="store_true")
    args = parser.parse_args()
    rules = read_yaml(Path(__file__).resolve().parents[1] / "config" / "publication-rules.yaml")
    bundle_rules = rules.get("bundle", {})
    allowed = set(bundle_rules.get("allowed_statuses_for_release", []))
    known_statuses = set(bundle_rules.get("known_statuses", []))
    required_fields = bundle_rules.get("required_fields", DEFAULT_REQUIRED_FIELDS)
    forbidden = [str(item).lower() for item in rules.get("forbidden_public_terms", [])]
    citation_types = set(rules.get("required_citation_types", []))
    stale_review_claims = [c for c in rules.get("stale_review_claims", []) if isinstance(c, dict)]
    bundle_resolved = BUNDLE_ROOT.resolve()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen_ids: dict[str, str] = {}

    for path in sorted(BUNDLE_ROOT.rglob("*.md")):
        if path.name in RESERVED_FILENAMES:
            continue
        relative = path.relative_to(BUNDLE_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        try:
            meta, body = parse_frontmatter(text)
        except Exception as exc:  # noqa: BLE001
            errors.append({"rule": "OKF-01", "path": relative, "message": str(exc)})
            continue

        for field in required_fields:
            if field_missing(meta, field):
                errors.append({"rule": "JVTO-06", "path": relative, "message": f"Missing required field: {field}"})

        if meta.get("visibility", "public") not in {"public", "public_sensitive"}:
            errors.append({"rule": "JVTO-02", "path": relative, "message": "Non-public visibility in public bundle."})

        status = meta.get("status")
        if known_statuses and status not in known_statuses:
            errors.append({"rule": "JVTO-07", "path": relative, "message": f"Unknown status: {status!r}."})
        if args.release and status not in allowed:
            errors.append({"rule": "JVTO-03", "path": relative, "message": f"Release requires status in {sorted(allowed)}."})
        if status in {"verified", "qualified"} and all(field_missing(meta, f) for f in VERIFICATION_FIELDS):
            errors.append({"rule": "JVTO-09", "path": relative, "message": f"Status {status!r} requires verification metadata ({' or '.join(VERIFICATION_FIELDS)})."})

        concept_id = str(meta.get("id", "")).strip()
        if concept_id:
            if concept_id in seen_ids:
                errors.append({"rule": "JVTO-08", "path": relative, "message": f"Duplicate id {concept_id!r} (also in {seen_ids[concept_id]})."})
            else:
                seen_ids[concept_id] = relative

        if meta.get("type") in citation_types:
            block = citations_block(body)
            if not block or not URL.search(block):
                errors.append({"rule": "JVTO-04", "path": relative, "message": "Citations section is missing or has no public URL."})

        lower = text.lower()
        for term in forbidden:
            if term in lower:
                errors.append({"rule": "JVTO-05", "path": relative, "message": f"Forbidden term: {term}"})

        for claim in stale_review_claims:
            platform = str(claim.get("platform", "")).strip().lower()
            count = str(claim.get("count", "")).strip()
            if not platform or not count:
                continue
            esc_count, esc_platform = re.escape(count), re.escape(platform)
            window = (
                rf"\b{esc_count}\b[^\n]{{0,40}}\b{esc_platform}\b"
                rf"|\b{esc_platform}\b[^\n]{{0,40}}\b{esc_count}\b"
            )
            if re.search(window, lower):
                errors.append({
                    "rule": "JVTO-11",
                    "path": relative,
                    "message": f"Known-stale review value '{count}' near '{platform}'; refresh to the canonical count.",
                })

        for link in LINK.findall(body):
            if link.startswith(("https://", "http://", "mailto:", "#")):
                continue
            resolved = internal_target(path, link).resolve()
            if not resolved.is_relative_to(bundle_resolved):
                errors.append({"rule": "JVTO-10", "path": relative, "message": f"Internal link escapes the bundle: {link}"})
                continue
            if not resolved.exists():
                issue = {"rule": "OKF-03", "path": relative, "message": f"Broken internal link: {link}"}
                (errors if args.strict_links else warnings).append(issue)

    report = {
        "validated_at": utc_now(),
        "release_mode": args.release,
        "strict_links": args.strict_links,
        "errors": errors,
        "warnings": warnings,
        "clean": not errors,
    }
    write_json(BUILD_ROOT / "validation-report.json", report)
    print(f"Validation: {len(errors)} error(s), {len(warnings)} warning(s).")
    for issue in errors:
        print(f"ERROR {issue['rule']} {issue['path']}: {issue['message']}", file=sys.stderr)
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
