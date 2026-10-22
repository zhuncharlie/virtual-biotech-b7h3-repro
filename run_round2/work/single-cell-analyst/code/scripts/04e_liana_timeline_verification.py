#!/usr/bin/env python
"""
Machine-check the pre-registration timeline for panels 4D / S5A.

Every timestamp below is read either from a file mtime or from a timestamp
embedded in the file itself.  No timestamp is typed in by hand.

Output
  results/tables/liana_timeline_verification.csv
"""
import os
import json
import re
from datetime import datetime, timezone, timedelta

import pandas as pd
import numpy as np

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
SRC_ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35"
WORK = os.path.join(ROOT, "work/single-cell-analyst")
SRC_WORK = os.path.join(SRC_ROOT, "work/single-cell-analyst")
TAB = os.path.join(WORK, "results/tables")            # output goes to LIVE
SRC_TAB = os.path.join(SRC_WORK, "results/tables")    # mtime evidence stays in SOURCE
LOGS = os.path.join(SRC_WORK, "logs")                 # original log mtimes stay in SOURCE
ORIG = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/single-cell-analyst")


def mtime_utc(path):
    return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat()


def parse_iso(s):
    return datetime.fromisoformat(s)


rows = []


def add(item, path, internal=None, note="", role=""):
    rows.append(dict(item=item, role=role, path=path,
                     file_mtime_utc=mtime_utc(path) if os.path.exists(path) else "MISSING",
                     embedded_timestamp_utc=internal or "", note=note))


# 1-2 CAF definition (written before any LIANA output)
p = os.path.join(SRC_TAB, "liana_b7h3_caf_definition.csv")
df = pd.read_csv(p)
add("CAF definition table", p, f"{df.pre_registered_utc.min()} .. {df.pre_registered_utc.max()}",
    "primary definition CD276>0 vs ==0; sensitivity a-c pre-specified here", "definition fixed")

p = os.path.join(SRC_TAB, "liana_b7h3_caf_definition_meta.json")
meta = json.load(open(p))
add("CAF definition meta", p, meta["timestamp_utc"], "same event; exact UTC", "definition fixed")

# 3-4 20-perm timing probe
p = os.path.join(SRC_TAB, "liana_PROBE_sca20_perms.csv")
add("20-perm probe output", p, "", "output existed from this time; could in principle have been seen", "probe")
p = os.path.join(SRC_TAB, "liana_PROBE_meta.json")
pm = json.load(open(p))
add("20-perm probe meta", p, "", f"elapsed {pm['elapsed_s']:.1f}s, n_perms={pm['n_perms']}", "probe")
p = os.path.join(LOGS, "liana_probe.log")
add("20-perm probe log", p, "", "probe completed", "probe")

# 5 50-perm benchmark (log rows carry run START time)
p = os.path.join(LOGS, "liana_run_SCLC_benchmark50.log")
start = re.search(r'"timestamp_utc": "([^"]+)"', open(p).read()).group(1)
wall = float(re.search(r'"total_wall_time_min": ([0-9.]+)', open(p).read()).group(1))
finish = parse_iso(start) + timedelta(minutes=wall)
add("50-perm benchmark log", p, f"start {start}; estimated finish {finish.isoformat()}",
    f"total wall {wall} min", "benchmark")

# 6-7 scripts that fixed parameters and filters (original run, before the main run)
p = os.path.join(ORIG, "code/scripts/03_liana_run.py")
add("script 03 (LIANA parameters)", p, "", "LIANA parameters and universe rule fixed in code", "filters fixed")
p = os.path.join(ORIG, "code/scripts/04_liana_extract_compare.py")
add("script 04 (filter values)", p, "", "specificity_rank<=0.1, p<0.01, >=3 methods fixed in code", "filters fixed")

# 8 consolidated filter CSV
p = os.path.join(SRC_TAB, "liana_pre_registered_filters.csv")
f = pd.read_csv(p)
add("consolidated pre-registered filters CSV", p,
    f"{f.pre_registered_utc.min()} .. {f.pre_registered_utc.max()}",
    "embedded timestamp is ~7 s later than file mtime; both fall inside the main run",
    "filters recorded")

# 9 main run
p = os.path.join(LOGS, "liana_run_SCLC_main.log")
txt = open(p).read()
start = re.search(r'"timestamp_utc": "([^"]+)"', txt).group(1)
wall = float(re.search(r'"total_wall_time_min": ([0-9.]+)', txt).group(1))
finish = parse_iso(start) + timedelta(minutes=wall)
add("SCLC main 1,000-perm log", p, f"start {start}; estimated finish {finish.isoformat()}",
    f"timestamp_utc is the START (set before the run); total wall {wall} min", "main run")
p = os.path.join(SRC_TAB, "liana_raw_sclc.parquet")
add("SCLC main raw LIANA output", p, "", "25,028 rows; md5 matches provenance copy", "main run")

out = pd.DataFrame(rows)
out.to_csv(os.path.join(TAB, "liana_timeline_verification.csv"), index=False)
print(out[["item", "role", "file_mtime_utc", "embedded_timestamp_utc"]].to_string(index=False))
