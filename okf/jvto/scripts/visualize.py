#!/usr/bin/env python3
"""Generate a single self-contained ``viz.html`` graph for the JVTO OKF bundle.

This is an additive port of the upstream ``knowledge-catalog`` reference
agent's ``viewer/generator.py`` (the ``reference-agent visualize`` command
referenced by this repo's README), adapted to the JVTO bundle:

- Concept colours use the JVTO ``known_concept_types`` palette.
- Cross-link edges resolve **bundle-relative absolute** links of the form
  ``[Kawah Ijen](/destinations/kawah-ijen.md)`` (the JVTO link convention),
  as well as ordinary relative ``./other.md`` links.
- Each node carries its publication ``status`` so the detail panel can show
  it.

The output is deterministic (it embeds only concept-derived data, no
timestamps), so re-running produces byte-identical HTML.

Usage::

    python scripts/visualize.py [--bundle PATH] [--out PATH] [--name NAME]

Defaults: ``--bundle`` is the JVTO bundle root, ``--out`` is
``<bundle>/viz.html``.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Allow ``python scripts/visualize.py`` from anywhere by making the script
# directory importable for the sibling modules.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from okf_core import OKFDocument, OKFDocumentError  # noqa: E402

_ASSET_DIR = Path(__file__).resolve().parent / "viz_assets"

# Colour per JVTO concept type (config/publication-rules.yaml: known_concept_types).
_TYPE_PALETTE = {
    "Organization": "#8b5cf6",
    "Destination": "#0ea5e9",
    "Tour Package": "#3b82f6",
    "Travel Guide": "#06b6d4",
    "Policy": "#f97316",
    "Trust Claim": "#22c55e",
    "Credential": "#16a34a",
    "Partner": "#eab308",
    "Reference": "#10b981",
    "Review Platform": "#ec4899",
    "Person": "#a855f7",
}
_DEFAULT_NODE_COLOR = "#94a3b8"


@dataclass
class Concept:
    id: str
    type: str
    title: str
    description: str
    resource: str
    status: str
    tags: list[str]
    body: str
    links_to: list[str] = field(default_factory=list)

    def to_node(self) -> dict[str, Any]:
        color = _TYPE_PALETTE.get(self.type, _DEFAULT_NODE_COLOR)
        return {
            "data": {
                "id": self.id,
                "label": self.title or self.id,
                "type": self.type,
                "status": self.status,
                "description": self.description,
                "resource": self.resource,
                "tags": self.tags,
                "color": color,
                "size": 30 + min(60, len(self.body) // 200),
            }
        }


def _extract_links(body: str, doc_dir: Path, bundle_root: Path) -> list[str]:
    """Return concept ids that ``body`` links to.

    Handles both JVTO bundle-relative absolute links (``/a/b.md``) and
    ordinary relative links (``./b.md``). External URLs and anchors are
    ignored. The resolved id has its ``.md`` suffix removed.
    """
    import re

    link_re = re.compile(r"\]\(([^)\s]+\.md)(?:#[A-Za-z0-9_\-]*)?\)")
    out: list[str] = []
    seen: set[str] = set()
    bundle_root_resolved = bundle_root.resolve()
    for m in link_re.finditer(body):
        target = m.group(1)
        if "://" in target:
            continue
        if target.startswith("/"):
            # Bundle-relative absolute link: strip the leading slash and .md.
            rel = target[1:]
            rel = rel[:-3] if rel.endswith(".md") else rel
        else:
            # Relative link: resolve against the document's directory.
            try:
                resolved = (doc_dir / target).resolve().relative_to(bundle_root_resolved)
            except ValueError:
                continue
            rel = resolved.as_posix()
            rel = rel[:-3] if rel.endswith(".md") else rel
        if rel and rel not in seen:
            seen.add(rel)
            out.append(rel)
    return out


def _walk_concepts(bundle_root: Path) -> list[Concept]:
    concepts: list[Concept] = []
    for md_path in sorted(bundle_root.rglob("*.md")):
        if md_path.name in common.RESERVED_FILENAMES:
            continue
        rel = md_path.relative_to(bundle_root).with_suffix("")
        concept_id = "/".join(rel.parts)
        try:
            doc = OKFDocument.parse(md_path.read_text(encoding="utf-8"))
        except OKFDocumentError:
            continue
        fm = doc.frontmatter or {}
        tags = fm.get("tags") or []
        if not isinstance(tags, list):
            tags = [str(tags)]
        concepts.append(
            Concept(
                id=concept_id,
                type=str(fm.get("type") or "Unknown"),
                title=str(fm.get("title") or concept_id),
                description=str(fm.get("description") or ""),
                resource=str(fm.get("resource") or ""),
                status=str(fm.get("status") or ""),
                tags=[str(t) for t in tags],
                body=doc.body or "",
                links_to=_extract_links(doc.body or "", md_path.parent, bundle_root),
            )
        )
    return concepts


def _build_graph(concepts: list[Concept]) -> dict[str, Any]:
    ids = {c.id for c in concepts}
    nodes = [c.to_node() for c in concepts]
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str]] = set()
    for c in concepts:
        for target in c.links_to:
            if target == c.id or target not in ids:
                continue
            key = (c.id, target)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append(
                {"data": {"id": f"{c.id}__{target}", "source": c.id, "target": target}}
            )
    bodies = {c.id: c.body for c in concepts}
    types = sorted({c.type for c in concepts})
    return {
        "nodes": nodes,
        "edges": edges,
        "bodies": bodies,
        "types": types,
        "palette": _TYPE_PALETTE,
    }


def generate_visualization(
    bundle_root: Path,
    out_path: Path,
    *,
    bundle_name: str | None = None,
) -> dict[str, int]:
    """Walk a bundle and write a single self-contained HTML visualization.

    Returns counts: ``{'concepts': N, 'edges': M, 'bytes': K}``.
    """
    bundle_root = Path(bundle_root)
    out_path = Path(out_path)
    if not bundle_root.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle_root}")

    concepts = _walk_concepts(bundle_root)
    graph = _build_graph(concepts)
    template = (_ASSET_DIR / "viz.html").read_text(encoding="utf-8")
    css = (_ASSET_DIR / "viz.css").read_text(encoding="utf-8")
    js = (_ASSET_DIR / "viz.js").read_text(encoding="utf-8")
    name = bundle_name or bundle_root.resolve().name

    html = (
        template
        .replace("/*__VIZ_CSS__*/", css)
        .replace("/*__VIZ_JS__*/", js)
        .replace("__BUNDLE_NAME__", json.dumps(name))
        .replace("__BUNDLE_DATA__", json.dumps(graph, sort_keys=True))
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    return {
        "concepts": len(concepts),
        "edges": len(graph["edges"]),
        "bytes": len(html.encode("utf-8")),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundle",
        type=Path,
        default=common.BUNDLE_ROOT,
        help="Bundle root directory (default: the JVTO bundle).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output HTML path (default: <bundle>/viz.html).",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="JVTO",
        help="Display name shown in the viewer header (default: JVTO).",
    )
    args = parser.parse_args(argv)

    out_path = args.out or (args.bundle / "viz.html")
    result = generate_visualization(args.bundle, out_path, bundle_name=args.name)
    print(
        f"Wrote {out_path} — {result['concepts']} concept(s), "
        f"{result['edges']} edge(s), {result['bytes']} bytes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
