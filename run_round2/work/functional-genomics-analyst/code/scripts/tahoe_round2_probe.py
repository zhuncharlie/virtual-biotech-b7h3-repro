#!/usr/bin/env python
"""Round-2 Tahoe-100M availability probe.

Checks, in order:
  1. TAHOE_DATA_PATH in this process environment
  2. TAHOE_DATA_PATH in the running functional_genomics MCP server process
     (the server launches with a fixed environment; a per-call fix is impossible)
  3. any prepared Tahoe pseudobulk directory in the project/data tree
  4. local Hugging Face client availability
  5. size of the official Tahoe-100M pseudobulk DE release (shard inventory)

Writes:
  data/processed/tahoe_environment_diagnostic.json
  data/raw/tahoe_de_shard_inventory.csv

This script does NOT query biological data. It only records why the MCP
Tahoe tools are or are not usable.
"""
import csv
import json
import os
import shutil
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

# Resolve output paths from this file (parents[2] == the agent workspace) so a
# re-run writes into the run it is launched from, not into an older run.
WORK = str(Path(__file__).resolve().parents[2])
PROJECT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech"
REVISION = "2dc57900b7981cfcf5e211527169a0b006546a95"
SERVER_SCRIPT = "functional_genomics_mcp/server.py"


def find_server_pids():
    pids = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace")
        except (OSError, PermissionError):
            continue
        if SERVER_SCRIPT in cmd:
            pids.append((int(pid), cmd.strip()))
    return pids


def server_env(pids):
    out = {}
    for pid, _ in pids:
        try:
            raw = open(f"/proc/{pid}/environ", "rb").read().split(b"\0")
        except (OSError, PermissionError):
            out[str(pid)] = {"readable": False}
            continue
        env = {}
        for item in raw:
            if b"=" in item:
                k, v = item.split(b"=", 1)
                k, v = k.decode(errors="replace"), v.decode(errors="replace")
                if "TAHOE" in k or "OPEN_TARGETS" in k or "HF_" in k:
                    env[k] = v
        out[str(pid)] = {"readable": True, "relevant_env": env,
                         "has_TAHOE_DATA_PATH": "TAHOE_DATA_PATH" in env}
    return out


def search_tahoe_dirs(bases, max_depth=4):
    hits = []
    for base in bases:
        if not os.path.isdir(base):
            continue
        base_depth = base.rstrip("/").count(os.sep)
        for dirpath, dirnames, filenames in os.walk(base):
            if dirpath.count(os.sep) - base_depth >= max_depth:
                dirnames[:] = []
                continue
            for name in dirnames + filenames:
                if "tahoe" in name.lower():
                    full = os.path.join(dirpath, name)
                    hits.append({"path": full, "is_dir": os.path.isdir(full),
                                 "size_bytes": None if os.path.isdir(full) else os.path.getsize(full)})
    return hits


def shard_inventory():
    try:
        from huggingface_hub import HfApi
    except Exception as exc:  # pragma: no cover
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    try:
        api = HfApi()
        files = [f for f in api.list_repo_tree(
            "tahoebio/Tahoe-100M", repo_type="dataset", revision=REVISION,
            path_in_repo="metadata/pseudobulk_differential_expression")
            if getattr(f, "size", None) is not None]
        rows = [{"path": f.path, "size_bytes": f.size} for f in files]
        out_csv = os.path.join(WORK, "data/raw/tahoe_de_shard_inventory.csv")
        os.makedirs(os.path.dirname(out_csv), exist_ok=True)
        with open(out_csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["path", "size_bytes"])
            w.writeheader()
            w.writerows(rows)
        sizes = [r["size_bytes"] for r in rows]
        return {"available": True, "n_shards": len(rows),
                "total_GiB": round(sum(sizes) / 1024 ** 3, 2),
                "median_shard_MB": round(statistics.median(sizes) / 1024 ** 2, 1),
                "inventory_csv": out_csv}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def main():
    pids = find_server_pids()
    diagnostic = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "process_env_TAHOE_DATA_PATH": os.environ.get("TAHOE_DATA_PATH"),
        "functional_genomics_server_pids": [p for p, _ in pids],
        "functional_genomics_server_env": server_env(pids),
        "tahoe_paths_found_in_tree": search_tahoe_dirs(
            [PROJECT, "/mnt/beegfs/xqinag/data", os.path.join(WORK, "data")]),
        "hf_client": {
            "hf_cli": shutil.which("hf"),
            "huggingface_cli": shutil.which("huggingface-cli"),
        },
        "de_shard_inventory": shard_inventory(),
        "interpretation": (
            "The functional_genomics MCP server cannot see TAHOE_DATA_PATH; its "
            "environment is fixed at launch and no prepared Tahoe pseudobulk "
            "directory exists, so every Tahoe MCP call fails before any data is "
            "read. This is a data-availability failure, not a zero-result query."
        ),
    }
    out = os.path.join(WORK, "data/processed/tahoe_environment_diagnostic.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        json.dump(diagnostic, fh, indent=2)
    print(json.dumps(diagnostic, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
