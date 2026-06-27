"""Shared OKF document and concept-path primitives for the JVTO tooling.

This module is an additive, dependency-light port of the upstream
``knowledge-catalog`` reference agent's ``bundle/document.py`` and
``bundle/paths.py`` modules, adapted to the JVTO bundle's conventions
(lowercase URL-safe concept ids, the same ``---`` frontmatter delimiter
used by ``common.parse_frontmatter``).

It is consumed by ``visualize.py`` and is available for future adoption by
``build_bundle.py`` / ``validate_okf.py`` / ``common.py``. It intentionally
does **not** change the behaviour of those scripts: the strict JVTO release
rules remain owned by ``validate_okf.py``. ``OKFDocument.validate`` only
checks the single field OKF v0.1 requires for conformance — a non-empty
``type`` (see ``okf/SPEC.md`` §9 in the upstream repository).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# OKF v0.1 requires only ``type``. The other keys are recommended; JVTO's
# own required-field rule (JVTO-06) is enforced separately in validate_okf.py.
REQUIRED_FRONTMATTER_KEYS = ("type",)
RECOMMENDED_FRONTMATTER_KEYS = ("title", "description", "tags", "timestamp")

_FRONTMATTER_DELIM = "---"

# JVTO concept ids are lowercase URL-safe paths (see common.safe_concept_id).
# A single path segment may not contain a slash; it starts with an
# alphanumeric and may continue with alphanumerics, hyphens, or underscores.
_SEGMENT_RE = re.compile(r"[a-z0-9][a-z0-9_\-]*")


class OKFDocumentError(ValueError):
    """Raised when a document cannot be parsed or fails OKF validation."""


@dataclass
class OKFDocument:
    """An OKF concept: a YAML frontmatter mapping plus a markdown body."""

    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""

    @classmethod
    def parse(cls, text: str) -> "OKFDocument":
        lines = text.splitlines()
        if not lines or lines[0].strip() != _FRONTMATTER_DELIM:
            return cls(frontmatter={}, body=text)

        end_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == _FRONTMATTER_DELIM:
                end_idx = i
                break
        if end_idx is None:
            raise OKFDocumentError("Unterminated YAML frontmatter block")

        fm_text = "\n".join(lines[1:end_idx])
        try:
            fm = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError as e:
            raise OKFDocumentError(f"Invalid YAML in frontmatter: {e}") from e
        if not isinstance(fm, dict):
            raise OKFDocumentError("Frontmatter must be a YAML mapping")

        body = "\n".join(lines[end_idx + 1:])
        if body.startswith("\n"):
            body = body[1:]
        return cls(frontmatter=fm, body=body)

    def serialize(self) -> str:
        fm_text = yaml.safe_dump(
            self.frontmatter, sort_keys=False, allow_unicode=True
        ).rstrip()
        body = self.body if self.body.endswith("\n") else self.body + "\n"
        return f"{_FRONTMATTER_DELIM}\n{fm_text}\n{_FRONTMATTER_DELIM}\n\n{body}"

    def validate(self) -> None:
        """Check OKF v0.1 conformance: a non-empty ``type`` field."""
        missing = [k for k in REQUIRED_FRONTMATTER_KEYS if not self.frontmatter.get(k)]
        if missing:
            raise OKFDocumentError(
                f"Missing required frontmatter keys: {', '.join(missing)}"
            )


def _validate_segment(seg: str) -> None:
    if not _SEGMENT_RE.fullmatch(seg):
        raise ValueError(f"Invalid concept id segment: {seg!r}")


def parse_concept_id(s: str) -> tuple[str, ...]:
    """Split a ``a/b/c`` concept id into validated segments."""
    parts = tuple(p for p in s.split("/") if p)
    if not parts:
        raise ValueError(f"Empty concept id: {s!r}")
    for p in parts:
        _validate_segment(p)
    return parts


def concept_id_to_path(bundle_root: Path, concept_id: tuple[str, ...]) -> Path:
    """Map ``("destinations", "kawah-ijen")`` to ``<root>/destinations/kawah-ijen.md``."""
    if not concept_id:
        raise ValueError("concept_id must have at least one segment")
    for seg in concept_id:
        _validate_segment(seg)
    *dirs, name = concept_id
    return bundle_root.joinpath(*dirs, f"{name}.md")


def path_to_concept_id(bundle_root: Path, path: Path) -> tuple[str, ...]:
    """Map ``<root>/destinations/kawah-ijen.md`` back to its concept-id tuple."""
    rel = path.relative_to(bundle_root).with_suffix("")
    return tuple(rel.parts)
