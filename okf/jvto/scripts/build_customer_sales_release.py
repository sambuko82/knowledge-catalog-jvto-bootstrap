"""Build the published Customer Sales Release (Milestone 1).

This is a NEW, separate publication artifact — NOT part of the OKF concept bundle under
`okf/bundles/jvto/` (which is built only by build_bundle.py and guarded for no-diff). The
Customer Sales Release is customer-facing sales content owned by this repo; it joins:

- approved public concepts in this repo (tour operationals, policies, destinations), and
- price-source evidence + canonical IDs/aliases/endpoint evidence from jvto-itinerary-core
  (read-only, via --core-root).

Per an explicit business decision, exact per-pax standard price tiers ARE published here.
The release excludes all supplier rates/costs/margins, internal-ops fields, and PII.

Output: okf/customer-sales-release/jvto/*.json  (deterministic; sorted keys).
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path
from typing import Any

from common import OKF_ROOT, BUNDLE_ROOT, parse_frontmatter, read_json, utc_now, write_json

DEFAULT_RELEASE_ID = "customer-sales-release-20260628-001"
RELEASE_SCHEMA = "customer-sales-release-v1"

CAPABILITIES = [
    "package_overview",
    "standard_price",
    "inclusions",
    "endpoint_chain",
    "rooming",
    "vehicle_luggage",
    "guide_support",
    "policy",
    "destination_guidance",
]

CORE_PRICING = "input/llm-wiki/package-readiness/package-pricing.json"
CORE_CATALOG_INDEX = "generated/itinerary-intelligence/package-catalog-index.json"
CORE_ROUTE_MAP = "generated/itinerary-intelligence/11-package-route-map.json"
CORE_DROPOFFS = "generated/itinerary-intelligence/02-dropoff-contexts.json"
CORE_ALIASES = "generated/itinerary-intelligence/location-alias-registry.json"
# Per-package classified standard route truth (valid pickups/dropoffs, structured
# Bali-transfer boundary, per-field classification). Projected VERBATIM — the runtime
# must never present a fact above the evidence class Core assigned it.
CORE_ROUTE_TRUTH = "generated/itinerary-intelligence/agent-contract/standard-route-truth.json"

# Tokens that must never appear in any emitted record (cost/margin/supplier/PII).
FORBIDDEN_SUBSTRINGS = (
    "driver_cost", "escort_cost", "supplier", "margin", "vendor", "profit",
    "backoffice_observed", "rate_idr", "cost_idr", "per_day", "price_per_day",
    "customer_email", "customer_phone", "passport", "payment_reference",
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_revision(root: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
        return out.stdout.strip()
    except Exception:
        return "unknown"


def _load_concept(rel_path: str) -> tuple[dict[str, Any], str]:
    front, body = parse_frontmatter((BUNDLE_ROOT / rel_path).read_text(encoding="utf-8"))
    return front, body.strip()


def _readiness(**flags: bool) -> dict[str, str]:
    return {cap: ("available" if flags.get(cap) else "unavailable") for cap in CAPABILITIES}


# Overnight sentinels that are NOT a lodging room (transit / day-trip).
NON_LODGING_OVERNIGHTS = {"no_overnight", "overnight_in_vehicle"}


def _dropoff_matches(option: str, ctx: dict[str, Any]) -> bool:
    """Precisely match a standard_dropoff_option string to one dropoff context.

    Avoids the broad location_group substring match that would, e.g., attach the
    train-station context to a package whose only options are Surabaya Airport/Hotel.
    """
    o = option.lower()
    typ = ctx.get("type", "")
    lg = (ctx.get("location_group") or "").lower()
    if typ == "airport":
        return "airport" in o and lg in o
    if typ == "hotel":
        return "hotel" in o and lg in o
    if typ == "harbor":
        return "ketapang" in o or "harbor" in o
    if typ == "bali_area":
        return "bali" in o or "gilimanuk" in o
    if typ == "train_station":
        return "train" in o or "station" in o
    if typ == "city_point":
        return bool(lg) and lg in o
    return False


def _base_inclusions(tokens: list[str], origin: str, ferry_included: bool) -> dict[str, Any]:
    included = [
        "private transport (dedicated vehicle)",
        "dedicated private driver and guide(s)",
        "all entrance fees and permits",
        "drinking water",
        "meals as stated in the itinerary",
        "full pick-up to drop-off assistance",
    ]
    if "bromo" in tokens:
        included.append("private 4WD jeep for Bromo")
    if "ijen" in tokens:
        included.extend(["gas masks and trekking poles for Ijen", "Ijen health-screening coordination where required"])
    if ferry_included or origin == "bali":
        included.append("ferry crossing (East Java – Bali)")
    return {
        "included": included,
        "excluded": ["international/domestic flights", "visas", "travel insurance", "tips", "personal expenses"],
        "conditional": ["meals not marked B/L/D on a given day", "optional add-ons outside the standard route"],
    }


def build(core_root: Path, release_id: str) -> dict[str, Any]:
    pricing = {row["package_id"]: row for row in read_json(core_root / CORE_PRICING)}
    catalog_index = {row["package_id"]: row for row in read_json(core_root / CORE_CATALOG_INDEX)}
    route_map = {row["package_id"]: row for row in read_json(core_root / CORE_ROUTE_MAP)}
    dropoffs = {row["id"]: row for row in read_json(core_root / CORE_DROPOFFS)}
    aliases_raw = read_json(core_root / CORE_ALIASES)
    route_truth = {p["package_key"]: p for p in read_json(core_root / CORE_ROUTE_TRUTH).get("packages", [])}

    catalog = read_json(BUNDLE_ROOT / "catalog.json")
    concepts = catalog.get("concepts", [])

    source_ref = {"release_id": release_id}

    profiles: list[dict[str, Any]] = []
    price_tiers: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []
    endpoints: list[dict[str, Any]] = []
    accommodation: list[dict[str, Any]] = []
    vehicle_luggage: list[dict[str, Any]] = []
    guide_support: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []

    for entry in concepts:
        if entry.get("type") != "Tour Package":
            continue
        front, _ = _load_concept(entry["path"])
        pkg = front.get("package_key")
        if not pkg:
            gaps.append({"package_key": None, "concept": entry["id"], "capability": "package_overview", "reason": "missing package_key"})
            continue
        op = front.get("operational", {}) or {}
        idx = catalog_index.get(pkg, {})
        tokens = idx.get("destination_tokens", []) or []
        origin = (idx.get("origin") or op.get("origin", "")).lower()
        price = pricing.get(pkg)
        ferry = bool(price.get("ferry_included")) if price else (origin == "bali")

        # --- package profile ---
        days = op.get("days", []) or []
        has_price = price is not None
        overnights = [d.get("overnight") for d in days if d.get("overnight") and d.get("overnight") not in NON_LODGING_OVERNIGHTS]
        profiles.append({
            **source_ref,
            "package_key": pkg,
            "itinerary_core_package_id": idx.get("package_id", pkg),
            "slug": idx.get("slug"),
            "title": entry.get("title"),
            "description": entry.get("description"),
            "origin": op.get("origin"),
            "duration": idx.get("duration"),
            "day_count": op.get("day_count"),
            "private": "no shared groups" in (op.get("crew_roles", "")).lower(),
            "destination_tokens": tokens,
            "public_url": idx.get("public_url"),
            "day_titles": [{"day": d.get("day"), "title": d.get("title"), "meals": d.get("meals", []) or []} for d in days],
            "source_evidence": ["knowledge:" + entry["path"], "core:" + CORE_CATALOG_INDEX],
            "readiness": _readiness(package_overview=True),
        })

        # --- standard price tiers ---
        if has_price:
            price_tiers.append({
                **source_ref,
                "package_key": pkg,
                "price_type": "published_standard",
                "currency": price.get("currency", "IDR"),
                "ferry_included": ferry,
                "pax_tiers": price.get("pax_tiers", []),
                "min_pax": min((t["min_pax"] for t in price.get("pax_tiers", [])), default=None),
                "availability": "needs_live_confirmation",
                "source_evidence": ["core:" + CORE_PRICING],
                "readiness": {"standard_price": "available"},
            })
        else:
            gaps.append({"package_key": pkg, "capability": "standard_price", "reason": "no published price tier in source"})

        # --- component matrix (inclusions/exclusions) ---
        components.append({
            **source_ref,
            "package_key": pkg,
            **_base_inclusions(tokens, origin, ferry),
            "source_evidence": ["knowledge:policies/inclusions-exclusions"],
            "readiness": {"inclusions": "available"},
        })

        # --- endpoint chain ---
        # Join by exact package_key first. Bali-origin keys use a "<slug>-bali" route-map
        # variant; do NOT fall back to the bare slug for them (it collides with the
        # Surabaya variant of the same slug and would assign the wrong dropoffs).
        slug = idx.get("slug") or pkg
        rm_candidates = [pkg, f"{slug}-bali"] if pkg.startswith("bali/") else [pkg, slug]
        rm = next((route_map[c] for c in rm_candidates if c in route_map), {})
        options = rm.get("standard_dropoff_options", []) or []
        finish_details = []
        for ctx_id, ctx in dropoffs.items():
            if any(_dropoff_matches(opt, ctx) for opt in options):
                finish_details.append({"id": ctx_id, "label": ctx.get("label"), "type": ctx.get("type"),
                                       "connects_to": ctx.get("connects_to", []), "required_customer_fields": ctx.get("required_customer_fields", [])})
        # Classified truth from Core (verbatim): valid pickups, classified endpoint options,
        # and the structured Bali-transfer boundary. The old free-text "finish in Bali" note
        # was mis-applied to Bali-ORIGIN packages that actually finish in Surabaya; the
        # boundary is now direction-aware (from_bali / to_bali / both / none).
        rt = route_truth.get(pkg, {})
        pickup_options = rt.get("valid_pickups", [])
        endpoint_options = rt.get("valid_dropoffs", [])
        bali_transfer = rt.get("bali_transfer")
        note = bali_transfer.get("note") if bali_transfer else None
        endpoints.append({
            **source_ref,
            "package_key": pkg,
            "origin": op.get("origin"),
            "ferry_included": ferry,
            "standard_pickup_options": [p.get("label") for p in pickup_options],
            "pickup_details": pickup_options,
            "standard_dropoff_options": options,
            "finish_details": finish_details,
            "endpoint_options": endpoint_options,
            "bali_transfer": bali_transfer,
            "note": note,
            "source_evidence": ["core:" + CORE_ROUTE_MAP, "core:" + CORE_DROPOFFS, "core:" + CORE_ROUTE_TRUTH],
            "readiness": {
                "endpoint_chain": "available" if options else "unavailable",
                "pickup_options": "available" if pickup_options else "unavailable",
            },
        })
        if not options:
            gaps.append({"package_key": pkg, "capability": "endpoint_chain", "reason": "no standard_dropoff_options in route map"})
        if not pickup_options:
            gaps.append({"package_key": pkg, "capability": "pickup_options", "reason": "no valid_pickups in core standard-route-truth"})

        # --- accommodation rules (named overnights only; no supplier rates) ---
        accommodation.append({
            **source_ref,
            "package_key": pkg,
            "overnights": overnights,
            "rooming_assumption": "standard rooming per the package; twin/double or extra room on request (subject to confirmation)",
            "source_evidence": ["knowledge:" + entry["path"]],
            "readiness": {"rooming": "available" if overnights else "unavailable"},
        })
        if not overnights:
            gaps.append({"package_key": pkg, "capability": "rooming", "reason": "no named overnights (e.g. day-trip)"})

        # --- vehicle + luggage ---
        vehicle_luggage.append({
            **source_ref,
            "package_key": pkg,
            "vehicle_category": op.get("vehicle_category"),
            "luggage_rule": None,
            "source_evidence": ["knowledge:" + entry["path"]],
            "readiness": {"vehicle_luggage": "available" if op.get("vehicle_category") else "unavailable"},
        })
        gaps.append({"package_key": pkg, "capability": "vehicle_luggage", "reason": "luggage allowance not published (vehicle class available)"})

        # --- guide support ---
        guide_support.append({
            **source_ref,
            "package_key": pkg,
            "crew_roles": op.get("crew_roles"),
            "language_note": "English-speaking driver/guide standard; other languages subject to confirmation",
            "source_evidence": ["knowledge:" + entry["path"]],
            "readiness": {"guide_support": "available" if op.get("crew_roles") else "unavailable"},
        })

    # --- policy cards ---
    policy_cards = []
    for entry in concepts:
        if entry.get("type") != "Policy":
            continue
        _, body = _load_concept(entry["path"])
        policy_cards.append({**source_ref, "id": entry["id"], "title": entry.get("title"),
                             "description": entry.get("description"), "body": body,
                             "source_evidence": ["knowledge:" + entry["path"]], "readiness": {"policy": "available"}})

    # --- destination guidance ---
    destination_guidance = []
    for entry in concepts:
        if entry.get("type") != "Destination":
            continue
        front, body = _load_concept(entry["path"])
        activity = front.get("activity", {}) or {}
        destination_guidance.append({**source_ref, "id": entry["id"], "title": entry.get("title"),
                                     "description": entry.get("description"),
                                     "typical_schedule": activity.get("typical_schedule"),
                                     "effort": activity.get("effort"),
                                     "access_requirements": activity.get("access_requirements", []) or [],
                                     "source_evidence": ["knowledge:" + entry["path"]], "readiness": {"destination_guidance": "available"}})

    # --- location aliases ---
    location_aliases = sorted(
        ({"node_id": a.get("node_id"), "aliases": a.get("aliases", []) or []} for a in aliases_raw if a.get("node_id")),
        key=lambda a: a["node_id"],
    )

    objects = {
        "package-profiles.json": sorted(profiles, key=lambda r: r["package_key"]),
        "standard-price-tiers.json": sorted(price_tiers, key=lambda r: r["package_key"]),
        "component-matrices.json": sorted(components, key=lambda r: r["package_key"]),
        "endpoint-chains.json": sorted(endpoints, key=lambda r: r["package_key"]),
        "accommodation-rules.json": sorted(accommodation, key=lambda r: r["package_key"]),
        "vehicle-and-luggage-rules.json": sorted(vehicle_luggage, key=lambda r: r["package_key"]),
        "guide-support-rules.json": sorted(guide_support, key=lambda r: r["package_key"]),
        "policy-cards.json": sorted(policy_cards, key=lambda r: r["id"]),
        "destination-guidance.json": sorted(destination_guidance, key=lambda r: r["id"]),
        "location-aliases.json": location_aliases,
    }

    # --- coverage report (per-capability availability across packages) ---
    package_keys = [p["package_key"] for p in profiles]
    capability_counts = {cap: 0 for cap in CAPABILITIES}
    for p in profiles:
        capability_counts["package_overview"] += 1
    capability_counts["standard_price"] = len(price_tiers)
    capability_counts["inclusions"] = len(components)
    capability_counts["endpoint_chain"] = sum(1 for e in endpoints if e["readiness"]["endpoint_chain"] == "available")
    capability_counts["rooming"] = sum(1 for a in accommodation if a["readiness"]["rooming"] == "available")
    capability_counts["vehicle_luggage"] = sum(1 for v in vehicle_luggage if v["readiness"]["vehicle_luggage"] == "available")
    capability_counts["guide_support"] = sum(1 for g in guide_support if g["readiness"]["guide_support"] == "available")
    capability_counts["policy"] = len(policy_cards)
    capability_counts["destination_guidance"] = len(destination_guidance)

    coverage = {
        "release_id": release_id,
        "package_count": len(package_keys),
        "object_counts": {name: len(payload) for name, payload in objects.items()},
        "capability_packages_available": capability_counts,
        "capability_readiness": {
            "package_overview": "available", "standard_price": "available", "inclusions": "available",
            "endpoint_chain": "available", "rooming": "available", "vehicle_luggage": "partial",
            "guide_support": "available", "policy": "available", "destination_guidance": "available",
        },
        "notes": ["luggage allowance is not published (vehicle class is); see gap-report.json"],
    }
    gap_report = {"release_id": release_id, "gap_count": len(gaps), "gaps": sorted(gaps, key=lambda g: (g.get("package_key") or "", g["capability"]))}

    return {"objects": objects, "coverage": coverage, "gap_report": gap_report, "package_keys": package_keys}


def main() -> None:
    parser = argparse.ArgumentParser(prog="build_customer_sales_release")
    parser.add_argument("--core-root", required=True, help="Path to a local jvto-itinerary-core checkout")
    parser.add_argument("--release-id", default=DEFAULT_RELEASE_ID)
    parser.add_argument("--out", default=str(OKF_ROOT / "customer-sales-release" / "jvto"))
    args = parser.parse_args()

    core_root = Path(args.core_root).resolve()
    out_dir = Path(args.out)
    built = build(core_root, args.release_id)

    for name, payload in built["objects"].items():
        write_json(out_dir / name, payload)
    write_json(out_dir / "coverage-report.json", built["coverage"])
    write_json(out_dir / "gap-report.json", built["gap_report"])

    source_lock = {
        "schema_version": "customer-sales-source-lock-v1",
        "release_id": args.release_id,
        "created_at": utc_now(),
        "knowledge_catalog": {
            "repo": "sambuko82/knowledge-catalog-jvto-bootstrap",
            "revision": _git_revision(OKF_ROOT.parent),
            "catalog_path": "okf/bundles/jvto/catalog.json",
            "catalog_sha256": _sha256_file(BUNDLE_ROOT / "catalog.json"),
        },
        "itinerary_core": {
            "repo": "sambuko82/jvto-itinerary-core",
            "revision": _git_revision(core_root),
            "sources": {rel: _sha256_file(core_root / rel) for rel in [CORE_PRICING, CORE_CATALOG_INDEX, CORE_ROUTE_MAP, CORE_DROPOFFS, CORE_ALIASES, CORE_ROUTE_TRUTH]},
        },
    }
    write_json(out_dir / "source-lock.json", source_lock)

    manifest = {
        "schema_version": RELEASE_SCHEMA,
        "release_id": args.release_id,
        "created_at": utc_now(),
        "customer_traffic_ready": False,
        "package_count": built["coverage"]["package_count"],
        "object_counts": built["coverage"]["object_counts"],
        "capability_readiness": built["coverage"]["capability_readiness"],
        "price_published": True,
        "price_note": "Exact per-pax standard price tiers are published (business-approved). Availability still requires live confirmation.",
        "excluded": ["supplier rates", "internal costs", "margin", "vendor allocation", "PII"],
    }
    write_json(out_dir / "release-manifest.json", manifest)
    print(f"Customer Sales Release written to {out_dir} ({built['coverage']['package_count']} packages)")


if __name__ == "__main__":
    main()
