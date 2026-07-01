"""Realistic-scenario coverage for build_customer_sales_release.py.

No test previously existed for this script. These tests run it against the real sibling
jvto-itinerary-core checkout (the way it is actually invoked) and assert that facts newly
connected from Core — package/route recommendations, destination operational overlays,
and staging operational notes — reach the release with correct classification and
provenance, and that the existing no-leak/schema validators still pass.

Skips gracefully if the sibling checkout is not present (this script is not part of the
CLAUDE.md-mandated CI validation path, unlike build_bundle.py / validate_okf.py).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
CORE_ROOT = TOOL_ROOT.parents[2] / "jvto-itinerary-core"


@unittest.skipUnless(CORE_ROOT.exists(), f"sibling checkout not found at {CORE_ROOT}")
class BuildCustomerSalesReleaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.out_dir = Path(tempfile.mkdtemp()) / "release"
        result = subprocess.run(
            [sys.executable, "scripts/build_customer_sales_release.py",
             "--core-root", str(CORE_ROOT), "--out", str(self.out_dir)],
            cwd=TOOL_ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def _read(self, name: str):
        return json.loads((self.out_dir / name).read_text(encoding="utf-8"))

    def test_ferry_and_ijen_advisories_reach_endpoint_chains_for_a_real_ketapang_package(self) -> None:
        endpoints = {r["package_key"]: r for r in self._read("endpoint-chains.json")}
        pkg = endpoints["tumpak-sewu-bromo-ijen-4d3n"]
        rule_ids = {r["rule_id"] for r in pkg["route_recommendations"]}
        self.assertIn("ferry_bali_buffer_required", rule_ids)
        self.assertIn("ijen_access_closure_risk", rule_ids)
        for r in pkg["route_recommendations"]:
            self.assertNotIn("IDR", r["note"], "cost figure must not leak into the customer-sales release")

    def test_a_surabaya_only_package_does_not_carry_irrelevant_recommendations(self) -> None:
        endpoints = {r["package_key"]: r for r in self._read("endpoint-chains.json")}
        pkg = endpoints["bromo-1d1n"]
        rule_ids = {r["rule_id"] for r in pkg["route_recommendations"]}
        self.assertNotIn("ferry_bali_buffer_required", rule_ids)
        self.assertNotIn("ijen_access_closure_risk", rule_ids)

    def test_kawah_ijen_destination_guidance_carries_fatigue_and_live_check_facts(self) -> None:
        guidance = {r["id"]: r for r in self._read("destination-guidance.json")}
        ijen = guidance["destinations/kawah-ijen"]
        self.assertIsNotNone(ijen["operational_overlay"])
        self.assertEqual(ijen["operational_overlay"]["fatigue_score"], 5)
        self.assertIn("health_screening", ijen["operational_overlay"]["requires_live_check"])
        self.assertIn("core:generated/itinerary-intelligence/agent-contract/destination-operational-overlays.json",
                      ijen["source_evidence"])

    def test_bromo_package_accommodation_rules_carry_staging_operational_notes(self) -> None:
        accommodation = {r["package_key"]: r for r in self._read("accommodation-rules.json")}
        pkg = accommodation["bromo-1d1n"]
        self.assertTrue(pkg["staging_notes"], "bromo-1d1n should have at least one staging note")
        staging = pkg["staging_notes"][0]
        self.assertIn("operational_notes", staging)
        self.assertIn("risk_if_arrival_late", staging)

    def test_release_still_passes_the_no_leak_validator(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_customer_sales_release.py", "--out", str(self.out_dir)],
            cwd=TOOL_ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass", report)


if __name__ == "__main__":
    unittest.main()
