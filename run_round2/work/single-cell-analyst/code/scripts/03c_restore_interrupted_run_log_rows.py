#!/usr/bin/env python
"""
Restore the SCLC benchmark50 and main rows into this run's liana_run_log.csv.

The rows were written by the interrupted run 20261021-080518.  The copy carried
into this run was 0 bytes, so only the reconstructed LUAD row was present.
This script prepends the original rows verbatim (adding a `fix` note) and keeps
the reconstructed LUAD row.  No result value is modified.
"""
import os
import pandas as pd

ROOT = "/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/20261021-204038-round-2-of-the-b7-h3-cd276-case-a9b7a6f8"
WORK = os.path.join(ROOT, "work/single-cell-analyst")
TAB = os.path.join(WORK, "results/tables")
LOG = os.path.join(TAB, "liana_run_log.csv")
ORIG = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
        "20261021-080518-round-2-of-the-b7-h3-cd276-lung-27ef6dcf/work/single-cell-analyst/"
        "results/tables/liana_run_log.csv")

if __name__ == "__main__":
    old = pd.read_csv(ORIG)
    old["fix"] = ("row restored from interrupted run 20261021-080518; the copy in this run "
                  "was 0 bytes so the row was absent here")
    cur = pd.read_csv(LOG)
    out = pd.concat([old, cur], ignore_index=True)
    out = out.drop_duplicates(subset=["timestamp_utc", "disease", "run_tag"], keep="first")
    out.to_csv(LOG, index=False)
    print(out[["timestamp_utc", "disease", "run_tag", "status", "n_perms",
               "n_interactions_raw", "fix"]].to_string(index=False))
