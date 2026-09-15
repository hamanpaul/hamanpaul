#!/usr/bin/env python3
"""Freeze inspected PUBLIC repository READMEs; never publish private source.

This explicit refresh command is not run by the normal architecture verifier.
A changed README blob stops the refresh instead of silently changing facts.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def api(path: str):
    headers = {"User-Agent": "hamanpaul-architecture-evidence", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request("https://api.github.com/" + path, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)

def main() -> None:
    lock = json.loads((ROOT / "docs/source-lock.json").read_text())
    manifest = {"schema_version": 1, "scope": "Public README declarations, not runtime E2E proof", "sources": []}
    pending = []
    for slug, expected in sorted(lock["sources"].items()):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", slug) or not re.fullmatch(r"[0-9a-f]{40}", expected):
            raise ValueError("Invalid repository or blob pin")
        name = "hamanpaul/" + slug
        meta = api("repos/" + name)
        if meta.get("private") is not False or meta.get("visibility") != "public":
            raise RuntimeError(name + ": refusing to export non-public source")
        branch = meta["default_branch"]
        ref = api("repos/" + name + "/git/ref/heads/" + branch)
        revision = ref["object"]["sha"]
        obj = api("repos/" + name + "/contents/README.md?ref=" + revision)
        data = base64.b64decode(obj["content"], validate=False)
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if obj["sha"] != expected or blob != expected:
            raise RuntimeError(name + ": inspected README changed; reread before refreshing")
        data.decode("utf-8")
        path = "docs/evidence/" + slug + "/README.md"
        pending.append((path, data))
        manifest["sources"].append({"repository": name, "revision": revision, "path": "README.md", "blob_sha": blob, "sha256": hashlib.sha256(data).hexdigest(), "snapshot": path, "url": "https://github.com/" + name + "/blob/" + revision + "/README.md", "visibility": "public"})
    for path, data in pending:
        dest = ROOT / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    (ROOT / "docs/source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Frozen public sources:", len(pending))

if __name__ == "__main__":
    main()
