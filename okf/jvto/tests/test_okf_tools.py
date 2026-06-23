from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import textwrap
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

    def test_local_fetch_copies_allowed_and_blocks_forbidden(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            clone = root / "fake_llm_wiki"
            allowed_rel = "output/products/package-readiness/_manifest.json"
            allowed_body = '{"schema_version": "package-readiness/v1.3", "clean": true}'
            allowed_file = clone / allowed_rel
            allowed_file.parent.mkdir(parents=True)
            allowed_file.write_text(allowed_body, encoding="utf-8")
            forbidden_file = clone / "raw" / "FINANCE" / "rates.json"
            forbidden_file.parent.mkdir(parents=True)
            forbidden_file.write_text('{"secret": true}', encoding="utf-8")

            config = root / "upstreams.yaml"
            config.write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    upstreams:
                      llm_wiki:
                        repo: sambuko82/llm-wiki
                        ref: master
                        forbidden_prefixes: [raw/]
                        files:
                          - {path: output/products/package-readiness/_manifest.json, required: true}
                          - {path: raw/FINANCE/rates.json, required: false}
                    """
                ),
                encoding="utf-8",
            )

            snapshot_root = root / "snapshots"
            env = os.environ.copy()
            env.update({
                "JVTO_OKF_SNAPSHOT_ROOT": str(snapshot_root),
                "JVTO_OKF_LOCAL_LLM_WIKI": str(clone),
            })
            result = subprocess.run(
                [sys.executable, "scripts/fetch_snapshots.py", "--local", "--config", str(config)],
                cwd=TOOL_ROOT, env=env, capture_output=True, text=True,
            )
            # A forbidden entry in the allow-list is a hard error by design.
            self.assertEqual(result.returncode, 2, result.stderr)

            snap = snapshot_root / "llm_wiki" / allowed_rel
            self.assertTrue(snap.exists())
            self.assertEqual(snap.read_text(encoding="utf-8"), allowed_body)
            # The forbidden file must never be copied into the snapshot.
            self.assertFalse((snapshot_root / "llm_wiki" / "raw" / "FINANCE" / "rates.json").exists())

            manifest = json.loads((snapshot_root / "_snapshot_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["mode"], "local")
            records = {r["path"]: r for r in manifest["sources"]["llm_wiki"]["files"]}
            self.assertEqual(records[allowed_rel]["status"], "fetched")
            self.assertEqual(records[allowed_rel]["sha256"], hashlib.sha256(allowed_body.encode()).hexdigest())
            self.assertEqual(records["raw/FINANCE/rates.json"]["status"], "blocked")

    def test_local_fetch_rejects_symlink_into_forbidden_area(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            clone = root / "clone"
            secret = clone / "raw" / "FINANCE" / "rates.json"
            secret.parent.mkdir(parents=True)
            secret.write_text("SECRET-COGS", encoding="utf-8")
            # An innocent-looking allow-listed path that is actually a symlink
            # pointing into the forbidden raw/ area.
            allowed = clone / "output" / "products" / "package-readiness" / "_manifest.json"
            allowed.parent.mkdir(parents=True)
            allowed.symlink_to(secret)

            config = root / "upstreams.yaml"
            config.write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    upstreams:
                      llm_wiki:
                        repo: sambuko82/llm-wiki
                        ref: master
                        forbidden_prefixes: [raw/]
                        files:
                          - {path: output/products/package-readiness/_manifest.json, required: true}
                    """
                ),
                encoding="utf-8",
            )

            snapshot_root = root / "snapshots"
            env = os.environ.copy()
            env.update({
                "JVTO_OKF_SNAPSHOT_ROOT": str(snapshot_root),
                "JVTO_OKF_LOCAL_LLM_WIKI": str(clone),
            })
            result = subprocess.run(
                [sys.executable, "scripts/fetch_snapshots.py", "--local", "--config", str(config)],
                cwd=TOOL_ROOT, env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            # The secret target's bytes must never reach the snapshot.
            snap = snapshot_root / "llm_wiki" / "output" / "products" / "package-readiness" / "_manifest.json"
            self.assertFalse(snap.exists())
            manifest = json.loads((snapshot_root / "_snapshot_manifest.json").read_text(encoding="utf-8"))
            records = {r["path"]: r for r in manifest["sources"]["llm_wiki"]["files"]}
            self.assertEqual(records["output/products/package-readiness/_manifest.json"]["status"], "blocked")

    def test_local_fetch_happy_path_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            clone = root / "fake_core"
            rel = "generated/itinerary-intelligence/manifest.json"
            f = clone / rel
            f.parent.mkdir(parents=True)
            f.write_text('{"ok": true}', encoding="utf-8")

            config = root / "upstreams.yaml"
            config.write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    upstreams:
                      itinerary_core:
                        repo: sambuko82/jvto-itinerary-core
                        ref: main
                        forbidden_prefixes: [input/, seed/]
                        files:
                          - {path: generated/itinerary-intelligence/manifest.json, required: true}
                    """
                ),
                encoding="utf-8",
            )

            snapshot_root = root / "snapshots"
            env = os.environ.copy()
            env.update({
                "JVTO_OKF_SNAPSHOT_ROOT": str(snapshot_root),
                "JVTO_OKF_LOCAL_ITINERARY_CORE": str(clone),
            })
            result = subprocess.run(
                [sys.executable, "scripts/fetch_snapshots.py", "--local", "--config", str(config)],
                cwd=TOOL_ROOT, env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((snapshot_root / "itinerary_core" / rel).exists())

    def test_local_fetch_missing_root_is_blocking_when_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / "upstreams.yaml"
            config.write_text(
                textwrap.dedent(
                    """\
                    version: 1
                    upstreams:
                      llm_wiki:
                        repo: sambuko82/llm-wiki
                        ref: master
                        files:
                          - {path: output/products/package-readiness/_manifest.json, required: true}
                    """
                ),
                encoding="utf-8",
            )
            snapshot_root = root / "snapshots"
            env = os.environ.copy()
            env.update({"JVTO_OKF_SNAPSHOT_ROOT": str(snapshot_root)})
            # No JVTO_OKF_LOCAL_LLM_WIKI set -> unresolved root -> blocking.
            env.pop("JVTO_OKF_LOCAL_LLM_WIKI", None)
            result = subprocess.run(
                [sys.executable, "scripts/fetch_snapshots.py", "--local", "--config", str(config)],
                cwd=TOOL_ROOT, env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_policy_candidate_build_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            snapshot_root = root / "snapshots"
            policy_dir = snapshot_root / "llm_wiki" / "output" / "website" / "policy-bundle"
            policy_dir.mkdir(parents=True)
            (policy_dir / "_manifest.json").write_text(
                json.dumps({"schema_version": "policy-bundle/v1.0", "clean": True, "generated_at": "2026-06-23T00:00:00Z"}),
                encoding="utf-8",
            )
            (policy_dir / "policy-bundle.json").write_text(
                json.dumps([
                    {
                        "policy_id": "booking-paths",
                        "domain": "Booking Paths",
                        "notes": "Two official booking paths.",
                        "consumers": ["faq", "website"],
                        "evidence": [
                            {"section": "Booking Flow", "text": "Website instant book and WhatsApp-assisted. See [[products/packages-overview|the overview]]."}
                        ],
                    }
                ]),
                encoding="utf-8",
            )

            bundle_root = root / "bundle"
            for sub in ("tours", "policies"):
                (bundle_root / sub).mkdir(parents=True)
                (bundle_root / sub / "index.md").write_text(f"# {sub}\n", encoding="utf-8")

            env = os.environ.copy()
            env.update({
                "JVTO_OKF_SNAPSHOT_ROOT": str(snapshot_root),
                "JVTO_OKF_BUNDLE_ROOT": str(bundle_root),
                "JVTO_OKF_BUILD_ROOT": str(root / "build"),
            })
            result = subprocess.run([sys.executable, "scripts/build_bundle.py", "--policies", "--indexes"], cwd=TOOL_ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            concept = bundle_root / "policies" / "booking-paths.md"
            self.assertTrue(concept.exists())
            content = concept.read_text(encoding="utf-8")
            self.assertIn("type: Policy", content)
            self.assertIn("generated_pending_review", content)
            self.assertIn("# Citations", content)
            self.assertNotIn("[[", content)  # Obsidian wikilinks flattened

            validation = subprocess.run([sys.executable, "scripts/validate_okf.py", "--strict-links"], cwd=TOOL_ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_curated_verified_concept_passes_release(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            curation = root / "approved"
            curation.mkdir(parents=True)
            (curation / "organization.yaml").write_text(
                textwrap.dedent(
                    """\
                    records:
                      - id: organization
                        type: Organization
                        title: JVTO
                        description: Private volcano tour operator.
                        tags: [organization, jvto]
                        timestamp: "2026-06-23T00:00:00+07:00"
                        status: verified
                        visibility: public
                        last_verified: "2026-06-23"
                        body: |
                          # Overview
                          JVTO runs private volcano tours.
                          # Related Concepts
                          - [Tours](/tours/index.md)
                        citations:
                          - https://javavolcano-touroperator.com
                    """
                ),
                encoding="utf-8",
            )
            bundle_root = root / "bundle"
            (bundle_root / "tours").mkdir(parents=True)
            (bundle_root / "tours" / "index.md").write_text("# tours\n", encoding="utf-8")

            env = os.environ.copy()
            env.update({
                "JVTO_OKF_CURATION_ROOT": str(curation),
                "JVTO_OKF_BUNDLE_ROOT": str(bundle_root),
                "JVTO_OKF_BUILD_ROOT": str(root / "build"),
            })
            build = subprocess.run([sys.executable, "scripts/build_bundle.py", "--curated", "--indexes"], cwd=TOOL_ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            concept = bundle_root / "organization.md"
            self.assertTrue(concept.exists())
            content = concept.read_text(encoding="utf-8")
            self.assertIn("status: verified", content)
            self.assertIn("# Citations", content)

            release = subprocess.run([sys.executable, "scripts/validate_okf.py", "--release", "--strict-links"], cwd=TOOL_ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(release.returncode, 0, release.stderr)

    def test_validate_rejects_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bundle_root = root / "bundle" / "references"
            bundle_root.mkdir(parents=True)
            (bundle_root / "bad.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    type: Reference
                    id: references/bad
                    description: Missing title and tags.
                    timestamp: "2026-06-23T00:00:00Z"
                    status: draft
                    visibility: public
                    ---

                    # Body
                    """
                ),
                encoding="utf-8",
            )
            env = os.environ.copy()
            env.update({
                "JVTO_OKF_BUNDLE_ROOT": str(root / "bundle"),
                "JVTO_OKF_BUILD_ROOT": str(root / "build"),
            })
            result = subprocess.run([sys.executable, "scripts/validate_okf.py"], cwd=TOOL_ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertIn("Missing required field: title", result.stderr)
            self.assertIn("Missing required field: tags", result.stderr)

    def test_validate_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            refs = root / "bundle" / "references"
            refs.mkdir(parents=True)
            record = textwrap.dedent(
                """\
                ---
                type: Reference
                title: Dup
                description: Duplicate id case.
                tags: [reference]
                timestamp: "2026-06-23T00:00:00Z"
                id: references/dup
                status: reviewed
                visibility: public
                ---

                # Body
                """
            )
            (refs / "a.md").write_text(record, encoding="utf-8")
            (refs / "b.md").write_text(record, encoding="utf-8")
            env = os.environ.copy()
            env.update({
                "JVTO_OKF_BUNDLE_ROOT": str(root / "bundle"),
                "JVTO_OKF_BUILD_ROOT": str(root / "build"),
            })
            result = subprocess.run([sys.executable, "scripts/validate_okf.py"], cwd=TOOL_ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertIn("Duplicate id", result.stderr)


if __name__ == "__main__":
    unittest.main()
