"""Tests for the shared OKF core module and the bundle visualizer."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import okf_core  # noqa: E402
import visualize  # noqa: E402


class OKFDocumentTests(unittest.TestCase):
    def test_parse_roundtrip(self) -> None:
        text = (
            "---\n"
            "type: Destination\n"
            "title: Kawah Ijen\n"
            "description: An active volcano.\n"
            "tags:\n- volcano\n- ijen\n"
            "---\n\n"
            "# Overview\n\nBody text.\n"
        )
        doc = okf_core.OKFDocument.parse(text)
        self.assertEqual(doc.frontmatter["type"], "Destination")
        self.assertEqual(doc.frontmatter["tags"], ["volcano", "ijen"])
        self.assertIn("# Overview", doc.body)
        # Re-parsing the serialized form yields the same frontmatter and body.
        reparsed = okf_core.OKFDocument.parse(doc.serialize())
        self.assertEqual(reparsed.frontmatter, doc.frontmatter)
        self.assertEqual(reparsed.body.strip(), doc.body.strip())

    def test_validate_requires_type(self) -> None:
        okf_core.OKFDocument(frontmatter={"type": "Policy"}).validate()  # no raise
        with self.assertRaises(okf_core.OKFDocumentError):
            okf_core.OKFDocument(frontmatter={"title": "no type"}).validate()

    def test_unterminated_frontmatter_raises(self) -> None:
        with self.assertRaises(okf_core.OKFDocumentError):
            okf_core.OKFDocument.parse("---\ntype: Policy\nno closing delimiter\n")

    def test_concept_id_path_roundtrip(self) -> None:
        root = Path("/bundle")
        cid = okf_core.parse_concept_id("destinations/kawah-ijen")
        self.assertEqual(cid, ("destinations", "kawah-ijen"))
        path = okf_core.concept_id_to_path(root, cid)
        self.assertEqual(path, root / "destinations" / "kawah-ijen.md")
        self.assertEqual(okf_core.path_to_concept_id(root, path), cid)

    def test_concept_id_rejects_traversal(self) -> None:
        with self.assertRaises(ValueError):
            okf_core.parse_concept_id("../secrets/finance")


class VisualizeTests(unittest.TestCase):
    def _write(self, root: Path, rel: str, text: str) -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_absolute_bundle_links_become_edges(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "organization.md",
                "---\ntype: Organization\ntitle: JVTO\nstatus: reviewed\n---\n\n"
                "See [Kawah Ijen](/destinations/kawah-ijen.md).\n",
            )
            self._write(
                root,
                "destinations/kawah-ijen.md",
                "---\ntype: Destination\ntitle: Kawah Ijen\nstatus: reviewed\n---\n\n"
                "Part of [JVTO](/organization.md).\n",
            )
            # index.md is reserved and must be ignored.
            self._write(root, "index.md", "# Index\n\n* [JVTO](organization.md)\n")

            out = root / "viz.html"
            result = visualize.generate_visualization(root, out, bundle_name="JVTO")

            self.assertEqual(result["concepts"], 2)
            self.assertEqual(result["edges"], 2)

            html = out.read_text(encoding="utf-8")
            m = re.search(r"window\.BUNDLE = (\{.*?\});\n", html, re.S)
            self.assertIsNotNone(m)
            data = json.loads(m.group(1))
            sources = {e["data"]["source"] for e in data["edges"]}
            targets = {e["data"]["target"] for e in data["edges"]}
            self.assertEqual(sources, {"organization", "destinations/kawah-ijen"})
            self.assertEqual(targets, {"organization", "destinations/kawah-ijen"})
            # Node colour comes from the JVTO type palette; status is surfaced.
            org = next(n for n in data["nodes"] if n["data"]["id"] == "organization")
            self.assertEqual(org["data"]["color"], visualize._TYPE_PALETTE["Organization"])
            self.assertEqual(org["data"]["status"], "reviewed")

    def test_output_is_deterministic(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "organization.md",
                "---\ntype: Organization\ntitle: JVTO\n---\n\nBody.\n",
            )
            out1 = root / "a.html"
            out2 = root / "b.html"
            visualize.generate_visualization(root, out1, bundle_name="JVTO")
            visualize.generate_visualization(root, out2, bundle_name="JVTO")
            self.assertEqual(out1.read_bytes(), out2.read_bytes())


if __name__ == "__main__":
    unittest.main()
