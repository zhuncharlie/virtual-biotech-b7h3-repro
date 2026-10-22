"""
Annotate the reconstructed Census batch log and re-derive what is derivable.

Why this exists
---------------
`results/tables/scrna_census_batch_log.csv` was not captured from the tool. It
was written by `source_04_write_batch_log_reference.py`, which hardcodes the b1
row, takes b2/b3 cell counts from `n_cells_expected` in
`data/raw/metadata/luad_batch_definitions.csv`, hardcodes file sizes
(613.15 / 568.37 MB) and asserts `retry_count = 0`. The numbers are consistent
with the merge log, but the file is a reconstruction, not a record of what the
Census tool returned.

This script:
  1. reads the batch log and the predecessor merge log (read-only);
  2. re-derives each batch's returned cell count from the merge log's loaded
     shape -- the only surviving independent evidence;
  3. asserts the log's counts equal those shapes;
  4. adds explicit provenance columns so no reader mistakes the log for a raw
     tool record.

File sizes cannot be re-derived: the batch h5ad files no longer exist anywhere
in the run tree, so the sizes are hardcoded and flagged unverifiable.

Output
------
results/tables/scrna_census_batch_log.csv  (same rows + 4 provenance columns)
"""
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visium_c2l_common import WORK, log_run, checked_frame  # noqa: E402

LOG_CSV = f"{WORK}/results/tables/scrna_census_batch_log.csv"
MERGE_LOG = ("/mnt/beegfs/xqinag/projects/TheVirtualBiotech/runs/"
             "20261021-113551-round-2-of-the-b7-h3-cd276-case-ef6e8b35/work/"
             "single-cell-analyst/logs/03_merge_qc_downsample.log")

if not os.path.exists(MERGE_LOG):
    raise FileNotFoundError(f"merge log not found (read-only evidence): {MERGE_LOG}")

bl = pd.read_csv(LOG_CSV)
assert len(bl) == 3 and set(bl["batch_id"]) == {"b1", "b2", "b3"}, bl.shape

# "batch01_576f193c_all.h5ad (90384, 61497) obs_names unique: True"
pat = re.compile(r"^(batch0(\d)_\S+\.h5ad)\s+\((\d+),\s+(\d+)\)")
derived = {}
with open(MERGE_LOG) as fh:
    for line in fh:
        m = pat.match(line.strip())
        if m:
            derived[f"b{int(m.group(2))}"] = {
                "merge_log_file": m.group(1),
                "merge_log_n_cells": int(m.group(3)),
                "merge_log_n_genes": int(m.group(4)),
            }
assert set(derived) == {"b1", "b2", "b3"}, f"merge-log batches: {sorted(derived)}"

rows = []
for _, r in bl.iterrows():
    b = r["batch_id"]
    d = derived[b]
    n_log = int(r["n_cells_returned"])
    assert n_log == d["merge_log_n_cells"], (
        f"{b}: log says {n_log}, merge log loaded {d['merge_log_n_cells']}")
    assert int(r["n_cells_estimated"]) == n_log, f"{b}: estimate != returned"
    rows.append({
        "batch_id": b, "dataset_id": r["dataset_id"],
        "disease_scope": r["disease_scope"], "value_filter": r["value_filter"],
        "columns": r["columns"], "layer": r["layer"],
        "n_cells_estimated": int(r["n_cells_estimated"]),
        "n_cells_returned": n_log,
        "n_genes_loaded": d["merge_log_n_genes"],
        "file_size_mb": float(r["file_size_mb"]),
        "success": bool(r["success"]), "retry_count": int(r["retry_count"]),
        "notes": r["notes"],
        "record_type": ("reconstructed: not captured from the tool; written by "
                        "source_04_write_batch_log_reference.py"),
        "cell_count_source": ("n_cells_expected in luad_batch_definitions.csv; "
                              "independently confirmed against merge-log shape"),
        "cell_count_confirmed_by": (f"{os.path.basename(MERGE_LOG)} line "
                                    f"{d['merge_log_file']} -> {n_log} cells"),
        "file_size_source": ("hardcoded; batch h5ad no longer exists, size not "
                             "re-derivable"),
        "retry_count_source": "hardcoded (asserted 0); no retry log survives",
    })

COLS = ["batch_id", "dataset_id", "disease_scope", "value_filter", "columns",
        "layer", "n_cells_estimated", "n_cells_returned", "n_genes_loaded",
        "file_size_mb", "success", "retry_count", "notes", "record_type",
        "cell_count_source", "cell_count_confirmed_by", "file_size_source",
        "retry_count_source"]
out = checked_frame(rows, COLS, "scrna_census_batch_log")
assert len(out) == 3
assert out["n_genes_loaded"].eq(61497).all()
assert out["n_cells_returned"].sum() == 502306, out["n_cells_returned"].sum()
out.to_csv(LOG_CSV, index=False)

print(out[["batch_id", "n_cells_returned", "n_genes_loaded", "file_size_mb",
           "cell_count_confirmed_by"]].to_string(index=False), flush=True)
log_run(step="census_batch_log_annotation", status="ok",
        detail=("Batch log marked as reconstructed; cell counts re-derived from "
                "merge-log shapes (90,384 + 206,186 + 205,736 = 502,306); file "
                "sizes and retry counts flagged as hardcoded/unverifiable"))
print("DONE", flush=True)
