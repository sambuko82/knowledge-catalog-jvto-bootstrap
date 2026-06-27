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
from pathlib import Path
from typing import Any

# Allow ``python scripts/visualize.py`` from anywhere by making the script
# directory importable for the sibling modules.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from bundle_graph import (  # noqa: E402
    _TYPE_PALETTE,  # re-exported for tests that assert node colours
    build_graph,
    walk_concepts,
)

_ASSET_DIR = Path(__file__).resolve().parent / "viz_assets"


def _embed_json(value: Any) -> str:
    """Serialize ``value`` for safe embedding inside an inline ``<script>``.

    ``json.dumps`` would leave a literal ``</script>`` from concept content
    intact, which a browser would treat as closing the script tag (breaking
    the viewer and allowing the trailing bundle text to be parsed as HTML).
    Escaping ``<`` and ``>`` to their ``\\uXXXX`` forms keeps the value valid
    JSON/JS while making ``</script>`` impossible to emit. The result is
    deterministic (no timestamps, sorted keys).
    """
    return (
        json.dumps(value, sort_keys=True)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


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

    # The viewer is a local inspection tool: show every concept regardless of
    # status (no status filter), unlike the published catalog.json.
    concepts = walk_concepts(bundle_root)
    graph = build_graph(concepts)
    template = (_ASSET_DIR / "viz.html").read_text(encoding="utf-8")
    css = (_ASSET_DIR / "viz.css").read_text(encoding="utf-8")
    js = (_ASSET_DIR / "viz.js").read_text(encoding="utf-8")
    name = bundle_name or bundle_root.resolve().name

    html = (
        template
        .replace("/*__VIZ_CSS__*/", css)
        .replace("/*__VIZ_JS__*/", js)
        .replace("__BUNDLE_NAME__", _embed_json(name))
        .replace("__BUNDLE_DATA__", _embed_json(graph))
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
