#!/usr/bin/env python3
"""Lightweight PostToolUse hook: structural check for edited OKF curation YAML.

Fires after Edit/Write. Reads the hook JSON on stdin, and if the edited file is a
`okf/jvto/curation/approved/*.yaml`, runs a fast structural check:

  - YAML parses
  - each record id is non-empty and unique within the file
  - concept type is one of the known types
  - status is a known lifecycle value
  - Partner and Reference records contain a "# Claim Boundary" section
  - no forbidden public terms appear in the record

It does NOT build the bundle or hit the network (that is the pre-commit/CI job in
validate-okf.sh). Structural problems exit 2 with a message so the agent sees them;
anything else exits 0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

VALID_TYPES = {
    "Organization", "Destination", "Tour Package", "Policy", "Travel Guide",
    "Trust Claim", "Credential", "Review Platform", "Partner", "Reference",
}
BOUNDARY_REQUIRED_TYPES = {"Partner", "Reference"}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # not our event / no payload — never block
    file_path = str(((payload.get("tool_input") or {}).get("file_path")) or "").replace("\\", "/")
    if "okf/jvto/curation/approved/" not in file_path or not file_path.endswith(".yaml"):
        return 0

    path = Path(file_path)
    if not path.exists():
        return 0

    try:
        import yaml  # noqa: PLC0415
    except Exception:
        return 0  # PyYAML not importable here — leave it to validate-okf.sh

    # Load known statuses + forbidden terms from the publication rules if reachable.
    known_statuses = {"draft", "generated_pending_review", "needs_review", "reviewed",
                      "verified", "qualified", "published", "deprecated"}
    forbidden: list[str] = []
    try:
        repo = path.resolve()
        while repo.name and not (repo / "okf" / "jvto" / "config").exists():
            repo = repo.parent
        rules = yaml.safe_load((repo / "okf" / "jvto" / "config" / "publication-rules.yaml").read_text(encoding="utf-8"))
        known_statuses = set((rules.get("bundle") or {}).get("known_statuses", known_statuses)) or known_statuses
        forbidden = [str(t).lower() for t in rules.get("forbidden_public_terms", [])]
    except Exception:
        pass

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        print(f"[okf hook] {path.name}: YAML does not parse: {exc}", file=sys.stderr)
        return 2

    records = data.get("records", []) if isinstance(data, dict) else []
    issues: list[str] = []
    seen: set[str] = set()
    for rec in records:
        if not isinstance(rec, dict):
            continue
        rid = str(rec.get("id", "")).strip()
        rtype = str(rec.get("type", "")).strip()
        status = str(rec.get("status", "")).strip()
        body = str(rec.get("body", ""))
        label = rid or "(missing id)"
        if not rid:
            issues.append("a record is missing 'id'")
        elif rid in seen:
            issues.append(f"duplicate id within file: {rid}")
        else:
            seen.add(rid)
        if rtype and rtype not in VALID_TYPES:
            issues.append(f"{label}: unknown type {rtype!r}")
        if status and status not in known_statuses:
            issues.append(f"{label}: unknown status {status!r}")
        if rtype in BOUNDARY_REQUIRED_TYPES and "# Claim Boundary" not in body:
            issues.append(f"{label}: {rtype} concept must include a '# Claim Boundary' section")
        text = " ".join(str(v) for v in rec.values()).lower()
        for term in forbidden:
            if term and term in text:
                issues.append(f"{label}: forbidden public term: {term}")

    if issues:
        print(f"[okf hook] {path.name}: structural issues before build/validate:", file=sys.stderr)
        for i in issues:
            print(f"  - {i}", file=sys.stderr)
        print("  Fix these, then run okf/jvto validation (see CLAUDE.md).", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
