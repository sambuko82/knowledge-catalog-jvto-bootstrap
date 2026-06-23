from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]


class OkfToolsTest(unittest.TestCase):
    def test_package_candidate_build_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            snapshot_root = root / "snapshots"
            package_dir = snapshot_root / "llm_wiki" / "output" / "products" / "package-readiness"
            package_dir.mkdir(parents=True)
            bundle_root = root / "bundle"
            (bundle_root / "policies").mkdir(parents=True)
            (bundle_root / "policies" / "index.md").write_text("# Policies\n", encoding="utf-8")
            build_root = root / "build"

            def write_json(name: str, payload) -> None:
                (package_dir / name).write_text(json.dumps(payload), encoding="utf-8")

            write_json("_manifest.json", {"schema_version": "package-readiness/v1.3", "clean": True, "generated_at": "2026-06-23T00:00:00Z"})
            write_json("package-registry.json", [{"package_id": "bromo-1d1n", "slug": "bromo-1d1n", "origin": "surabaya", "title": "1 Day Bromo", "duration": "1D1N", "public_url": "/tours/from-surabaya/bromo-1d1n", "ijen_relevant": False, "visits_madakaripura": False, "is_specialty": False}])
            write_json("package-pricing.json", [{"package_id": "bromo-1d1n", "currency": "IDR", "pax_tiers": []}])
            write_json("package-itineraries.json", [{"package_id": "bromo-1d1n", "days": [{"title": "Bromo sunrise"}]}])
            write_json("booking-compatibility.json", [{"package_id": "bromo-1d1n", "instant_book": True, "whatsapp_assisted": True}])

            env = os.environ.copy()
            env.update({
                "JVTO_OKF_SNAPSHOT_ROOT": str(snapshot_root),
                "JVTO_OKF_BUNDLE_ROOT": str(bundle_root),
                "JVTO_OKF_BUILD_ROOT": str(build_root),
            })
            result = subprocess.run([sys.executable, "scripts/build_bundle.py", "--all"], cwd=TOOL_ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            concept = bundle_root / "tours" / "from-surabaya" / "bromo-1d1n.md"
            self.assertTrue(concept.exists())
            content = concept.read_text(encoding="utf-8")
            self.assertIn("generated_pending_review", content)
            self.assertIn("# Citations", content)

            validation = subprocess.run([sys.executable, "scripts/validate_okf.py", "--strict-links"], cwd=TOOL_ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(validation.returncode, 0, validation.stderr)


if __name__ == "__main__":
    unittest.main()
