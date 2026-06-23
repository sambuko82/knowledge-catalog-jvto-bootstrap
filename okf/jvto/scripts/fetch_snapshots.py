#!/usr/bin/env python3
"""Fetch only allow-listed upstream files into local uncommitted snapshots.

Two modes:

  remote (default)  Download via raw.githubusercontent.com. The upstream repo
                    must be reachable anonymously (public) or through a
                    pre-authenticated proxy.

  local  (--local)  Copy from local clones already on disk. Use this when an
                    upstream must stay private (e.g. llm-wiki holds non-public
                    finance/raw data) or when working offline. Each upstream's
                    clone root is resolved from the environment variable
                    JVTO_OKF_LOCAL_<KEY_UPPER> (e.g. JVTO_OKF_LOCAL_LLM_WIKI),
                    falling back to a `local_path` entry in upstreams.yaml.

Either way only the allow-listed paths are read and the same snapshot layout,
allow-list, forbidden-prefix guard, and manifest are produced, so build and
validate stay unchanged.
"""
from __future__ import annotations

import argparse
import os
import subprocess
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


def read_local(base: Path, path: str) -> bytes:
    return (base / path).read_bytes()


def local_root_for(name: str, source: dict, config_dir: Path) -> Path | None:
    """Resolve an upstream's local clone root from env var or config `local_path`."""
    raw = os.environ.get(f"JVTO_OKF_LOCAL_{name.upper()}") or source.get("local_path")
    if not raw:
        return None
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = (config_dir / candidate).resolve()
    return candidate


def git_commit(root: Path) -> str | None:
    """Best-effort provenance: the HEAD commit of a local clone, if it is a repo."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:  # noqa: BLE001
        return None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", type=Path, default=CONFIG_ROOT / "upstreams.yaml")
    parser.add_argument("--local", action="store_true", help="Copy from local clones instead of downloading.")
    parser.add_argument("--strict", action="store_true", help="Fail on optional source-fetch errors too.")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    config = read_yaml(args.config)
    config_dir = args.config.resolve().parent
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    manifest: dict = {
        "fetched_at": utc_now(),
        "mode": "local" if args.local else "remote",
        "sources": {},
        "errors": errors,
    }

    for name, source in (config.get("upstreams") or {}).items():
        records: list[dict] = []
        forbidden = tuple(source.get("forbidden_prefixes") or [])
        files = source.get("files") or []
        has_required = any(f.get("required") for f in files)
        local_root: Path | None = None
        local_commit: str | None = None

        if args.local:
            local_root = local_root_for(name, source, config_dir)
            if local_root is None or not local_root.exists():
                message = (
                    f"{name}: local clone root not found "
                    f"(set JVTO_OKF_LOCAL_{name.upper()} or local_path in upstreams.yaml)"
                )
                records.append({"path": "*", "status": "error", "error": message})
                if has_required or args.strict:
                    errors.append(message)
                print(message, file=sys.stderr)
                manifest["sources"][name] = {
                    "repo": source.get("repo"),
                    "ref": source.get("ref"),
                    "local": True,
                    "local_root": str(local_root) if local_root else None,
                    "files": records,
                }
                continue
            local_commit = git_commit(local_root)

        for file_spec in files:
            path = str(file_spec["path"])
            required = bool(file_spec.get("required", False))
            if path.startswith(forbidden):
                message = f"{name}:{path}: path violates source boundary"
                records.append({"path": path, "status": "blocked", "error": message})
                errors.append(message)
                print(message, file=sys.stderr)
                continue
            target = SNAPSHOT_ROOT / name / path
            try:
                if args.local:
                    origin = str(local_root / path)
                    data = read_local(local_root, path)  # type: ignore[arg-type]
                else:
                    origin = raw_url(str(source["repo"]), str(source["ref"]), path)
                    data = fetch(origin, args.timeout)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                records.append({
                    "path": path,
                    "source": origin,
                    "mode": file_spec.get("mode"),
                    "required": required,
                    "status": "fetched",
                    "bytes": len(data),
                    "sha256": sha256_bytes(data),
                })
                print(f"fetched {name}:{path}")
            except urllib.error.HTTPError as exc:
                message = f"{name}:{path}: HTTP {exc.code}"
                records.append({"path": path, "status": "error", "required": required, "error": message})
                if required or args.strict:
                    errors.append(message)
                print(message, file=sys.stderr)
            except FileNotFoundError:
                message = f"{name}:{path}: not found in local clone"
                records.append({"path": path, "status": "error", "required": required, "error": message})
                if required or args.strict:
                    errors.append(message)
                print(message, file=sys.stderr)
            except Exception as exc:  # noqa: BLE001
                message = f"{name}:{path}: {type(exc).__name__}: {exc}"
                records.append({"path": path, "status": "error", "required": required, "error": message})
                if required or args.strict:
                    errors.append(message)
                print(message, file=sys.stderr)

        manifest["sources"][name] = {
            "repo": source.get("repo"),
            "ref": source.get("ref"),
            "local": args.local,
            "local_root": str(local_root) if local_root else None,
            "local_commit": local_commit,
            "files": records,
        }

    write_json(SNAPSHOT_ROOT / "_snapshot_manifest.json", manifest)
    if errors:
        print(f"Snapshot fetch finished with {len(errors)} blocking error(s).", file=sys.stderr)
        return 2
    print("Snapshot fetch completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
