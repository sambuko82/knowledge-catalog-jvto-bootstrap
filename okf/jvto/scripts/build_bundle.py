#!/usr/bin/env python3
"""Build OKF candidates from controlled snapshots and human-approved curation records."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import (
    BUNDLE_ROOT,
    BUILD_ROOT,
    CURATION_ROOT,
    SNAPSHOT_ROOT,
    concept_path,
    parse_frontmatter,
    read_json,
    read_yaml,
    safe_concept_id,
    utc_now,
    write_json,
    write_yaml_frontmatter,
)

PUBLIC_BASE = "https://javavolcano-touroperator.com"


def snapshot(relative: str) -> Path:
    return SNAPSHOT_ROOT / "llm_wiki" / relative


def write_concept(concept_id: str, metadata: dict[str, Any], body: str) -> Path:
    target = concept_path(concept_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(write_yaml_frontmatter(metadata) + "\n" + body.strip() + "\n", encoding="utf-8")
    return target


def tags_for_package(row: dict[str, Any]) -> list[str]:
    text = " ".join(str(row.get(k, "")) for k in ("package_id", "slug", "origin")).lower()
    tags = {"tour-package", f"origin-{row.get('origin', 'unknown')}"}
    for token, tag in [
        ("ijen", "ijen"),
        ("bromo", "bromo"),
        ("tumpak", "tumpak-sewu"),
        ("papuma", "papuma"),
        ("madakaripura", "madakaripura"),
        ("malang", "malang"),
    ]:
        if token in text:
            tags.add(tag)
    if row.get("is_specialty"):
        tags.add("specialty")
    return sorted(tags)


def build_packages() -> list[str]:
    base = "output/products/package-readiness"
    manifest_path = snapshot(f"{base}/_manifest.json")
    if not manifest_path.exists():
        raise RuntimeError("Package Readiness snapshot is missing. Run fetch_snapshots.py first.")

    manifest = read_json(manifest_path)
    schema = str(manifest.get("schema_version", ""))
    if not manifest.get("clean"):
        raise RuntimeError("Package Readiness manifest is not clean; candidate generation blocked.")
    if not schema.startswith("package-readiness/v1"):
        raise RuntimeError(f"Unsupported Package Readiness schema: {schema}")

    registry = read_json(snapshot(f"{base}/package-registry.json"))
    itineraries = {str(x.get("package_id")): x for x in read_json(snapshot(f"{base}/package-itineraries.json"))}
    pricing = {str(x.get("package_id")): x for x in read_json(snapshot(f"{base}/package-pricing.json"))}
    compatibility = {str(x.get("package_id")): x for x in read_json(snapshot(f"{base}/booking-compatibility.json"))}
    built: list[str] = []

    for row in registry:
        package_id = str(row.get("package_id", "")).strip()
        slug = str(row.get("slug", "")).strip()
        origin = str(row.get("origin", "")).strip().lower()
        if not package_id or not slug or origin not in {"surabaya", "bali"}:
            continue

        cid = safe_concept_id(f"tours/from-{origin}/{slug}")
        public_path = str(row.get("public_url") or "").strip()
        resource = f"{PUBLIC_BASE}{public_path}" if public_path.startswith("/") else public_path
        itinerary = itineraries.get(package_id, {})
        titles = [
            str(day.get("title")).strip()
            for day in itinerary.get("days", [])
            if isinstance(day, dict) and str(day.get("title", "")).strip()
        ]
        itinerary_lines = [f"{number}. {title}" for number, title in enumerate(titles, 1)]
        if not itinerary_lines:
            itinerary_lines = ["No itinerary titles were present in this snapshot."]

        price = pricing.get(package_id, {})
        price_note = "No price is emitted automatically. Check the current public package page before publishing a price."
        if price.get("currency"):
            price_note = f"Snapshot currency: `{price['currency']}`. {price_note}"

        compat = compatibility.get(package_id, {})
        booking_lines = [
            f"- Snapshot value `{key}`: `{compat[key]}`."
            for key in ("instant_book", "whatsapp_assisted")
            if key in compat
        ] or ["- Booking handling must be checked on the live package page."]

        metadata = {
            "type": "Tour Package",
            "title": str(row.get("title") or slug),
            "description": f"Generated public candidate for {row.get('title') or slug}; must be reviewed against the live package page.",
            "resource": resource,
            "tags": tags_for_package(row),
            "timestamp": utc_now(),
            "id": cid,
            "status": "generated_pending_review",
            "visibility": "public",
            "generated_by": "okf/jvto/scripts/build_bundle.py",
            "source_snapshot": "llm_wiki/output/products/package-readiness",
            "source_manifest_schema": schema,
            "source_generated_at": manifest.get("generated_at"),
            "public_data_review_required": True,
        }
        body = "\n".join(
            [
                "# Overview",
                "",
                "This concept is a controlled draft generated from the LLM Wiki Package Readiness bundle. It is not release-ready until a reviewer verifies the current public package page.",
                "",
                f"- **Origin:** {origin.title()}",
                f"- **Duration:** {row.get('duration') or 'Not stated'}",
                f"- **Ijen relevant:** {bool(row.get('ijen_relevant'))}",
                f"- **Visits Madakaripura:** {bool(row.get('visits_madakaripura'))}",
                "",
                "# Itinerary Outline",
                "",
                *itinerary_lines,
                "",
                "# Booking and Pricing Review Notes",
                "",
                price_note,
                "",
                *booking_lines,
                "",
                "# Related Concepts",
                "",
                "- [All tours](/tours/index.md)",
                "- [Policies](/policies/index.md)",
                "",
                "# Citations",
                "",
                f"- {resource or 'Add the official public package URL during review.'}",
            ]
        )
        write_concept(cid, metadata, body)
        built.append(cid)
    return built


def build_curated() -> list[str]:
    built: list[str] = []
    for file in sorted(CURATION_ROOT.glob("*.yaml")):
        data = read_yaml(file)
        records = data.get("records", []) if isinstance(data, dict) else []
        for record in records:
            if not isinstance(record, dict) or str(record.get("status")) not in {"reviewed", "published"}:
                continue
            cid = safe_concept_id(str(record.get("id", "")))
            body = str(record.get("body", "")).strip()
            citations = record.get("citations", [])
            if citations and "# Citations" not in body:
                body += "\n\n# Citations\n\n" + "\n".join(f"- {citation}" for citation in citations)
            metadata = {key: value for key, value in record.items() if key not in {"id", "body", "citations"}}
            metadata["id"] = cid
            metadata.setdefault("timestamp", utc_now())
            metadata.setdefault("visibility", "public")
            write_concept(cid, metadata, body)
            built.append(cid)
    return built


def read_meta(path: Path) -> dict[str, Any] | None:
    try:
        return parse_frontmatter(path.read_text(encoding="utf-8"))[0]
    except Exception:
        return None


def build_indexes() -> None:
    for folder in sorted([item for item in BUNDLE_ROOT.rglob("*") if item.is_dir()], key=lambda item: len(item.parts), reverse=True):
        relative = folder.relative_to(BUNDLE_ROOT)
        heading = "# Java Volcano Tour Operator — Knowledge Bundle" if str(relative) == "." else "# " + relative.as_posix().replace("-", " ").title()
        lines = [heading, ""]
        children = [child for child in sorted(folder.iterdir()) if child.is_dir()]
        if children:
            lines.extend(["## Subdirectories", ""])
            for child in children:
                lines.append(f"* [{child.name.replace('-', ' ').title()}]({child.name}/index.md) - JVTO {child.name.replace('-', ' ')} concepts.")
            lines.append("")
        concepts = []
        for child in sorted(folder.glob("*.md")):
            if child.name in {"index.md", "log.md"}:
                continue
            meta = read_meta(child)
            if meta:
                concepts.append((child, meta))
        if concepts:
            lines.extend(["## Concepts", ""])
            for child, meta in concepts:
                lines.append(f"* [{meta.get('title', child.stem)}]({child.name}) - {meta.get('description', 'No description.')}")
            lines.append("")
        if not children and not concepts:
            lines.extend(["No reviewed concepts are published in this directory yet.", ""])
        if str(relative) == ".":
            lines.extend([
                "## Reading Rules",
                "",
                "Check each concept's `status`, `last_verified`, and citations. `generated_pending_review` concepts cannot enter a public release.",
                "",
            ])
        (folder / "index.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packages", action="store_true")
    parser.add_argument("--curated", action="store_true")
    parser.add_argument("--indexes", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    default = not any((args.packages, args.curated, args.indexes, args.all))
    packages = build_packages() if args.packages or args.all or default else []
    curated = build_curated() if args.curated or args.all or default else []
    if args.indexes or args.all or default:
        build_indexes()
    write_json(BUILD_ROOT / "build-report.json", {"built_at": utc_now(), "package_candidates": packages, "curated_concepts": curated})
    print(f"Built {len(packages)} package candidate(s) and {len(curated)} curated concept(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
