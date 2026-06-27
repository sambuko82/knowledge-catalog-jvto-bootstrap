"""Shared bundle-walk and graph model for the JVTO OKF bundle.

This module centralizes the concept-walk, cross-link resolution, and graph
construction that both the interactive visualizer (``visualize.py``) and the
machine-readable consumption manifest (``build_bundle.build_catalog``) need, so
the two stay in lock-step and there is a single OKF graph model.

It uses the lenient ``okf_core.OKFDocument`` parser (a bundle viewer/index must
tolerate odd content), and leaves the strict frontmatter gate to
``validate_okf.py`` / ``common.parse_frontmatter`` — those are intentionally not
touched here.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

# Make sibling modules importable whether run as a script or imported by tests.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from okf_core import OKFDocument, OKFDocumentError  # noqa: E402

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

_LINK_RE = re.compile(r"\]\(([^)\s]+\.md)(?:#[A-Za-z0-9_\-]*)?\)")
_URL_RE = re.compile(r"https?://[^\s)]+")


@dataclass
class Concept:
    id: str
    type: str
    title: str
    description: str
    resource: str
    status: str
    visibility: str
    last_verified: str
    tags: list[str]
    citations: list[str]
    path: str
    body: str
    links_to: list[str] = field(default_factory=list)

    def color(self) -> str:
        return _TYPE_PALETTE.get(self.type, _DEFAULT_NODE_COLOR)

    def to_node(self) -> dict[str, Any]:
        return {
            "data": {
                "id": self.id,
                "label": self.title or self.id,
                "type": self.type,
                "status": self.status,
                "description": self.description,
                "resource": self.resource,
                "tags": self.tags,
                "color": self.color(),
                "size": 30 + min(60, len(self.body) // 200),
            }
        }


def extract_links(body: str, doc_dir: Path, bundle_root: Path) -> list[str]:
    """Return concept ids that ``body`` links to.

    Handles JVTO bundle-relative absolute links (``/a/b.md``) and ordinary
    relative links (``./b.md``, ``../b.md``). External URLs and anchors are
    ignored; the resolved id has its ``.md`` suffix removed.
    """
    out: list[str] = []
    seen: set[str] = set()
    bundle_root_resolved = bundle_root.resolve()
    for m in _LINK_RE.finditer(body):
        target = m.group(1)
        if "://" in target:
            continue
        if target.startswith("/"):
            rel = target[1:]
            rel = rel[:-3] if rel.endswith(".md") else rel
        else:
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


def _citation_urls(body: str) -> list[str]:
    """Return the http(s) URLs listed under a top-level ``# Citations`` section."""
    idx = body.find("# Citations")
    if idx == -1:
        return []
    after = body[idx + len("# Citations"):]
    nxt = re.search(r"\n#\s", after)
    section = after[: nxt.start()] if nxt else after
    out: list[str] = []
    seen: set[str] = set()
    for url in _URL_RE.findall(section):
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def walk_concepts(
    bundle_root: Path, *, statuses: Iterable[str] | None = None
) -> list[Concept]:
    """Walk a bundle into ``Concept`` records, sorted by id.

    Reserved files (``index.md`` / ``log.md``) are skipped. When ``statuses`` is
    given, only concepts whose ``status`` is in that set are returned (used to
    publish release-eligible concepts only).
    """
    allowed = set(statuses) if statuses is not None else None
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
        status = str(fm.get("status") or "")
        if allowed is not None and status not in allowed:
            continue
        tags = fm.get("tags") or []
        if not isinstance(tags, list):
            tags = [str(tags)]
        cits = fm.get("citations") or []
        if not isinstance(cits, list):
            cits = [str(cits)]
        body = doc.body or ""
        # Curated concepts carry citations in the body's "# Citations" section,
        # not in frontmatter; surface those URLs too.
        citation_urls = [str(c) for c in cits] + [
            u for u in _citation_urls(body) if u not in {str(c) for c in cits}
        ]
        concepts.append(
            Concept(
                id=concept_id,
                type=str(fm.get("type") or "Unknown"),
                title=str(fm.get("title") or concept_id),
                description=str(fm.get("description") or ""),
                resource=str(fm.get("resource") or ""),
                status=status,
                visibility=str(fm.get("visibility") or ""),
                last_verified=str(fm.get("last_verified") or ""),
                tags=[str(t) for t in tags],
                citations=citation_urls,
                path=md_path.relative_to(bundle_root).as_posix(),
                body=body,
                links_to=extract_links(body, md_path.parent, bundle_root),
            )
        )
    return concepts


def _resolved_edges(concepts: list[Concept]) -> list[tuple[str, str]]:
    """Deduplicated, sorted (source, target) edges between included concepts."""
    ids = {c.id for c in concepts}
    seen: set[tuple[str, str]] = set()
    for c in concepts:
        for target in c.links_to:
            if target == c.id or target not in ids:
                continue
            seen.add((c.id, target))
    return sorted(seen)


def build_graph(concepts: list[Concept]) -> dict[str, Any]:
    """Cytoscape-shaped graph for the interactive viewer."""
    nodes = [c.to_node() for c in concepts]
    edges = [
        {"data": {"id": f"{s}__{t}", "source": s, "target": t}}
        for s, t in _resolved_edges(concepts)
    ]
    bodies = {c.id: c.body for c in concepts}
    types = sorted({c.type for c in concepts})
    return {
        "nodes": nodes,
        "edges": edges,
        "bodies": bodies,
        "types": types,
        "palette": _TYPE_PALETTE,
    }


def build_catalog(
    concepts: list[Concept], *, okf_version: str = "0.1", bundle: str = "jvto"
) -> dict[str, Any]:
    """Machine-readable consumption manifest: the whole knowledge graph in one object.

    Deterministic: concepts are already id-sorted by ``walk_concepts``, edges are
    sorted, and the caller serializes with ``sort_keys=True`` and no timestamps.
    """
    ids = {c.id for c in concepts}
    type_counts: dict[str, int] = {}
    for c in concepts:
        type_counts[c.type] = type_counts.get(c.type, 0) + 1
    return {
        "okf_version": okf_version,
        "bundle": bundle,
        "concept_count": len(concepts),
        "type_counts": type_counts,
        "concepts": [
            {
                "id": c.id,
                "path": c.path,
                "type": c.type,
                "title": c.title,
                "description": c.description,
                "status": c.status,
                "visibility": c.visibility,
                "last_verified": c.last_verified,
                "tags": c.tags,
                "resource": c.resource,
                "citations": c.citations,
                "links_to": sorted(t for t in dict.fromkeys(c.links_to) if t in ids),
            }
            for c in concepts
        ],
        "edges": [{"source": s, "target": t} for s, t in _resolved_edges(concepts)],
    }
