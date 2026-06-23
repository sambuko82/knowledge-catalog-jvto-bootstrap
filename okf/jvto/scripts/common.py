from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

TOOL_ROOT = Path(__file__).resolve().parents[1]
OKF_ROOT = TOOL_ROOT.parents[0]
BUNDLE_ROOT = Path(os.environ.get("JVTO_OKF_BUNDLE_ROOT", OKF_ROOT / "bundles" / "jvto"))
SNAPSHOT_ROOT = Path(os.environ.get("JVTO_OKF_SNAPSHOT_ROOT", TOOL_ROOT / "sources" / "snapshots"))
BUILD_ROOT = Path(os.environ.get("JVTO_OKF_BUILD_ROOT", TOOL_ROOT / "build"))
CONFIG_ROOT = TOOL_ROOT / "config"
CURATION_ROOT = Path(os.environ.get("JVTO_OKF_CURATION_ROOT", TOOL_ROOT / "curation" / "approved"))
RESERVED_FILENAMES = {"index.md", "log.md"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def write_yaml_frontmatter(metadata: dict[str, Any]) -> str:
    return "---\n" + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip() + "\n---\n"


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("Missing YAML frontmatter")
    pieces = text.split("---\n", 2)
    if len(pieces) < 3:
        raise ValueError("Unclosed YAML frontmatter")
    data = yaml.safe_load(pieces[1]) or {}
    if not isinstance(data, dict):
        raise ValueError("Frontmatter must be a mapping")
    return data, pieces[2]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_concept_id(concept_id: str) -> str:
    value = concept_id.strip().strip("/")
    if not value or value.endswith(".md") or ".." in value.split("/"):
        raise ValueError(f"Unsafe concept id: {concept_id!r}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9/_-]*", value):
        raise ValueError(f"Concept id must be lowercase URL-safe path: {concept_id!r}")
    return value


def concept_path(concept_id: str) -> Path:
    return BUNDLE_ROOT / f"{safe_concept_id(concept_id)}.md"
