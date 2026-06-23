#!/usr/bin/env python3
"""Fetch only allow-listed upstream files into local uncommitted snapshots."""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

from common import CONFIG_ROOT, SNAPSHOT_ROOT, read_yaml, sha256_bytes, utc_now, write_json


def raw_url(repo: str, ref: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"


def fetch(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "jvto-okf-snapshot-fetcher/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_ROOT / "upstreams.yaml")
    parser.add_argument("--strict", action="store_true", help="Fail on optional source-fetch errors too.")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    config = read_yaml(args.config)
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    manifest: dict = {"fetched_at": utc_now(), "sources": {}, "errors": errors}

    for name, source in (config.get("upstreams") or {}).items():
        records = []
        forbidden = tuple(source.get("forbidden_prefixes") or [])
        for file_spec in source.get("files") or []:
            path = str(file_spec["path"])
            required = bool(file_spec.get("required", False))
            if path.startswith(forbidden):
                message = f"{name}:{path}: path violates source boundary"
                records.append({"path": path, "status": "blocked", "error": message})
                errors.append(message)
                continue
            url = raw_url(str(source["repo"]), str(source["ref"]), path)
            target = SNAPSHOT_ROOT / name / path
            try:
                data = fetch(url, args.timeout)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                records.append({"path": path, "url": url, "mode": file_spec.get("mode"), "required": required, "status": "fetched", "bytes": len(data), "sha256": sha256_bytes(data)})
                print(f"fetched {name}:{path}")
            except urllib.error.HTTPError as exc:
                message = f"{name}:{path}: HTTP {exc.code}"
                records.append({"path": path, "url": url, "status": "error", "required": required, "error": message})
                if required or args.strict:
                    errors.append(message)
                print(message, file=sys.stderr)
            except Exception as exc:  # noqa: BLE001
                message = f"{name}:{path}: {type(exc).__name__}: {exc}"
                records.append({"path": path, "url": url, "status": "error", "required": required, "error": message})
                if required or args.strict:
                    errors.append(message)
                print(message, file=sys.stderr)
        manifest["sources"][name] = {"repo": source["repo"], "ref": source["ref"], "files": records}

    write_json(SNAPSHOT_ROOT / "_snapshot_manifest.json", manifest)
    if errors:
        print(f"Snapshot fetch finished with {len(errors)} blocking error(s).", file=sys.stderr)
        return 2
    print("Snapshot fetch completed successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
