#!/usr/bin/env python3
"""Validate the public JVTO OKF bundle and write a machine-readable local report.

Rules:
  OKF-01  frontmatter parses
  JVTO-06 required fields present (type, title, description, tags, timestamp, id, status)
  JVTO-02 visibility is public / public_sensitive
  JVTO-07 status is a known lifecycle value
  JVTO-03 (release) status is release-eligible
  JVTO-08 concept id is unique across the bundle
  JVTO-04 required-citation types carry a non-empty "# Citations" section with a public URL
  JVTO-09 verified/qualified concepts carry verification metadata (last_verified or verified_at)
  JVTO-05 no forbidden/sensitive terms
  JVTO-10 internal Markdown links stay inside the bundle (no escape)
  OKF-03  internal Markdown links resolve
  JVTO-11 no known-stale review counts near their platform (config: stale_review_claims)
  JVTO-12 provenance required (Person + records with observations/operational/commercial_context)
  JVTO-13 source_refs repo/path must be a known scope repo and resolve under its allow scope (config: source-scope.yaml)
  JVTO-19 each source_refs entry must be a mapping with non-empty source_id/repo/path/source_class/captured_at and a known source_class
  JVTO-14 a generated/manual_seed/inferred record cannot be the sole evidence of a fact
  JVTO-15 a Tour Package identity (package_key) must originate once
  JVTO-16 Review Platform observations, when present, carry current rating/count/as_of/source
  JVTO-17 concept type is a known concept type (config: known_concept_types)
  JVTO-04 (relaxed) required-citation types carry a non-secondary public URL (citation or resource) OR a source_refs anchor
  JVTO-18 the JVTO website (a secondary presentation layer) may not be the SOLE evidence for a claim;
          a source_refs anchor or a non-website external citation/resource must also be present
          (config: secondary_presentation_domains)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import BUNDLE_ROOT, BUILD_ROOT, RESERVED_FILENAMES, parse_frontmatter, read_yaml, utc_now, write_json

LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
URL = re.compile(r"https?://[^\s)]+")
NEXT_HEADING = re.compile(r"\n#\s")
DEFAULT_REQUIRED_FIELDS = ["type", "title", "description", "tags", "timestamp", "id", "status"]
VERIFICATION_FIELDS = ("last_verified", "verified_at")


def internal_target(source: Path, link: str) -> Path:
    if link.startswith("/"):
        return BUNDLE_ROOT / link.lstrip("/")
    return source.parent / link


def field_missing(meta: dict, field: str) -> bool:
    value = meta.get(field)
    if value is None:
        return True
    if field == "tags":
        return not isinstance(value, list) or len(value) == 0
    if isinstance(value, str):
        return not value.strip()
    return False


def citations_block(body: str) -> str | None:
    """Return the text of the '# Citations' section, or None if it is absent."""
    idx = body.find("# Citations")
    if idx == -1:
        return None
    after = body[idx + len("# Citations"):]
    nxt = NEXT_HEADING.search(after)
    return after[: nxt.start()] if nxt else after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--strict-links", action="store_true")
    args = parser.parse_args()
    rules = read_yaml(Path(__file__).resolve().parents[1] / "config" / "publication-rules.yaml")
    bundle_rules = rules.get("bundle", {})
    allowed = set(bundle_rules.get("allowed_statuses_for_release", []))
    known_statuses = set(bundle_rules.get("known_statuses", []))
    required_fields = bundle_rules.get("required_fields", DEFAULT_REQUIRED_FIELDS)
    forbidden = [str(item).lower() for item in rules.get("forbidden_public_terms", [])]
    citation_types = set(rules.get("required_citation_types", []))
    # R3 config (JVTO-11..JVTO-17).
    known_types = set(rules.get("known_concept_types", []))
    source_ref_types = set(rules.get("source_ref_required_types", []))
    source_ref_fields = list(rules.get("source_ref_required_fields", []))
    stale_claims = rules.get("stale_review_claims", []) or []
    scope_path = Path(__file__).resolve().parents[1] / "config" / "source-scope.yaml"
    scope = read_yaml(scope_path) if scope_path.exists() else {}
    deny_by_repo = {
        str(name): [str(p) for p in (spec.get("deny", []) or [])]
        for name, spec in (scope.get("repos", {}) or {}).items()
    }
    allow_by_repo = {
        str(name): [str(p) for p in (spec.get("allow", []) or [])]
        for name, spec in (scope.get("repos", {}) or {}).items()
    }
    known_repos = {str(name) for name in (scope.get("repos", {}) or {}).keys()}
    source_classes = {str(c) for c in (scope.get("rules", {}) or {}).get("source_classes", [])}
    derived_classes = set((scope.get("rules", {}) or {}).get("derived_source_classes", []))
    required_ref_fields = ("source_id", "repo", "path", "source_class", "captured_at")

    def source_ref_problems(ref) -> list[tuple[str, str]]:
        """Return (rule, message) problems for one source_refs entry; empty list means valid.
        Closes the bypass where a placeholder ref (e.g. {} or "x") satisfied the evidence basis."""
        if not isinstance(ref, dict):
            return [("JVTO-19", f"source_refs entry must be a mapping, got {type(ref).__name__}.")]
        problems: list[tuple[str, str]] = []
        for field in required_ref_fields:
            if not str(ref.get(field, "")).strip():
                problems.append(("JVTO-19", f"source_refs entry missing required field: {field}."))
        sclass = str(ref.get("source_class", "")).strip()
        if sclass and source_classes and sclass not in source_classes:
            problems.append(("JVTO-19", f"source_refs entry has unknown source_class: {sclass!r}."))
        ref_repo = str(ref.get("repo", "")).rstrip("/").split("/")[-1]
        ref_path = str(ref.get("path", "")).strip()
        if ref_repo and known_repos and ref_repo not in known_repos:
            problems.append(("JVTO-13", f"source_ref repo not in source scope: {ref_repo}."))
        elif ref_repo and ref_path:
            if any(ref_path.startswith(p) for p in deny_by_repo.get(ref_repo, [])):
                problems.append(("JVTO-13", f"source_ref path under denied scope: {ref_repo}:{ref_path}"))
            else:
                allowed = allow_by_repo.get(ref_repo, [])
                if allowed and not any(ref_path.startswith(p) for p in allowed):
                    problems.append(("JVTO-13", f"source_ref path outside allow scope: {ref_repo}:{ref_path}"))
        return problems
    # R4: the JVTO website is a secondary presentation/corroboration layer, never the sole evidence
    # for a claim (matched by host, so an external URL that merely contains the brand in its path —
    # e.g. a trustpilot review URL — is NOT a secondary-domain match).
    secondary_domains = [str(d).strip().lower() for d in rules.get("secondary_presentation_domains", []) if str(d).strip()]
    website_re = re.compile(
        r"https?://(?:[a-z0-9-]+\.)*(?:" + "|".join(re.escape(d) for d in secondary_domains) + r")(?:[/:?]|$)",
        re.I,
    ) if secondary_domains else None

    def is_secondary(value: str) -> bool:
        return bool(website_re.search(str(value))) if website_re else False

    bundle_resolved = BUNDLE_ROOT.resolve()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen_ids: dict[str, str] = {}
    seen_packages: dict[str, str] = {}

    for path in sorted(BUNDLE_ROOT.rglob("*.md")):
        if path.name in RESERVED_FILENAMES:
            continue
        relative = path.relative_to(BUNDLE_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        try:
            meta, body = parse_frontmatter(text)
        except Exception as exc:  # noqa: BLE001
            errors.append({"rule": "OKF-01", "path": relative, "message": str(exc)})
            continue

        for field in required_fields:
            if field_missing(meta, field):
                errors.append({"rule": "JVTO-06", "path": relative, "message": f"Missing required field: {field}"})

        if meta.get("visibility", "public") not in {"public", "public_sensitive"}:
            errors.append({"rule": "JVTO-02", "path": relative, "message": "Non-public visibility in public bundle."})

        status = meta.get("status")
        if known_statuses and status not in known_statuses:
            errors.append({"rule": "JVTO-07", "path": relative, "message": f"Unknown status: {status!r}."})
        if args.release and status not in allowed:
            errors.append({"rule": "JVTO-03", "path": relative, "message": f"Release requires status in {sorted(allowed)}."})
        if status in {"verified", "qualified"} and all(field_missing(meta, f) for f in VERIFICATION_FIELDS):
            errors.append({"rule": "JVTO-09", "path": relative, "message": f"Status {status!r} requires verification metadata ({' or '.join(VERIFICATION_FIELDS)})."})

        concept_id = str(meta.get("id", "")).strip()
        if concept_id:
            if concept_id in seen_ids:
                errors.append({"rule": "JVTO-08", "path": relative, "message": f"Duplicate id {concept_id!r} (also in {seen_ids[concept_id]})."})
            else:
                seen_ids[concept_id] = relative

        # Evidence basis shared by JVTO-04 and JVTO-18 so the two rules can never diverge on what
        # counts as a non-website (stronger) basis. A non-secondary external URL may live in the
        # rendered "# Citations" block OR in the `resource` frontmatter field; a relative resource
        # (e.g. /tours/...) yields no http(s) URL and so is correctly not counted as evidence.
        cblock = citations_block(body)
        citation_urls = URL.findall(cblock) if cblock else []
        resource_val = str(meta.get("resource", "")).strip()
        resource_urls = URL.findall(resource_val)
        non_secondary_urls = [u for u in (citation_urls + resource_urls) if not is_secondary(u)]
        refs = meta.get("source_refs")
        has_valid_source_refs = isinstance(refs, list) and any(not source_ref_problems(r) for r in refs)
        has_stronger_basis = has_valid_source_refs or bool(non_secondary_urls)

        # JVTO-04: required-citation types must carry a non-website public URL (citation or resource)
        # or a source_refs anchor.
        if meta.get("type") in citation_types and not has_stronger_basis:
            errors.append({"rule": "JVTO-04", "path": relative, "message": "Required-citation type needs a non-website public-URL citation or a source_refs anchor."})

        # JVTO-18: the JVTO website is a secondary presentation/corroboration layer. It may appear as
        # supplementary context, but it may not be the SOLE evidence for a claim — a concept that
        # references the website must also carry a source_refs anchor or a non-website external URL.
        if website_re:
            has_secondary = is_secondary(resource_val) or any(is_secondary(u) for u in citation_urls)
            if has_secondary and not has_stronger_basis:
                errors.append({"rule": "JVTO-18", "path": relative, "message": "JVTO website may not be the sole evidence for a claim; add a source_refs anchor or a non-website external citation/resource."})

        lower = text.lower()
        for term in forbidden:
            if term in lower:
                errors.append({"rule": "JVTO-05", "path": relative, "message": f"Forbidden term: {term}"})

        ctype = meta.get("type")

        # JVTO-17: type is a known concept type.
        if known_types and ctype not in known_types:
            errors.append({"rule": "JVTO-17", "path": relative, "message": f"Unknown concept type: {ctype!r}."})

        # JVTO-11: no known-stale review count within ~40 chars of its platform name.
        for claim in stale_claims:
            platform = str(claim.get("platform", "")).lower().strip()
            count = str(claim.get("count", "")).strip()
            if not platform or not count:
                continue
            hit = any(
                re.search(rf"\b{re.escape(count)}\b", lower[m.start(): m.end() + 40])
                for m in re.finditer(re.escape(platform), lower)
            )
            if hit:
                errors.append({"rule": "JVTO-11", "path": relative, "message": f"Stale review count {count} near '{platform}'."})

        # JVTO-12: provenance required for Person + records carrying observation/operational/commercial fields.
        source_refs = meta.get("source_refs")
        needs_refs = ctype in source_ref_types or any(meta.get(f) for f in source_ref_fields)
        if needs_refs and (not isinstance(source_refs, list) or not source_refs):
            errors.append({"rule": "JVTO-12", "path": relative, "message": "Record requires a non-empty source_refs provenance list."})

        # JVTO-19 (schema) + JVTO-13 (scope): every source_refs entry must be a well-formed, in-scope
        # provenance record. JVTO-14: a derived-only set cannot be the sole evidence of a fact.
        if isinstance(source_refs, list) and source_refs:
            classes: set[str] = set()
            for ref in source_refs:
                for rule, message in source_ref_problems(ref):
                    errors.append({"rule": rule, "path": relative, "message": message})
                if isinstance(ref, dict):
                    classes.add(str(ref.get("source_class", "")))
            if derived_classes and classes and classes.issubset(derived_classes) and meta.get("claim_basis") != "planning_assumption":
                errors.append({"rule": "JVTO-14", "path": relative, "message": "Derived-only source_refs cannot be sole evidence (add a direct source or set claim_basis: planning_assumption)."})

        # JVTO-15: a Tour Package identity (package_key) must originate once.
        if ctype == "Tour Package":
            pkey = str(meta.get("package_key", "")).strip()
            if pkey:
                if pkey in seen_packages:
                    errors.append({"rule": "JVTO-15", "path": relative, "message": f"Duplicate Tour Package identity {pkey!r} (also in {seen_packages[pkey]})."})
                else:
                    seen_packages[pkey] = relative

        # JVTO-16: Review Platform observations, when present, carry a complete current observation.
        if ctype == "Review Platform" and meta.get("observations") is not None:
            obs = meta.get("observations") or {}
            current = obs.get("current") if isinstance(obs, dict) else None
            if not isinstance(current, dict) or any(not str(current.get(k, "")).strip() for k in ("rating", "count", "as_of", "source")):
                errors.append({"rule": "JVTO-16", "path": relative, "message": "Review Platform observations.current must carry rating, count, as_of, source."})

        for link in LINK.findall(body):
            if link.startswith(("https://", "http://", "mailto:", "#")):
                continue
            resolved = internal_target(path, link).resolve()
            if not resolved.is_relative_to(bundle_resolved):
                errors.append({"rule": "JVTO-10", "path": relative, "message": f"Internal link escapes the bundle: {link}"})
                continue
            if not resolved.exists():
                issue = {"rule": "OKF-03", "path": relative, "message": f"Broken internal link: {link}"}
                (errors if args.strict_links else warnings).append(issue)

    report = {
        "validated_at": utc_now(),
        "release_mode": args.release,
        "strict_links": args.strict_links,
        "errors": errors,
        "warnings": warnings,
        "clean": not errors,
    }
    write_json(BUILD_ROOT / "validation-report.json", report)
    print(f"Validation: {len(errors)} error(s), {len(warnings)} warning(s).")
    for issue in errors:
        print(f"ERROR {issue['rule']} {issue['path']}: {issue['message']}", file=sys.stderr)
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
