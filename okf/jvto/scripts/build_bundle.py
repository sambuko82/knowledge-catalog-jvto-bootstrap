#!/usr/bin/env python3
"""Build OKF candidates from controlled snapshots and human-approved curation records.

Generators:
  build_packages()  Tour Package drafts from the Package Readiness bundle.
  build_policies()  Policy drafts from the Policy Bundle.
  build_curated()   Public concepts from reviewed/verified curation records.

Generated drafts are always written as ``generated_pending_review`` and cannot
enter a release. Only curated records with a release-eligible status produce
public concepts. Indexes are regenerated on build and list only release-eligible
concepts. The bundle log (log.md) is not modified by the build.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from bundle_graph import build_catalog, walk_concepts
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

RELEASE_CURATION_STATUSES = {"reviewed", "verified", "qualified", "published"}
WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def snapshot(relative: str) -> Path:
    return SNAPSHOT_ROOT / "llm_wiki" / relative


def strip_wikilinks(text: str) -> str:
    """Convert Obsidian [[target|label]] / [[target]] to plain text (OKF link rule)."""
    return WIKILINK.sub(lambda m: (m.group(2) or m.group(1)).strip(), text)


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
    # Derive the concept timestamp from the source so repeated builds are idempotent.
    package_timestamp = str(manifest.get("generated_at") or utc_now())

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
            "tags": tags_for_package(row),
            "timestamp": package_timestamp,
            "id": cid,
            "status": "generated_pending_review",
            "visibility": "public",
            "generated_by": "okf/jvto/scripts/build_bundle.py",
            "source_snapshot": "llm_wiki/output/products/package-readiness",
            "source_manifest_schema": schema,
            "source_generated_at": manifest.get("generated_at"),
            "source_refs": [{
                "source_id": "SRC-PKG-READINESS",
                "repo": "sambuko82/llm-wiki",
                "path": "output/products/package-readiness/package-registry.json",
                "source_class": "operational_direct",
                "captured_at": manifest.get("generated_at"),
                "locator": package_id,
            }],
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
            ]
        )
        write_concept(cid, metadata, body)
        built.append(cid)
    return built


def build_policies() -> list[str]:
    """Generate Policy drafts from the Policy Bundle snapshot, if present and clean.

    Skips silently only when no policy snapshot is present at all, so package-only
    runs keep working. Once any policy snapshot file exists the manifest is
    mandatory and must report a compatible schema and ``clean: true`` (mirroring
    build_packages); a partial/failed fetch is treated as blocking rather than
    silently producing ungated drafts. Internal source paths are never printed;
    only customer-facing policy text (with Obsidian wikilinks flattened) reaches
    the public draft.
    """
    base = "output/website/policy-bundle"
    bundle_path = snapshot(f"{base}/policy-bundle.json")
    manifest_path = snapshot(f"{base}/_manifest.json")
    if not bundle_path.exists() and not manifest_path.exists():
        return []
    if not manifest_path.exists():
        raise RuntimeError("Policy Bundle manifest is missing; cannot verify the clean/schema gate.")
    if not bundle_path.exists():
        raise RuntimeError("Policy Bundle manifest present but policy-bundle.json is missing.")

    manifest = read_json(manifest_path)
    schema = str(manifest.get("schema_version", ""))
    if not manifest.get("clean"):
        raise RuntimeError("Policy Bundle manifest is not clean; candidate generation blocked.")
    if not schema.startswith("policy-bundle/v1"):
        raise RuntimeError(f"Unsupported Policy Bundle schema: {schema}")
    generated_at = manifest.get("generated_at")

    built: list[str] = []
    for policy in read_json(bundle_path):
        if not isinstance(policy, dict):
            continue
        policy_id = str(policy.get("policy_id", "")).strip()
        if not policy_id:
            continue
        cid = safe_concept_id(f"policies/{policy_id}")
        domain = str(policy.get("domain") or policy_id).strip()
        notes = str(policy.get("notes") or "").strip()
        consumers = [str(c).strip() for c in policy.get("consumers", []) if str(c).strip()]

        detail_lines: list[str] = []
        for evidence in policy.get("evidence", []):
            if not isinstance(evidence, dict):
                continue
            section = str(evidence.get("section") or "Detail").strip()
            content = strip_wikilinks(str(evidence.get("text") or "").strip())
            if not content:
                continue
            detail_lines.extend([f"## {section}", "", content, ""])
        if not detail_lines:
            detail_lines = ["No policy evidence text was present in this snapshot.", ""]

        tags = sorted({"policy", f"policy-{policy_id}"} | {f"consumer-{c}" for c in consumers})
        metadata = {
            "type": "Policy",
            "title": domain,
            "description": notes or f"{domain} policy for JVTO customers.",
            "tags": tags,
            "timestamp": str(generated_at or utc_now()),
            "id": cid,
            "status": "generated_pending_review",
            "visibility": "public",
            "generated_by": "okf/jvto/scripts/build_bundle.py",
            "source_snapshot": "llm_wiki/output/website/policy-bundle",
            "source_manifest_schema": schema,
            "source_generated_at": generated_at,
            "source_refs": [{
                "source_id": "SRC-POLICY-PACK",
                "repo": "sambuko82/llm-wiki",
                "path": "wiki/sources/jvto-policy-pack-v6.md",
                "source_class": "operational_direct",
                "captured_at": str(generated_at or ""),
                "locator": policy_id,
            }],
            "public_data_review_required": True,
        }
        body = "\n".join(
            [
                "# Overview",
                "",
                "This concept is a controlled draft generated from the LLM Wiki Policy Bundle. It is not release-ready until a reviewer verifies the current public policy page.",
                "",
                notes or f"{domain} policy.",
                "",
                "# Policy Detail",
                "",
                *detail_lines,
                "# Related Concepts",
                "",
                "- [All policies](/policies/index.md)",
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
            if not isinstance(record, dict) or str(record.get("status")) not in RELEASE_CURATION_STATUSES:
                continue
            cid = safe_concept_id(str(record.get("id", "")))
            if not str(record.get("timestamp", "")).strip():
                raise RuntimeError(
                    f"curation record '{cid}' in {file.name} is missing a required 'timestamp'; "
                    f"add an explicit ISO date so repeated builds stay idempotent."
                )
            body = str(record.get("body", "")).strip()
            citations = record.get("citations", [])
            if citations and "# Citations" not in body:
                body += "\n\n# Citations\n\n" + "\n".join(f"- {citation}" for citation in citations)
            metadata = {key: value for key, value in record.items() if key not in {"id", "body", "citations"}}
            metadata["id"] = cid
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
    folders = [BUNDLE_ROOT] + [item for item in BUNDLE_ROOT.rglob("*") if item.is_dir()]
    for folder in sorted(folders, key=lambda item: len(item.parts), reverse=True):
        relative = folder.relative_to(BUNDLE_ROOT)
        is_root = str(relative) == "."
        heading = "# Java Volcano Tour Operator — Knowledge Bundle" if is_root else "# " + relative.as_posix().replace("-", " ").title()
        lines = [heading, ""]
        if is_root:
            lines.extend([
                "Public, self-contained Open Knowledge Format bundle for JVTO. Each concept",
                "declares its own `type`, `status`, `tags`, `timestamp`, and citations so an",
                "agent can navigate progressively. Sections appear here only once they hold",
                "concepts.",
                "",
            ])
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
            # Only release-eligible concepts are presented as published knowledge.
            # Drafts/pending-review concepts are excluded from the public index.
            if meta and meta.get("status") in RELEASE_CURATION_STATUSES:
                concepts.append((child, meta))
        if concepts:
            lines.extend(["## Concepts", ""])
            for child, meta in concepts:
                lines.append(f"* [{meta.get('title', child.stem)}]({child.name}) - {meta.get('description', 'No description.')}")
            lines.append("")
        if not children and not concepts:
            lines.extend(["No reviewed concepts are published in this directory yet.", ""])
        if is_root:
            lines.extend([
                "## Reading Rules",
                "",
                "Check each concept's `status`, `last_verified`, and citations. Only `reviewed`,",
                "`verified`, `qualified`, or `published` concepts are release-eligible;",
                "`generated_pending_review` drafts cannot enter a public release.",
                "",
            ])
        content = "\n".join(lines)
        # OKF v0.1 (SPEC §11) permits a single `okf_version` declaration, and only
        # in the bundle-root index.md frontmatter. All other index files stay
        # frontmatter-free.
        if is_root:
            content = '---\nokf_version: "0.1"\n---\n\n' + content
        (folder / "index.md").write_text(content, encoding="utf-8")


def build_catalog_file() -> int:
    """Write the machine-readable consumption manifest (catalog.json).

    Walks the built bundle (release-eligible concepts only, matching the index
    policy so drafts never leak) and writes a deterministic JSON graph of all
    concepts and their cross-links, so AI agents and search tools can load the
    whole bundle in a single fetch. Regenerated whenever the indexes are.
    """
    concepts = walk_concepts(BUNDLE_ROOT, statuses=RELEASE_CURATION_STATUSES)
    catalog = build_catalog(concepts, okf_version="0.1", bundle="jvto")
    (BUNDLE_ROOT / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return len(concepts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packages", action="store_true")
    parser.add_argument("--policies", action="store_true")
    parser.add_argument("--curated", action="store_true")
    parser.add_argument("--indexes", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    default = not any((args.packages, args.policies, args.curated, args.indexes, args.all))
    packages = build_packages() if args.packages or args.all or default else []
    policies = build_policies() if args.policies or args.all or default else []
    curated = build_curated() if args.curated or args.all or default else []
    cataloged = 0
    if args.indexes or args.all or default:
        build_indexes()
        cataloged = build_catalog_file()
    write_json(
        BUILD_ROOT / "build-report.json",
        {
            "built_at": utc_now(),
            "package_candidates": packages,
            "policy_candidates": policies,
            "curated_concepts": curated,
            "cataloged_concepts": cataloged,
        },
    )
    print(
        f"Built {len(packages)} package candidate(s), {len(policies)} policy candidate(s), "
        f"and {len(curated)} curated concept(s); cataloged {cataloged} concept(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
