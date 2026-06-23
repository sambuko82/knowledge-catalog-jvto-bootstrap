#!/usr/bin/env python3
"""Validate the public JVTO OKF bundle and write a machine-readable local report."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import BUNDLE_ROOT, BUILD_ROOT, RESERVED_FILENAMES, parse_frontmatter, read_yaml, utc_now, write_json

LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def internal_target(source: Path, link: str) -> Path:
    if link.startswith("/"):
        return BUNDLE_ROOT / link.lstrip("/")
    return (source.parent / link).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--strict-links", action="store_true")
    args = parser.parse_args()
    rules = read_yaml(Path(__file__).resolve().parents[1] / "config" / "publication-rules.yaml")
    allowed = set(rules["bundle"]["allowed_statuses_for_release"])
    forbidden = [str(item).lower() for item in rules.get("forbidden_public_terms", [])]
    citation_types = set(rules.get("required_citation_types", []))
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

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
        if not str(meta.get("type", "")).strip():
            errors.append({"rule": "OKF-02", "path": relative, "message": "Missing type."})
        if not str(meta.get("id", "")).strip():
            errors.append({"rule": "JVTO-01", "path": relative, "message": "Missing stable id."})
        if meta.get("visibility", "public") not in {"public", "public_sensitive"}:
            errors.append({"rule": "JVTO-02", "path": relative, "message": "Non-public visibility in public bundle."})
        if args.release and meta.get("status") not in allowed:
            errors.append({"rule": "JVTO-03", "path": relative, "message": f"Release requires status in {sorted(allowed)}."})
        if meta.get("type") in citation_types and "# Citations" not in body:
            errors.append({"rule": "JVTO-04", "path": relative, "message": "Missing # Citations section."})
        lower = text.lower()
        for term in forbidden:
            if term in lower:
                errors.append({"rule": "JVTO-05", "path": relative, "message": f"Forbidden term: {term}"})
        for link in LINK.findall(body):
            if link.startswith(("https://", "http://", "mailto:", "#")):
                continue
            if not internal_target(path.resolve(), link).exists():
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
